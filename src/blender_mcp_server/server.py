"""Blender MCP Server — External MCP server that bridges Claude Desktop to Blender."""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import Context, FastMCP

from blender_mcp_server.headless import HeadlessBlenderExecutor, HeadlessJobManager
from blender_mcp_server.providers import (
    BlenderBridgeProvider,
    CapabilityRouter,
    ProviderRegistry,
    ProviderRequest,
)

logger = logging.getLogger(__name__)

BLENDER_HOST = "127.0.0.1"
BLENDER_PORT = 9876
HEADLESS_JOB_MANAGER = HeadlessJobManager()


class BlenderConnection:
    """Async TCP client that communicates with the Blender add-on."""

    def __init__(self, host: str = BLENDER_HOST, port: int = BLENDER_PORT):
        self.host = host
        self.port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
        logger.info(f"Connected to Blender at {self.host}:{self.port}")

    async def disconnect(self):
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
            self._reader = None

    async def send_command(self, command: str, params: dict | None = None) -> Any:
        """Send a command to Blender and return the result."""
        if not self._writer:
            await self.connect()

        assert self._reader is not None
        assert self._writer is not None

        request = {
            "id": str(uuid.uuid4()),
            "command": command,
            "params": params or {},
        }

        async with self._lock:
            try:
                self._writer.write(json.dumps(request).encode() + b"\n")
                await self._writer.drain()

                line = await self._reader.readline()
                if not line:
                    raise ConnectionError("Blender connection closed")

                response = json.loads(line)
                if not response.get("success"):
                    raise RuntimeError(response.get("error", "Unknown error from Blender"))
                return response.get("result")
            except (ConnectionError, OSError) as e:
                # Connection lost — reset and re-raise
                self._writer = None
                self._reader = None
                raise ConnectionError(f"Lost connection to Blender: {e}") from e


@asynccontextmanager
async def blender_lifespan(server: FastMCP):
    """Manage the Blender connection lifecycle."""
    conn = BlenderConnection()
    try:
        await conn.connect()
    except OSError:
        logger.warning("Could not connect to Blender on startup. Will retry on first tool call.")
    yield conn
    await conn.disconnect()


mcp = FastMCP(
    "Blender MCP Server",
    lifespan=blender_lifespan,
    log_level="INFO",
)


def _get_conn(ctx: Context) -> BlenderConnection:
    return ctx.request_context.lifespan_context  # type: ignore[no-any-return]


def _get_router(ctx: Context) -> CapabilityRouter:
    registry = ProviderRegistry(
        [BlenderBridgeProvider(_get_conn(ctx))]
    )
    return CapabilityRouter(
        registry,
        preferred_provider_ids=("blender-bridge",),
    )


# -- Scene tools --


@mcp.tool(
    name="blender_scene_get_info",
    description="Get information about the current Blender scene including name, frame range, render engine, resolution, and object count.",
)
async def scene_get_info(ctx: Context) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="scene.get_info",
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(result.error or "scene.get_info failed")

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_scene_list_objects",
    description="List all objects in the current Blender scene. Optionally filter by type (MESH, CAMERA, LIGHT, EMPTY, CURVE, etc.).",
)
async def scene_list_objects(ctx: Context, type: str | None = None) -> str:
    parameters: dict[str, Any] = {}
    if type:
        parameters["type"] = type

    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="scene.list_objects",
        parameters=parameters,
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(result.error or "scene.list_objects failed")

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_object_get_transform",
    description="Get the position, rotation, and scale of a Blender object by name.",
)
async def object_get_transform(ctx: Context, name: str) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="object.get_transform",
        parameters={"name": name},
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(result.error or "object.get_transform failed")

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_object_get_hierarchy",
    description="Get the parent/child hierarchy of objects. If name is provided, returns the subtree for that object. Otherwise returns the full scene hierarchy.",
)
async def object_get_hierarchy(ctx: Context, name: str | None = None) -> str:
    parameters: dict[str, Any] = {}
    if name:
        parameters["name"] = name

    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="object.get_hierarchy",
        parameters=parameters,
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(result.error or "object.get_hierarchy failed")

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_material_list",
    description="List all materials in the Blender file.",
)
async def material_list(ctx: Context) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="material.list",
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "material.list failed"
        )

    return json.dumps(result.result, indent=2)


# -- Object mutation tools --


@mcp.tool(
    name="blender_object_create",
    description="Create a new mesh object in Blender. Supported types: cube, sphere, cylinder, plane, cone, torus.",
)
async def object_create(
    ctx: Context,
    mesh_type: str = "cube",
    name: str | None = None,
    location: list[float] | None = None,
    size: float = 2.0,
) -> str:
    parameters: dict[str, Any] = {
        "type": mesh_type,
        "size": size,
    }
    if name:
        parameters["name"] = name
    if location:
        parameters["location"] = location

    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="object.create_mesh",
        parameters=parameters,
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "object.create_mesh failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_object_delete",
    description="Delete an object from the Blender scene by name.",
)
async def object_delete(ctx: Context, name: str) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="object.delete",
        parameters={"name": name},
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "object.delete failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_object_translate",
    description="Move an object. Provide either 'location' for absolute positioning or 'offset' for relative movement.",
)
async def object_translate(
    ctx: Context,
    name: str,
    location: list[float] | None = None,
    offset: list[float] | None = None,
) -> str:
    parameters: dict[str, Any] = {"name": name}
    if location:
        parameters["location"] = location
    if offset:
        parameters["offset"] = offset

    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="object.translate",
        parameters=parameters,
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "object.translate failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_object_rotate",
    description="Set the rotation of an object. Provide rotation as [x, y, z] angles. By default angles are in degrees.",
)
async def object_rotate(
    ctx: Context,
    name: str,
    rotation: list[float],
    degrees: bool = True,
) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="object.rotate",
        parameters={
            "name": name,
            "rotation": rotation,
            "degrees": degrees,
        },
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "object.rotate failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_object_scale",
    description="Set the scale of an object. Provide scale as [x, y, z].",
)
async def object_scale(ctx: Context, name: str, scale: list[float]) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="object.scale",
        parameters={
            "name": name,
            "scale": scale,
        },
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "object.scale failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_object_duplicate",
    description="Duplicate an object in the Blender scene. Optionally provide a new name.",
)
async def object_duplicate(
    ctx: Context,
    name: str,
    new_name: str | None = None,
) -> str:
    parameters: dict[str, Any] = {"name": name}
    if new_name:
        parameters["new_name"] = new_name

    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="object.duplicate",
        parameters=parameters,
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "object.duplicate failed"
        )

    return json.dumps(result.result, indent=2)


# -- Geometry editing tools --


@mcp.tool(
    name="blender_mesh_extrude",
    description=(
        "Extrude one or more faces of a mesh object by an explicit "
        "3D offset vector."
    ),
)
async def mesh_extrude(
    ctx: Context,
    name: str,
    face_indices: list[int],
    offset: list[float],
) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="mesh.extrude",
        parameters={
            "name": name,
            "face_indices": face_indices,
            "offset": offset,
        },
    )

    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "mesh.extrude failed"
        )

    return json.dumps(result.result, indent=2)



# -- Material tools --


@mcp.tool(
    name="blender_material_create",
    description="Create a new material. Optionally set an initial base color as [r, g, b] with values 0-1.",
)
async def material_create(
    ctx: Context,
    name: str = "Material",
    color: list[float] | None = None,
) -> str:
    parameters: dict[str, Any] = {"name": name}
    if color:
        parameters["color"] = color

    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="material.create",
        parameters=parameters,
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "material.create failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_material_assign",
    description="Assign an existing material to an object.",
)
async def material_assign(
    ctx: Context,
    object: str,
    material: str,
) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="material.assign",
        parameters={
            "object": object,
            "material": material,
        },
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "material.assign failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_material_set_color",
    description="Set the base color of a material. Color is [r, g, b] with values 0-1.",
)
async def material_set_color(
    ctx: Context,
    name: str,
    color: list[float],
) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="material.set_color",
        parameters={
            "name": name,
            "color": color,
        },
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "material.set_color failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_material_set_texture",
    description="Set an image texture as the base color of a material. Provide the file path to the image.",
)
async def material_set_texture(
    ctx: Context,
    name: str,
    filepath: str,
) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="material.set_texture",
        parameters={
            "name": name,
            "filepath": filepath,
        },
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "material.set_texture failed"
        )

    return json.dumps(result.result, indent=2)


# -- Render tools --


@mcp.tool(
    name="blender_render_still",
    description=(
        "Render the current scene as a still image. Optionally set output path, resolution, and render engine "
        "(BLENDER_EEVEE, CYCLES, etc.). Use transport='bridge' for the live Blender add-on session, or "
        "transport='headless' with blend_file='/path/to/file.blend' to render in a separate background Blender process."
    ),
)
async def render_still(
    ctx: Context,
    output_path: str = "//render.png",
    resolution_x: int | None = None,
    resolution_y: int | None = None,
    engine: str | None = None,
    transport: str = "bridge",
    blend_file: str | None = None,
    factory_startup: bool | None = None,
) -> str:
    if transport == "headless":
        code = """
import bpy
scene = bpy.context.scene
scene.render.filepath = args["output_path"]
if args.get("resolution_x") is not None:
    scene.render.resolution_x = args["resolution_x"]
if args.get("resolution_y") is not None:
    scene.render.resolution_y = args["resolution_y"]
if args.get("engine"):
    scene.render.engine = args["engine"]
bpy.ops.render.render(write_still=True)
__result__ = {
    "output_path": scene.render.filepath,
    "engine": scene.render.engine,
    "resolution_x": scene.render.resolution_x,
    "resolution_y": scene.render.resolution_y,
}
"""
        executor = HeadlessBlenderExecutor()
        result = await executor.execute(
            code=code,
            args={
                "output_path": output_path,
                "resolution_x": resolution_x,
                "resolution_y": resolution_y,
                "engine": engine,
            },
            blend_file=blend_file,
            factory_startup=factory_startup,
        )
    else:
        parameters: dict[str, Any] = {
            "output_path": output_path,
        }
        if resolution_x is not None:
            parameters["resolution_x"] = resolution_x
        if resolution_y is not None:
            parameters["resolution_y"] = resolution_y
        if engine:
            parameters["engine"] = engine

        request = ProviderRequest(
            request_id=str(uuid.uuid4()),
            capability_id="render.still",
            parameters=parameters,
        )
        routed_result = await _get_router(ctx).execute(request)

        if not routed_result.success:
            raise RuntimeError(
                routed_result.error or "render.still failed"
            )

        result = routed_result.result

    return json.dumps(result, indent=2)


@mcp.tool(
    name="blender_render_animation",
    description=(
        "Render an animation. Optionally set output path, frame range, and render engine. "
        "Use transport='bridge' for the live Blender add-on session, or transport='headless' with a blend_file "
        "to render in a separate background Blender process."
    ),
)
async def render_animation(
    ctx: Context,
    output_path: str = "//render_",
    frame_start: int | None = None,
    frame_end: int | None = None,
    engine: str | None = None,
    transport: str = "bridge",
    blend_file: str | None = None,
    factory_startup: bool | None = None,
) -> str:
    if transport == "headless":
        code = """
import bpy
scene = bpy.context.scene
scene.render.filepath = args["output_path"]
if args.get("frame_start") is not None:
    scene.frame_start = args["frame_start"]
if args.get("frame_end") is not None:
    scene.frame_end = args["frame_end"]
if args.get("engine"):
    scene.render.engine = args["engine"]
bpy.ops.render.render(animation=True)
__result__ = {
    "output_path": scene.render.filepath,
    "engine": scene.render.engine,
    "frame_start": scene.frame_start,
    "frame_end": scene.frame_end,
}
"""
        executor = HeadlessBlenderExecutor()
        result = await executor.execute(
            code=code,
            args={
                "output_path": output_path,
                "frame_start": frame_start,
                "frame_end": frame_end,
                "engine": engine,
            },
            blend_file=blend_file,
            factory_startup=factory_startup,
        )
    else:
        parameters: dict[str, Any] = {
            "output_path": output_path,
        }
        if frame_start is not None:
            parameters["frame_start"] = frame_start
        if frame_end is not None:
            parameters["frame_end"] = frame_end
        if engine:
            parameters["engine"] = engine

        request = ProviderRequest(
            request_id=str(uuid.uuid4()),
            capability_id="render.animation",
            parameters=parameters,
        )
        routed_result = await _get_router(ctx).execute(request)

        if not routed_result.success:
            raise RuntimeError(
                routed_result.error or "render.animation failed"
            )

        result = routed_result.result

    return json.dumps(result, indent=2)


# -- Export tools --


@mcp.tool(
    name="blender_export_gltf",
    description="Export the scene as glTF/GLB. Provide the output file path.",
)
async def export_gltf(ctx: Context, filepath: str) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="export.gltf",
        parameters={"filepath": filepath},
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "export.gltf failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_export_obj",
    description="Export the scene as OBJ. Provide the output file path.",
)
async def export_obj(ctx: Context, filepath: str) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="export.obj",
        parameters={"filepath": filepath},
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "export.obj failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_export_fbx",
    description="Export the scene as FBX. Provide the output file path.",
)
async def export_fbx(ctx: Context, filepath: str) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="export.fbx",
        parameters={"filepath": filepath},
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "export.fbx failed"
        )

    return json.dumps(result.result, indent=2)


# -- History tools --


@mcp.tool(
    name="blender_history_undo",
    description="Undo the last operation in Blender.",
)
async def history_undo(ctx: Context) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="history.undo",
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "history.undo failed"
        )

    return json.dumps(result.result, indent=2)


@mcp.tool(
    name="blender_history_redo",
    description="Redo the last undone operation in Blender.",
)
async def history_redo(ctx: Context) -> str:
    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="history.redo",
    )
    result = await _get_router(ctx).execute(request)

    if not result.success:
        raise RuntimeError(
            result.error or "history.redo failed"
        )

    return json.dumps(result.result, indent=2)


# -- Python execution tools --


@mcp.tool(
    name="blender_python_exec",
    description=(
        "Execute a Python script in Blender's context synchronously. "
        "Provide either 'code' (inline Python string) or 'script_path' (path to a .py file), not both. "
        "The script has access to 'bpy', 'mathutils', and an 'args' dict with your supplied arguments. "
        "Set '__result__' in the script to return a JSON-serializable value. "
        "Returns the result, captured stdout/stderr, and execution duration. "
        "Use transport='bridge' for the live Blender add-on session, or transport='headless' to run the script "
        "in a separate `blender -b` process. For long-running tasks like baking, use blender_python_exec_async."
    ),
)
async def python_exec(
    ctx: Context,
    code: str | None = None,
    script_path: str | None = None,
    args: dict | None = None,
    timeout_seconds: int | None = None,
    transport: str = "bridge",
    blend_file: str | None = None,
    factory_startup: bool | None = None,
) -> str:
    if transport == "headless":
        executor = HeadlessBlenderExecutor()
        result = await executor.execute(
            code=code,
            script_path=script_path,
            args=args,
            timeout_seconds=timeout_seconds,
            blend_file=blend_file,
            factory_startup=factory_startup,
        )
    else:
        parameters: dict[str, Any] = {}
        if code is not None:
            parameters["code"] = code
        if script_path is not None:
            parameters["script_path"] = script_path
        if args is not None:
            parameters["args"] = args
        if timeout_seconds is not None:
            parameters["timeout_seconds"] = timeout_seconds

        request = ProviderRequest(
            request_id=str(uuid.uuid4()),
            capability_id="python.execute",
            parameters=parameters,
        )
        routed_result = await _get_router(ctx).execute(request)

        if not routed_result.success:
            raise RuntimeError(
                routed_result.error or "python.execute failed"
            )

        result = routed_result.result

    return json.dumps(result, indent=2)


@mcp.tool(
    name="blender_python_exec_async",
    description=(
        "Start a long-running Python script in Blender asynchronously. "
        "Same parameters as blender_python_exec. Returns a job_id immediately. "
        "Use blender_job_status to poll for completion, and blender_job_cancel to abort. "
        "The script can check '__cancel_event__.is_set()' to detect cancellation. "
        "Ideal for fluid baking, rigid body simulation, or heavy scene generation. "
        "Use transport='headless' to run the job in a separate background Blender process."
    ),
)
async def python_exec_async(
    ctx: Context,
    code: str | None = None,
    script_path: str | None = None,
    args: dict | None = None,
    timeout_seconds: int | None = None,
    transport: str = "bridge",
    blend_file: str | None = None,
    factory_startup: bool | None = None,
) -> str:
    if transport == "headless":
        executor = HeadlessBlenderExecutor()
        job_id = await HEADLESS_JOB_MANAGER.create_job(
            executor,
            code=code,
            script_path=script_path,
            args=args,
            timeout_seconds=timeout_seconds,
            blend_file=blend_file,
            factory_startup=factory_startup,
        )
        result = {"job_id": job_id}
    else:
        parameters: dict[str, Any] = {}
        if code is not None:
            parameters["code"] = code
        if script_path is not None:
            parameters["script_path"] = script_path
        if args is not None:
            parameters["args"] = args
        if timeout_seconds is not None:
            parameters["timeout_seconds"] = timeout_seconds

        request = ProviderRequest(
            request_id=str(uuid.uuid4()),
            capability_id="python.execute_async",
            parameters=parameters,
        )
        routed_result = await _get_router(ctx).execute(request)

        if not routed_result.success:
            raise RuntimeError(
                routed_result.error or "python.execute_async failed"
            )

        result = routed_result.result

    return json.dumps(result, indent=2)


@mcp.tool(
    name="blender_job_status",
    description=(
        "Get the status of an async Blender job. Returns job_id, status "
        "(queued/running/succeeded/failed/cancelled), timestamps, result, stdout, stderr, and error. "
        "Poll this after starting a job with blender_python_exec_async."
    ),
)
async def job_status(ctx: Context, job_id: str) -> str:
    if job_id.startswith("headless-job-"):
        result = HEADLESS_JOB_MANAGER.get_status(job_id)
    else:
        request = ProviderRequest(
            request_id=str(uuid.uuid4()),
            capability_id="job.status",
            parameters={"job_id": job_id},
        )
        routed_result = await _get_router(ctx).execute(request)

        if not routed_result.success:
            raise RuntimeError(
                routed_result.error or "job.status failed"
            )

        result = routed_result.result

    return json.dumps(result, indent=2)


@mcp.tool(
    name="blender_job_cancel",
    description=(
        "Cancel a running or queued async Blender job. "
        "The job's __cancel_event__ is set; scripts that check it will stop gracefully."
    ),
)
async def job_cancel(ctx: Context, job_id: str) -> str:
    if job_id.startswith("headless-job-"):
        result = await HEADLESS_JOB_MANAGER.cancel(job_id)
    else:
        request = ProviderRequest(
            request_id=str(uuid.uuid4()),
            capability_id="job.cancel",
            parameters={"job_id": job_id},
        )
        routed_result = await _get_router(ctx).execute(request)

        if not routed_result.success:
            raise RuntimeError(
                routed_result.error or "job.cancel failed"
            )

        result = routed_result.result

    return json.dumps(result, indent=2)


@mcp.tool(
    name="blender_job_list",
    description="List known async Blender jobs with their IDs, statuses, and creation timestamps.",
)
async def job_list(ctx: Context) -> str:
    headless_jobs = HEADLESS_JOB_MANAGER.list_jobs()["jobs"]

    request = ProviderRequest(
        request_id=str(uuid.uuid4()),
        capability_id="job.list",
    )

    routed_result = await _get_router(ctx).execute(request)

    if routed_result.success:
        bridge_result = routed_result.result or {}
        bridge_jobs = bridge_result.get("jobs", [])
    else:
        bridge_jobs = []

    result = {
        "jobs": bridge_jobs + headless_jobs,
    }

    return json.dumps(result, indent=2)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

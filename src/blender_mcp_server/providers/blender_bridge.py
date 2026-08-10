from __future__ import annotations

from time import perf_counter
from typing import Any, Protocol

from blender_mcp_server.providers.base import (
    ProviderInfo,
    ProviderRequest,
    ProviderResult,
)

BLENDER_BRIDGE_CAPABILITIES = (
    "export.fbx",
    "export.gltf",
    "export.obj",
    "history.redo",
    "history.undo",
    "job.cancel",
    "job.list",
    "job.status",
    "material.assign",
    "material.create",
    "material.list",
    "material.set_color",
    "material.set_texture",
    "mesh.bevel",
    "mesh.extrude",
    "mesh.inset",
    "object.create_mesh",
    "object.delete",
    "object.duplicate",
    "object.get_hierarchy",
    "object.get_transform",
    "object.rotate",
    "object.scale",
    "object.translate",
    "python.execute",
    "python.execute_async",
    "render.animation",
    "render.still",
    "scene.get_info",
    "scene.list_objects",
)


class BlenderCommandConnection(Protocol):
    """Connection interface required by the Blender bridge provider."""

    async def send_command(
        self,
        command: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Send one command to the Blender add-on."""


class BlenderBridgeProvider:
    """Execute registered capabilities through the live Blender TCP bridge."""

    def __init__(
        self,
        connection: BlenderCommandConnection,
        *,
        version: str = "1.0.0",
    ) -> None:
        self._connection = connection
        self._version = version

    def get_info(self) -> ProviderInfo:
        connected = getattr(self._connection, "_writer", None) is not None

        return ProviderInfo(
            id="blender-bridge",
            name="Blender Bridge",
            version=self._version,
            description=(
                "Execute Blender capabilities through the live local "
                "Blender add-on TCP bridge."
            ),
            capabilities=BLENDER_BRIDGE_CAPABILITIES,
            available=True,
            metadata={
                "transport": "tcp",
                "connected": connected,
                "auto_reconnect": True,
            },
        )

    def supports(self, capability_id: str) -> bool:
        return capability_id in BLENDER_BRIDGE_CAPABILITIES

    async def execute(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:
        started_at = perf_counter()

        if not self.supports(request.capability_id):
            return ProviderResult(
                request_id=request.request_id,
                provider_id="blender-bridge",
                capability_id=request.capability_id,
                success=False,
                error=(
                    "Blender Bridge does not support capability "
                    f"'{request.capability_id}'."
                ),
                duration_seconds=perf_counter() - started_at,
            )

        try:
            result = await self._connection.send_command(
                request.capability_id,
                request.parameters,
            )
        except Exception as exc:
            return ProviderResult(
                request_id=request.request_id,
                provider_id="blender-bridge",
                capability_id=request.capability_id,
                success=False,
                error=str(exc) or exc.__class__.__name__,
                duration_seconds=perf_counter() - started_at,
                metadata={
                    "exception_type": exc.__class__.__name__,
                },
            )

        return ProviderResult(
            request_id=request.request_id,
            provider_id="blender-bridge",
            capability_id=request.capability_id,
            success=True,
            result=result,
            duration_seconds=perf_counter() - started_at,
        )

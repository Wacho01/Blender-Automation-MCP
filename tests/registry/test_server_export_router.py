from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    export_fbx,
    export_gltf,
    export_obj,
)

ExportFunction = Callable[..., Awaitable[str]]


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_export_gltf_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="export.gltf",
            success=True,
            result={
                "filepath": "C:/exports/scene.glb",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await export_gltf(
            ctx,
            filepath="C:/exports/scene.glb",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "export.gltf"
    assert request.parameters == {
        "filepath": "C:/exports/scene.glb",
    }
    assert json.loads(result) == {
        "filepath": "C:/exports/scene.glb",
    }


@pytest.mark.asyncio
async def test_export_obj_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="export.obj",
            success=True,
            result={
                "filepath": "C:/exports/scene.obj",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await export_obj(
            ctx,
            filepath="C:/exports/scene.obj",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "export.obj"
    assert request.parameters == {
        "filepath": "C:/exports/scene.obj",
    }
    assert json.loads(result) == {
        "filepath": "C:/exports/scene.obj",
    }


@pytest.mark.asyncio
async def test_export_fbx_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-3",
            provider_id="blender-bridge",
            capability_id="export.fbx",
            success=True,
            result={
                "filepath": "C:/exports/scene.fbx",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await export_fbx(
            ctx,
            filepath="C:/exports/scene.fbx",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "export.fbx"
    assert request.parameters == {
        "filepath": "C:/exports/scene.fbx",
    }
    assert json.loads(result) == {
        "filepath": "C:/exports/scene.fbx",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function", "capability_id", "filepath"),
    [
        (
            export_gltf,
            "export.gltf",
            "scene.glb",
        ),
        (
            export_obj,
            "export.obj",
            "scene.obj",
        ),
        (
            export_fbx,
            "export.fbx",
            "scene.fbx",
        ),
    ],
)
async def test_export_tools_raise_for_provider_failure(
    function: ExportFunction,
    capability_id: str,
    filepath: str,
) -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-failure",
            provider_id="blender-bridge",
            capability_id=capability_id,
            success=False,
            error=f"{capability_id} failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match=rf"{capability_id} failed",
        ),
    ):
        await function(
            ctx,
            filepath=filepath,
        )

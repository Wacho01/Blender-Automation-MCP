from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    scene_get_info,
    scene_list_objects,
)


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_scene_get_info_routes_through_capability_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="scene.get_info",
            success=True,
            result={"name": "Scene"},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await scene_get_info(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "scene.get_info"
    assert request.parameters == {}
    assert json.loads(result) == {"name": "Scene"}


@pytest.mark.asyncio
async def test_scene_get_info_raises_for_provider_failure() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="scene.get_info",
            success=False,
            error="Bridge unavailable",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(RuntimeError, match="Bridge unavailable"),
    ):
        await scene_get_info(ctx)


@pytest.mark.asyncio
async def test_scene_list_objects_routes_without_filter() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="scene.list_objects",
            success=True,
            result={"objects": []},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await scene_list_objects(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "scene.list_objects"
    assert request.parameters == {}
    assert json.loads(result) == {"objects": []}


@pytest.mark.asyncio
async def test_scene_list_objects_routes_type_filter() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-3",
            provider_id="blender-bridge",
            capability_id="scene.list_objects",
            success=True,
            result={
                "objects": [
                    {
                        "name": "Cube",
                        "type": "MESH",
                    }
                ]
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await scene_list_objects(
            ctx,
            type="MESH",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "scene.list_objects"
    assert request.parameters == {"type": "MESH"}
    assert json.loads(result) == {
        "objects": [
            {
                "name": "Cube",
                "type": "MESH",
            }
        ]
    }


@pytest.mark.asyncio
async def test_scene_list_objects_raises_for_provider_failure() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-4",
            provider_id="blender-bridge",
            capability_id="scene.list_objects",
            success=False,
            error="List failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(RuntimeError, match="List failed"),
    ):
        await scene_list_objects(ctx)

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    object_get_hierarchy,
    object_get_transform,
)


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_object_get_transform_routes_through_capability_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="object.get_transform",
            success=True,
            result={
                "name": "Cube",
                "location": [1.0, 2.0, 3.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0],
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_get_transform(
            ctx,
            name="Cube",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.get_transform"
    assert request.parameters == {"name": "Cube"}
    assert json.loads(result) == {
        "name": "Cube",
        "location": [1.0, 2.0, 3.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    }


@pytest.mark.asyncio
async def test_object_get_transform_raises_for_provider_failure() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="object.get_transform",
            success=False,
            error="Object not found",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(RuntimeError, match="Object not found"),
    ):
        await object_get_transform(
            ctx,
            name="Missing",
        )


@pytest.mark.asyncio
async def test_object_get_hierarchy_routes_without_name() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-3",
            provider_id="blender-bridge",
            capability_id="object.get_hierarchy",
            success=True,
            result={
                "objects": [
                    {
                        "name": "Parent",
                        "children": [
                            {
                                "name": "Child",
                                "children": [],
                            }
                        ],
                    }
                ]
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_get_hierarchy(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.get_hierarchy"
    assert request.parameters == {}
    assert json.loads(result) == {
        "objects": [
            {
                "name": "Parent",
                "children": [
                    {
                        "name": "Child",
                        "children": [],
                    }
                ],
            }
        ]
    }


@pytest.mark.asyncio
async def test_object_get_hierarchy_routes_with_name() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-4",
            provider_id="blender-bridge",
            capability_id="object.get_hierarchy",
            success=True,
            result={
                "name": "Parent",
                "children": [
                    {
                        "name": "Child",
                        "children": [],
                    }
                ],
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_get_hierarchy(
            ctx,
            name="Parent",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.get_hierarchy"
    assert request.parameters == {"name": "Parent"}
    assert json.loads(result) == {
        "name": "Parent",
        "children": [
            {
                "name": "Child",
                "children": [],
            }
        ],
    }


@pytest.mark.asyncio
async def test_object_get_hierarchy_raises_for_provider_failure() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-5",
            provider_id="blender-bridge",
            capability_id="object.get_hierarchy",
            success=False,
            error="Hierarchy failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(RuntimeError, match="Hierarchy failed"),
    ):
        await object_get_hierarchy(ctx)

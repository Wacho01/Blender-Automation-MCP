from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    material_assign,
    material_create,
    material_list,
    material_set_color,
    material_set_texture,
)

MaterialFunction = Callable[..., Awaitable[str]]


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_material_list_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="material.list",
            success=True,
            result={
                "materials": [
                    {
                        "name": "Blue",
                    }
                ]
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await material_list(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "material.list"
    assert request.parameters == {}
    assert json.loads(result) == {
        "materials": [
            {
                "name": "Blue",
            }
        ]
    }


@pytest.mark.asyncio
async def test_material_create_routes_without_color() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="material.create",
            success=True,
            result={"name": "Blue"},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await material_create(
            ctx,
            name="Blue",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "material.create"
    assert request.parameters == {
        "name": "Blue",
    }
    assert json.loads(result) == {
        "name": "Blue",
    }


@pytest.mark.asyncio
async def test_material_create_routes_with_color() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-3",
            provider_id="blender-bridge",
            capability_id="material.create",
            success=True,
            result={"name": "Blue"},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await material_create(
            ctx,
            name="Blue",
            color=[0.0, 0.0, 1.0],
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "material.create"
    assert request.parameters == {
        "name": "Blue",
        "color": [0.0, 0.0, 1.0],
    }
    assert json.loads(result) == {
        "name": "Blue",
    }


@pytest.mark.asyncio
async def test_material_assign_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-4",
            provider_id="blender-bridge",
            capability_id="material.assign",
            success=True,
            result={"assigned": True},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await material_assign(
            ctx,
            object="Cube",
            material="Blue",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "material.assign"
    assert request.parameters == {
        "object": "Cube",
        "material": "Blue",
    }
    assert json.loads(result) == {
        "assigned": True,
    }


@pytest.mark.asyncio
async def test_material_set_color_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-5",
            provider_id="blender-bridge",
            capability_id="material.set_color",
            success=True,
            result={"updated": True},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await material_set_color(
            ctx,
            name="Blue",
            color=[0.0, 0.0, 1.0],
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "material.set_color"
    assert request.parameters == {
        "name": "Blue",
        "color": [0.0, 0.0, 1.0],
    }
    assert json.loads(result) == {
        "updated": True,
    }


@pytest.mark.asyncio
async def test_material_set_texture_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-6",
            provider_id="blender-bridge",
            capability_id="material.set_texture",
            success=True,
            result={"updated": True},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await material_set_texture(
            ctx,
            name="Blue",
            filepath="C:/textures/blue.png",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "material.set_texture"
    assert request.parameters == {
        "name": "Blue",
        "filepath": "C:/textures/blue.png",
    }
    assert json.loads(result) == {
        "updated": True,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function", "capability_id", "kwargs"),
    [
        (
            material_list,
            "material.list",
            {},
        ),
        (
            material_create,
            "material.create",
            {
                "name": "Blue",
            },
        ),
        (
            material_assign,
            "material.assign",
            {
                "object": "Cube",
                "material": "Blue",
            },
        ),
        (
            material_set_color,
            "material.set_color",
            {
                "name": "Blue",
                "color": [1.0, 0.0, 0.0],
            },
        ),
        (
            material_set_texture,
            "material.set_texture",
            {
                "name": "Blue",
                "filepath": "texture.png",
            },
        ),
    ],
)
async def test_material_tools_raise_for_provider_failure(
    function: MaterialFunction,
    capability_id: str,
    kwargs: dict[str, Any],
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
            **kwargs,
        )

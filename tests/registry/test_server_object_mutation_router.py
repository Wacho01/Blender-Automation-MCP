from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    object_create,
    object_delete,
    object_duplicate,
    object_rotate,
    object_scale,
    object_translate,
)


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_object_create_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="object.create_mesh",
            success=True,
            result={"name": "Cube"},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_create(
            ctx,
            mesh_type="cube",
            name="Cube",
            location=[1.0, 2.0, 3.0],
            size=2.0,
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.create_mesh"
    assert request.parameters == {
        "type": "cube",
        "size": 2.0,
        "name": "Cube",
        "location": [1.0, 2.0, 3.0],
    }
    assert json.loads(result) == {"name": "Cube"}


@pytest.mark.asyncio
async def test_object_create_omits_optional_parameters() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="object.create_mesh",
            success=True,
            result={"name": "Cube"},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_create(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.create_mesh"
    assert request.parameters == {
        "type": "cube",
        "size": 2.0,
    }
    assert json.loads(result) == {"name": "Cube"}


@pytest.mark.asyncio
async def test_object_delete_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-3",
            provider_id="blender-bridge",
            capability_id="object.delete",
            success=True,
            result={"deleted": True},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_delete(
            ctx,
            name="Cube",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.delete"
    assert request.parameters == {"name": "Cube"}
    assert json.loads(result) == {"deleted": True}


@pytest.mark.asyncio
async def test_object_translate_routes_absolute_location() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-4",
            provider_id="blender-bridge",
            capability_id="object.translate",
            success=True,
            result={"translated": True},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_translate(
            ctx,
            name="Cube",
            location=[1.0, 2.0, 3.0],
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.translate"
    assert request.parameters == {
        "name": "Cube",
        "location": [1.0, 2.0, 3.0],
    }
    assert json.loads(result) == {"translated": True}


@pytest.mark.asyncio
async def test_object_translate_routes_relative_offset() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-5",
            provider_id="blender-bridge",
            capability_id="object.translate",
            success=True,
            result={"translated": True},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_translate(
            ctx,
            name="Cube",
            offset=[0.5, 0.0, -1.0],
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.translate"
    assert request.parameters == {
        "name": "Cube",
        "offset": [0.5, 0.0, -1.0],
    }
    assert json.loads(result) == {"translated": True}


@pytest.mark.asyncio
async def test_object_rotate_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-6",
            provider_id="blender-bridge",
            capability_id="object.rotate",
            success=True,
            result={"rotated": True},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_rotate(
            ctx,
            name="Cube",
            rotation=[90.0, 0.0, 45.0],
            degrees=True,
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.rotate"
    assert request.parameters == {
        "name": "Cube",
        "rotation": [90.0, 0.0, 45.0],
        "degrees": True,
    }
    assert json.loads(result) == {"rotated": True}


@pytest.mark.asyncio
async def test_object_scale_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-7",
            provider_id="blender-bridge",
            capability_id="object.scale",
            success=True,
            result={"scaled": True},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_scale(
            ctx,
            name="Cube",
            scale=[2.0, 2.0, 2.0],
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.scale"
    assert request.parameters == {
        "name": "Cube",
        "scale": [2.0, 2.0, 2.0],
    }
    assert json.loads(result) == {"scaled": True}


@pytest.mark.asyncio
async def test_object_duplicate_routes_without_new_name() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-8",
            provider_id="blender-bridge",
            capability_id="object.duplicate",
            success=True,
            result={"name": "Cube.001"},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_duplicate(
            ctx,
            name="Cube",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.duplicate"
    assert request.parameters == {"name": "Cube"}
    assert json.loads(result) == {"name": "Cube.001"}


@pytest.mark.asyncio
async def test_object_duplicate_routes_with_new_name() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-9",
            provider_id="blender-bridge",
            capability_id="object.duplicate",
            success=True,
            result={"name": "CubeCopy"},
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await object_duplicate(
            ctx,
            name="Cube",
            new_name="CubeCopy",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "object.duplicate"
    assert request.parameters == {
        "name": "Cube",
        "new_name": "CubeCopy",
    }
    assert json.loads(result) == {"name": "CubeCopy"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function_name", "capability_id", "kwargs"),
    [
        (
            "object_create",
            "object.create_mesh",
            {
                "mesh_type": "cube",
                "name": "Cube",
            },
        ),
        (
            "object_delete",
            "object.delete",
            {
                "name": "Cube",
            },
        ),
        (
            "object_translate",
            "object.translate",
            {
                "name": "Cube",
                "offset": [1.0, 0.0, 0.0],
            },
        ),
        (
            "object_rotate",
            "object.rotate",
            {
                "name": "Cube",
                "rotation": [0.0, 0.0, 90.0],
            },
        ),
        (
            "object_scale",
            "object.scale",
            {
                "name": "Cube",
                "scale": [2.0, 2.0, 2.0],
            },
        ),
        (
            "object_duplicate",
            "object.duplicate",
            {
                "name": "Cube",
            },
        ),
    ],
)
async def test_object_mutation_tools_raise_for_provider_failure(
    function_name: str,
    capability_id: str,
    kwargs: dict[str, object],
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

    functions = {
        "object_create": object_create,
        "object_delete": object_delete,
        "object_translate": object_translate,
        "object_rotate": object_rotate,
        "object_scale": object_scale,
        "object_duplicate": object_duplicate,
    }
    function = functions[function_name]

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
        await function(ctx, **kwargs)

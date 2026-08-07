from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import mesh_extrude


def make_context() -> MagicMock:
    return MagicMock()


@pytest.mark.asyncio
async def test_mesh_extrude_routes_through_router() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="mesh.extrude",
            success=True,
            result={
                "name": "Cube",
                "face_indices": [1],
                "offset": [0.0, 0.0, 2.0],
                "vertex_count": 12,
                "edge_count": 20,
                "face_count": 11,
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await mesh_extrude(
            ctx,
            name="Cube",
            face_indices=[1],
            offset=[0.0, 0.0, 2.0],
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.extrude"

    assert request.parameters == {
        "name": "Cube",
        "face_indices": [1],
        "offset": [0.0, 0.0, 2.0],
    }

    payload = json.loads(result)

    assert payload["name"] == "Cube"
    assert payload["face_indices"] == [1]
    assert payload["offset"] == [0.0, 0.0, 2.0]


@pytest.mark.asyncio
async def test_mesh_extrude_routes_multiple_faces() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="mesh.extrude",
            success=True,
            result={
                "name": "Cube",
                "face_indices": [1, 3],
                "offset": [0.0, 0.0, 1.0],
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_extrude(
            ctx,
            name="Cube",
            face_indices=[1, 3],
            offset=[0.0, 0.0, 1.0],
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.extrude"

    assert request.parameters == {
        "name": "Cube",
        "face_indices": [1, 3],
        "offset": [0.0, 0.0, 1.0],
    }


@pytest.mark.asyncio
async def test_mesh_extrude_preserves_negative_offset() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-3",
            provider_id="blender-bridge",
            capability_id="mesh.extrude",
            success=True,
            result={
                "name": "Cube",
                "face_indices": [0],
                "offset": [0.0, 0.0, -0.5],
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_extrude(
            ctx,
            name="Cube",
            face_indices=[0],
            offset=[0.0, 0.0, -0.5],
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["offset"] == [
        0.0,
        0.0,
        -0.5,
    ]


@pytest.mark.asyncio
async def test_mesh_extrude_raises_for_provider_failure() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-failure",
            provider_id="blender-bridge",
            capability_id="mesh.extrude",
            success=False,
            error="mesh.extrude failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match=r"mesh\.extrude failed",
        ),
    ):
        await mesh_extrude(
            ctx,
            name="Cube",
            face_indices=[1],
            offset=[0.0, 0.0, 2.0],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("name", "face_indices", "offset"),
    [
        (
            "Cube",
            [0],
            [1.0, 0.0, 0.0],
        ),
        (
            "FeatureBody",
            [4, 5, 6],
            [0.0, 12.5, 0.0],
        ),
    ],
)
async def test_mesh_extrude_forwards_parameters_exactly(
    name: str,
    face_indices: list[int],
    offset: list[float],
) -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-parameterized",
            provider_id="blender-bridge",
            capability_id="mesh.extrude",
            success=True,
            result={
                "name": name,
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_extrude(
            ctx,
            name=name,
            face_indices=face_indices,
            offset=offset,
        )

    request = router.execute.await_args.args[0]

    expected: dict[str, Any] = {
        "name": name,
        "face_indices": face_indices,
        "offset": offset,
    }

    assert request.capability_id == "mesh.extrude"
    assert request.parameters == expected

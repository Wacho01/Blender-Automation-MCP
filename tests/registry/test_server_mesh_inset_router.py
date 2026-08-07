from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from blender_mcp_server.providers.base import ProviderResult
from blender_mcp_server.server import mesh_inset


@pytest.mark.asyncio
async def test_mesh_inset_routes_through_router(monkeypatch):
    router = AsyncMock()
    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="blender-bridge",
        capability_id="mesh.inset",
        success=True,
        result={"ok": True},
    )

    monkeypatch.setattr(
        "blender_mcp_server.server._get_router",
        lambda ctx: router,
    )

    result = await mesh_inset(
        ctx=object(),
        name="Cube",
        face_indices=[1],
        thickness=0.1,
        depth=0.0,
    )

    assert json.loads(result) == {"ok": True}

    request = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.inset"
    assert request.parameters == {
        "name": "Cube",
        "face_indices": [1],
        "thickness": 0.1,
        "depth": 0.0,
    }


@pytest.mark.asyncio
async def test_mesh_inset_preserves_multiple_faces(monkeypatch):
    router = AsyncMock()
    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="blender-bridge",
        capability_id="mesh.inset",
        success=True,
        result={},
    )

    monkeypatch.setattr(
        "blender_mcp_server.server._get_router",
        lambda ctx: router,
    )

    await mesh_inset(
        ctx=object(),
        name="Cube",
        face_indices=[0, 2, 5],
        thickness=0.05,
        depth=0.02,
    )

    request = router.execute.await_args.args[0]

    assert request.parameters["face_indices"] == [0, 2, 5]
    assert request.parameters["thickness"] == 0.05
    assert request.parameters["depth"] == 0.02


@pytest.mark.asyncio
async def test_mesh_inset_provider_failure(monkeypatch):
    router = AsyncMock()
    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="blender-bridge",
        capability_id="mesh.inset",
        success=False,
        error="boom",
    )

    monkeypatch.setattr(
        "blender_mcp_server.server._get_router",
        lambda ctx: router,
    )

    with pytest.raises(RuntimeError, match="boom"):
        await mesh_inset(
            ctx=object(),
            name="Cube",
            face_indices=[1],
            thickness=0.1,
            depth=0.0,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("name", "face_indices", "thickness", "depth"),
    [
        ("Cube", [1], 0.10, 0.00),
        ("Feature", [2, 3], 0.05, 0.02),
    ],
)
async def test_mesh_inset_parameter_forwarding(
    monkeypatch,
    name,
    face_indices,
    thickness,
    depth,
):
    router = AsyncMock()
    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="blender-bridge",
        capability_id="mesh.inset",
        success=True,
        result={},
    )

    monkeypatch.setattr(
        "blender_mcp_server.server._get_router",
        lambda ctx: router,
    )

    await mesh_inset(
        ctx=object(),
        name=name,
        face_indices=face_indices,
        thickness=thickness,
        depth=depth,
    )

    request = router.execute.await_args.args[0]

    assert request.parameters == {
        "name": name,
        "face_indices": face_indices,
        "thickness": thickness,
        "depth": depth,
    }

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers.base import (
    ProviderRequest,
    ProviderResult,
)
from blender_mcp_server.server import mesh_dissolve


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("name", "element_type", "indices"),
    [
        ("Cube", "VERTS", [0, 1]),
        ("FeatureBody", "EDGES", [2, 5, 8]),
    ],
)
async def test_mesh_dissolve_routes_through_router(
    name,
    element_type,
    indices,
):
    router = AsyncMock()
    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.dissolve",
        success=True,
        result={"ok": True},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await mesh_dissolve(
            ctx,
            name=name,
            element_type=element_type,
            indices=indices,
        )

    assert '"ok": true' in result

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.dissolve"
    assert request.parameters == {
        "name": name,
        "element_type": element_type,
        "indices": indices,
    }


@pytest.mark.asyncio
async def test_mesh_dissolve_preserves_indices():
    router = AsyncMock()
    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.dissolve",
        success=True,
        result={},
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_dissolve(
            MagicMock(),
            name="MeshObject",
            element_type="VERTS",
            indices=[3, 7, 11],
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["indices"] == [3, 7, 11]
    assert request.parameters["element_type"] == "VERTS"


@pytest.mark.asyncio
async def test_mesh_dissolve_provider_failure():
    router = AsyncMock()
    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.dissolve",
        success=False,
        error="dissolve failed",
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match="dissolve failed",
        ),
    ):
        await mesh_dissolve(
            MagicMock(),
            name="Cube",
            element_type="EDGES",
            indices=[0],
        )

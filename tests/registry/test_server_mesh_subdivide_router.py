from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers.base import (
    ProviderRequest,
    ProviderResult,
)
from blender_mcp_server.server import mesh_subdivide


@pytest.mark.asyncio
async def test_mesh_subdivide_routes_through_router():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.subdivide",
        success=True,
        result={"ok": True},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await mesh_subdivide(
            ctx,
            name="Cube",
            edge_indices=[0, 1, 2, 3],
            cuts=1,
            smooth=0.0,
        )

    assert '"ok": true' in result

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.subdivide"
    assert request.parameters == {
        "name": "Cube",
        "edge_indices": [0, 1, 2, 3],
        "cuts": 1,
        "smooth": 0.0,
    }


@pytest.mark.asyncio
async def test_mesh_subdivide_multiple_cuts():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.subdivide",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_subdivide(
            ctx,
            name="FeatureBody",
            edge_indices=[3, 4, 8],
            cuts=4,
            smooth=0.25,
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["edge_indices"] == [3, 4, 8]
    assert request.parameters["cuts"] == 4
    assert request.parameters["smooth"] == 0.25


@pytest.mark.asyncio
async def test_mesh_subdivide_provider_failure():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.subdivide",
        success=False,
        error="subdivide failed",
    )

    ctx = MagicMock()

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match="subdivide failed",
        ),
    ):
        await mesh_subdivide(
            ctx,
            name="Cube",
            edge_indices=[0],
            cuts=1,
            smooth=0.0,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "name",
        "edge_indices",
        "cuts",
        "smooth",
    ),
    [
        (
            "Cube",
            [0],
            1,
            0.0,
        ),
        (
            "FeatureBody",
            [2, 6, 9],
            3,
            0.5,
        ),
    ],
)
async def test_mesh_subdivide_parameter_forwarding(
    name,
    edge_indices,
    cuts,
    smooth,
):
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.subdivide",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_subdivide(
            ctx,
            name=name,
            edge_indices=edge_indices,
            cuts=cuts,
            smooth=smooth,
        )

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.parameters == {
        "name": name,
        "edge_indices": edge_indices,
        "cuts": cuts,
        "smooth": smooth,
    }

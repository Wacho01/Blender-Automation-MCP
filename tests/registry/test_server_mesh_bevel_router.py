from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers.base import (
    ProviderRequest,
    ProviderResult,
)
from blender_mcp_server.server import mesh_bevel


@pytest.mark.asyncio
async def test_mesh_bevel_routes_through_router():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.bevel",
        success=True,
        result={"ok": True},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await mesh_bevel(
            ctx,
            name="Cube",
            edge_indices=[0],
            width=0.1,
            segments=3,
        )

    assert '"ok": true' in result


@pytest.mark.asyncio
async def test_mesh_bevel_multiple_edges():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.bevel",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_bevel(
            ctx,
            name="Cube",
            edge_indices=[0, 1, 5],
            width=0.25,
            segments=5,
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["edge_indices"] == [0, 1, 5]
    assert request.parameters["width"] == 0.25
    assert request.parameters["segments"] == 5


@pytest.mark.asyncio
async def test_mesh_bevel_provider_failure():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.bevel",
        success=False,
        error="boom",
    )

    ctx = MagicMock()

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(RuntimeError, match="boom"),
    ):
        await mesh_bevel(
            ctx,
            name="Cube",
            edge_indices=[0],
            width=0.1,
            segments=1,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "name",
        "edge_indices",
        "width",
        "segments",
    ),
    [
        (
            "Cube",
            [0],
            0.05,
            1,
        ),
        (
            "FeatureBody",
            [3, 8],
            0.20,
            4,
        ),
    ],
)
async def test_mesh_bevel_parameter_forwarding(
    name,
    edge_indices,
    width,
    segments,
):
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.bevel",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_bevel(
            ctx,
            name=name,
            edge_indices=edge_indices,
            width=width,
            segments=segments,
        )

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.bevel"
    assert request.parameters == {
        "name": name,
        "edge_indices": edge_indices,
        "width": width,
        "segments": segments,
    }

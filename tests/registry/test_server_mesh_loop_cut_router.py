from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers.base import (
    ProviderRequest,
    ProviderResult,
)
from blender_mcp_server.server import mesh_loop_cut


@pytest.mark.asyncio
async def test_mesh_loop_cut_routes_through_router():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.loop_cut",
        success=True,
        result={"ok": True},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await mesh_loop_cut(
            ctx,
            name="Cube",
            edge_index=0,
            cuts=1,
        )

    assert '"ok": true' in result

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.loop_cut"
    assert request.parameters == {
        "name": "Cube",
        "edge_index": 0,
        "cuts": 1,
    }


@pytest.mark.asyncio
async def test_mesh_loop_cut_multiple_cuts():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.loop_cut",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_loop_cut(
            ctx,
            name="FeatureBody",
            edge_index=8,
            cuts=4,
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["edge_index"] == 8
    assert request.parameters["cuts"] == 4


@pytest.mark.asyncio
async def test_mesh_loop_cut_provider_failure():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.loop_cut",
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
        await mesh_loop_cut(
            ctx,
            name="Cube",
            edge_index=0,
            cuts=1,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("name", "edge_index", "cuts"),
    [
        ("Cube", 0, 1),
        ("FeatureBody", 12, 3),
    ],
)
async def test_mesh_loop_cut_parameter_forwarding(
    name,
    edge_index,
    cuts,
):
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.loop_cut",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_loop_cut(
            ctx,
            name=name,
            edge_index=edge_index,
            cuts=cuts,
        )

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.parameters == {
        "name": name,
        "edge_index": edge_index,
        "cuts": cuts,
    }

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers.base import (
    ProviderRequest,
    ProviderResult,
)
from blender_mcp_server.server import mesh_merge


@pytest.mark.asyncio
async def test_mesh_merge_routes_through_router():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.merge",
        success=True,
        result={"ok": True},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await mesh_merge(
            ctx,
            name="Cube",
            vertex_indices=[0, 1],
            merge_type="CENTER",
        )

    assert '"ok": true' in result

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.merge"
    assert request.parameters == {
        "name": "Cube",
        "vertex_indices": [0, 1],
        "merge_type": "CENTER",
    }


@pytest.mark.asyncio
async def test_mesh_merge_preserves_first_mode():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.merge",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_merge(
            ctx,
            name="FeatureBody",
            vertex_indices=[2, 5, 8],
            merge_type="FIRST",
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["vertex_indices"] == [2, 5, 8]
    assert request.parameters["merge_type"] == "FIRST"


@pytest.mark.asyncio
async def test_mesh_merge_preserves_last_mode():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.merge",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_merge(
            ctx,
            name="FeatureBody",
            vertex_indices=[3, 7],
            merge_type="LAST",
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["merge_type"] == "LAST"


@pytest.mark.asyncio
async def test_mesh_merge_provider_failure():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.merge",
        success=False,
        error="merge failed",
    )

    ctx = MagicMock()

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match="merge failed",
        ),
    ):
        await mesh_merge(
            ctx,
            name="Cube",
            vertex_indices=[0, 1],
            merge_type="CENTER",
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "name",
        "vertex_indices",
        "merge_type",
    ),
    [
        (
            "Cube",
            [0, 1],
            "CENTER",
        ),
        (
            "FeatureBody",
            [4, 6, 9],
            "FIRST",
        ),
    ],
)
async def test_mesh_merge_parameter_forwarding(
    name,
    vertex_indices,
    merge_type,
):
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.merge",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_merge(
            ctx,
            name=name,
            vertex_indices=vertex_indices,
            merge_type=merge_type,
        )

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.parameters == {
        "name": name,
        "vertex_indices": vertex_indices,
        "merge_type": merge_type,
    }

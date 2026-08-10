from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers.base import (
    ProviderRequest,
    ProviderResult,
)
from blender_mcp_server.server import mesh_boolean


@pytest.mark.asyncio
async def test_mesh_boolean_routes_through_router():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.boolean",
        success=True,
        result={"ok": True},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await mesh_boolean(
            ctx,
            target_name="Target",
            cutter_name="Cutter",
            operation="DIFFERENCE",
            delete_cutter=True,
        )

    assert '"ok": true' in result

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.capability_id == "mesh.boolean"
    assert request.parameters == {
        "target_name": "Target",
        "cutter_name": "Cutter",
        "operation": "DIFFERENCE",
        "delete_cutter": True,
    }


@pytest.mark.asyncio
async def test_mesh_boolean_preserves_union_operation():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.boolean",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_boolean(
            ctx,
            target_name="BodyA",
            cutter_name="BodyB",
            operation="UNION",
            delete_cutter=False,
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["operation"] == "UNION"
    assert request.parameters["delete_cutter"] is False


@pytest.mark.asyncio
async def test_mesh_boolean_preserves_intersect_operation():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.boolean",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_boolean(
            ctx,
            target_name="BodyA",
            cutter_name="BodyB",
            operation="INTERSECT",
            delete_cutter=True,
        )

    request = router.execute.await_args.args[0]

    assert request.parameters["operation"] == "INTERSECT"


@pytest.mark.asyncio
async def test_mesh_boolean_provider_failure():
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.boolean",
        success=False,
        error="boolean failed",
    )

    ctx = MagicMock()

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match="boolean failed",
        ),
    ):
        await mesh_boolean(
            ctx,
            target_name="Target",
            cutter_name="Cutter",
            operation="DIFFERENCE",
            delete_cutter=True,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "target_name",
        "cutter_name",
        "operation",
        "delete_cutter",
    ),
    [
        (
            "Target",
            "Cutter",
            "DIFFERENCE",
            True,
        ),
        (
            "BodyA",
            "BodyB",
            "UNION",
            False,
        ),
    ],
)
async def test_mesh_boolean_parameter_forwarding(
    target_name,
    cutter_name,
    operation,
    delete_cutter,
):
    router = AsyncMock()

    router.execute.return_value = ProviderResult(
        request_id="1",
        provider_id="mock",
        capability_id="mesh.boolean",
        success=True,
        result={},
    )

    ctx = MagicMock()

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        await mesh_boolean(
            ctx,
            target_name=target_name,
            cutter_name=cutter_name,
            operation=operation,
            delete_cutter=delete_cutter,
        )

    request: ProviderRequest = router.execute.await_args.args[0]

    assert request.parameters == {
        "target_name": target_name,
        "cutter_name": cutter_name,
        "operation": operation,
        "delete_cutter": delete_cutter,
    }

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    job_cancel,
    job_list,
    job_status,
)


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_job_status_bridge_routes_through_router() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="job.status",
            success=True,
            result={
                "job_id": "bridge-job-1",
                "status": "running",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await job_status(
            ctx,
            job_id="bridge-job-1",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "job.status"
    assert request.parameters == {
        "job_id": "bridge-job-1",
    }
    assert json.loads(result) == {
        "job_id": "bridge-job-1",
        "status": "running",
    }


@pytest.mark.asyncio
async def test_job_cancel_bridge_routes_through_router() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="job.cancel",
            success=True,
            result={
                "job_id": "bridge-job-1",
                "status": "cancelled",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await job_cancel(
            ctx,
            job_id="bridge-job-1",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "job.cancel"
    assert request.parameters == {
        "job_id": "bridge-job-1",
    }
    assert json.loads(result) == {
        "job_id": "bridge-job-1",
        "status": "cancelled",
    }


@pytest.mark.asyncio
async def test_job_list_routes_bridge_and_merges_headless_jobs() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-3",
            provider_id="blender-bridge",
            capability_id="job.list",
            success=True,
            result={
                "jobs": [
                    {
                        "job_id": "bridge-job-1",
                        "status": "running",
                    }
                ]
            },
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        patch(
            "blender_mcp_server.server.HEADLESS_JOB_MANAGER.list_jobs",
            return_value={
                "jobs": [
                    {
                        "job_id": "headless-job-1",
                        "status": "succeeded",
                    }
                ]
            },
        ),
    ):
        result = await job_list(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "job.list"
    assert request.parameters == {}

    assert json.loads(result) == {
        "jobs": [
            {
                "job_id": "bridge-job-1",
                "status": "running",
            },
            {
                "job_id": "headless-job-1",
                "status": "succeeded",
            },
        ]
    }


@pytest.mark.asyncio
async def test_job_status_bridge_raises_for_provider_failure() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-4",
            provider_id="blender-bridge",
            capability_id="job.status",
            success=False,
            error="job.status failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match=r"job\.status failed",
        ),
    ):
        await job_status(
            ctx,
            job_id="bridge-job-1",
        )


@pytest.mark.asyncio
async def test_job_cancel_bridge_raises_for_provider_failure() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-5",
            provider_id="blender-bridge",
            capability_id="job.cancel",
            success=False,
            error="job.cancel failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match=r"job\.cancel failed",
        ),
    ):
        await job_cancel(
            ctx,
            job_id="bridge-job-1",
        )


@pytest.mark.asyncio
async def test_job_list_provider_failure_preserves_headless_jobs() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-6",
            provider_id="blender-bridge",
            capability_id="job.list",
            success=False,
            error="job.list failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        patch(
            "blender_mcp_server.server.HEADLESS_JOB_MANAGER.list_jobs",
            return_value={
                "jobs": [
                    {
                        "job_id": "headless-job-1",
                        "status": "running",
                    }
                ]
            },
        ),
    ):
        result = await job_list(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "job.list"
    assert request.parameters == {}

    assert json.loads(result) == {
        "jobs": [
            {
                "job_id": "headless-job-1",
                "status": "running",
            }
        ]
    }

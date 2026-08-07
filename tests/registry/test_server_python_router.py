from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    python_exec,
    python_exec_async,
)


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_python_exec_bridge_routes_through_router() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="python.execute",
            success=True,
            result={
                "result": {
                    "ok": True,
                },
                "stdout": "",
                "stderr": "",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await python_exec(
            ctx,
            code="__result__ = {'ok': True}",
            args={"value": 123},
            timeout_seconds=30,
            transport="bridge",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "python.execute"
    assert request.parameters == {
        "code": "__result__ = {'ok': True}",
        "args": {
            "value": 123,
        },
        "timeout_seconds": 30,
    }

    assert json.loads(result) == {
        "result": {
            "ok": True,
        },
        "stdout": "",
        "stderr": "",
    }


@pytest.mark.asyncio
async def test_python_exec_bridge_omits_none_parameters() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="python.execute",
            success=True,
            result={
                "result": None,
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await python_exec(
            ctx,
            code="pass",
            transport="bridge",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "python.execute"
    assert request.parameters == {
        "code": "pass",
    }

    assert json.loads(result) == {
        "result": None,
    }


@pytest.mark.asyncio
async def test_python_exec_bridge_routes_script_path() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-3",
            provider_id="blender-bridge",
            capability_id="python.execute",
            success=True,
            result={
                "result": {
                    "script": True,
                },
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await python_exec(
            ctx,
            script_path="C:/scripts/test.py",
            transport="bridge",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "python.execute"
    assert request.parameters == {
        "script_path": "C:/scripts/test.py",
    }

    assert json.loads(result) == {
        "result": {
            "script": True,
        },
    }


@pytest.mark.asyncio
async def test_python_exec_bridge_raises_for_provider_failure() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-4",
            provider_id="blender-bridge",
            capability_id="python.execute",
            success=False,
            error="python.execute failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match=r"python\.execute failed",
        ),
    ):
        await python_exec(
            ctx,
            code="pass",
            transport="bridge",
        )


@pytest.mark.asyncio
async def test_python_exec_async_bridge_routes_through_router() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-5",
            provider_id="blender-bridge",
            capability_id="python.execute_async",
            success=True,
            result={
                "job_id": "bridge-job-1",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await python_exec_async(
            ctx,
            code="print('hello')",
            args={
                "example": True,
            },
            timeout_seconds=60,
            transport="bridge",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "python.execute_async"
    assert request.parameters == {
        "code": "print('hello')",
        "args": {
            "example": True,
        },
        "timeout_seconds": 60,
    }

    assert json.loads(result) == {
        "job_id": "bridge-job-1",
    }


@pytest.mark.asyncio
async def test_python_exec_async_bridge_omits_none_parameters() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-6",
            provider_id="blender-bridge",
            capability_id="python.execute_async",
            success=True,
            result={
                "job_id": "bridge-job-2",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await python_exec_async(
            ctx,
            script_path="C:/scripts/long_job.py",
            transport="bridge",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "python.execute_async"
    assert request.parameters == {
        "script_path": "C:/scripts/long_job.py",
    }

    assert json.loads(result) == {
        "job_id": "bridge-job-2",
    }


@pytest.mark.asyncio
async def test_python_exec_async_bridge_raises_for_provider_failure() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-7",
            provider_id="blender-bridge",
            capability_id="python.execute_async",
            success=False,
            error="python.execute_async failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match=r"python\.execute_async failed",
        ),
    ):
        await python_exec_async(
            ctx,
            code="pass",
            transport="bridge",
        )

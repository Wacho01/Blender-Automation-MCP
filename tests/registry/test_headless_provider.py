from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from blender_mcp_server.providers import (
    CapabilityProvider,
    ProviderRequest,
)
from blender_mcp_server.providers.headless import (
    HEADLESS_CAPABILITIES,
    HeadlessProvider,
)


class FakeExecutor:
    def __init__(self) -> None:
        self.blender_binary = "fake-blender"
        self.execute = AsyncMock()


class FakeJobManager:
    def __init__(self) -> None:
        self.create_job = AsyncMock()
        self.get_status = MagicMock()
        self.cancel = AsyncMock()
        self.list_jobs = MagicMock()


def make_provider() -> tuple[
    HeadlessProvider,
    FakeExecutor,
    FakeJobManager,
]:
    executor = FakeExecutor()
    jobs = FakeJobManager()
    provider = HeadlessProvider(
        executor=executor,
        job_manager=jobs,
        version="2.0.0",
    )
    return provider, executor, jobs


def make_request(
    capability_id: str,
    *,
    parameters: dict[str, Any] | None = None,
    timeout_seconds: float | None = None,
) -> ProviderRequest:
    return ProviderRequest(
        request_id="request-1",
        capability_id=capability_id,
        parameters=parameters or {},
        timeout_seconds=timeout_seconds,
    )


def test_headless_provider_satisfies_protocol() -> None:
    provider, _, _ = make_provider()

    assert isinstance(provider, CapabilityProvider)


def test_headless_provider_info() -> None:
    provider, _, _ = make_provider()

    info = provider.get_info()

    assert info.id == "headless"
    assert info.name == "Headless Blender"
    assert info.version == "2.0.0"
    assert info.available is True
    assert info.capabilities == HEADLESS_CAPABILITIES
    assert info.metadata["transport"] == "headless"
    assert info.metadata["blender_binary"] == "fake-blender"
    assert info.metadata["background_process"] is True
    assert "background Blender processes" in info.description


def test_headless_capability_inventory() -> None:
    assert tuple(sorted(HEADLESS_CAPABILITIES)) == HEADLESS_CAPABILITIES
    assert set(HEADLESS_CAPABILITIES) == {
        "job.cancel",
        "job.list",
        "job.status",
        "python.execute",
        "python.execute_async",
    }


def test_headless_provider_supports_expected_capabilities() -> None:
    provider, _, _ = make_provider()

    assert provider.supports("python.execute") is True
    assert provider.supports("job.list") is True
    assert provider.supports("scene.get_info") is False


@pytest.mark.asyncio
async def test_execute_python_delegates_to_executor() -> None:
    provider, executor, _ = make_provider()
    executor.execute.return_value = {
        "result": 123,
        "error": None,
    }

    request = make_request(
        "python.execute",
        parameters={
            "code": "__result__ = 123",
            "args": {"value": 123},
            "blend_file": "scene.blend",
            "factory_startup": False,
        },
        timeout_seconds=30,
    )

    result = await provider.execute(request)

    executor.execute.assert_awaited_once_with(
        code="__result__ = 123",
        script_path=None,
        args={"value": 123},
        timeout_seconds=30,
        blend_file="scene.blend",
        factory_startup=False,
    )
    assert result.success is True
    assert result.request_id == "request-1"
    assert result.provider_id == "headless"
    assert result.result == {
        "result": 123,
        "error": None,
    }


@pytest.mark.asyncio
async def test_execute_python_uses_parameter_timeout() -> None:
    provider, executor, _ = make_provider()
    executor.execute.return_value = {"result": "ok"}

    result = await provider.execute(
        make_request(
            "python.execute",
            parameters={
                "code": "pass",
                "timeout_seconds": 12,
            },
        )
    )

    executor.execute.assert_awaited_once_with(
        code="pass",
        script_path=None,
        args=None,
        timeout_seconds=12,
        blend_file=None,
        factory_startup=None,
    )
    assert result.success is True


@pytest.mark.asyncio
async def test_execute_async_delegates_to_job_manager() -> None:
    provider, executor, jobs = make_provider()
    jobs.create_job.return_value = "headless-job-1234"

    request = make_request(
        "python.execute_async",
        parameters={
            "script_path": "script.py",
            "args": {"quality": "high"},
        },
    )

    result = await provider.execute(request)

    jobs.create_job.assert_awaited_once_with(
        executor,
        code=None,
        script_path="script.py",
        args={"quality": "high"},
        timeout_seconds=None,
        blend_file=None,
        factory_startup=None,
    )
    assert result.success is True
    assert result.result == {
        "job_id": "headless-job-1234"
    }


@pytest.mark.asyncio
async def test_job_status_delegates_to_job_manager() -> None:
    provider, _, jobs = make_provider()
    jobs.get_status.return_value = {
        "job_id": "headless-job-1",
        "status": "running",
    }

    result = await provider.execute(
        make_request(
            "job.status",
            parameters={"job_id": " headless-job-1 "},
        )
    )

    jobs.get_status.assert_called_once_with("headless-job-1")
    assert result.success is True
    assert result.result["status"] == "running"


@pytest.mark.asyncio
async def test_job_cancel_delegates_to_job_manager() -> None:
    provider, _, jobs = make_provider()
    jobs.cancel.return_value = {
        "job_id": "headless-job-1",
        "status": "cancelled",
    }

    result = await provider.execute(
        make_request(
            "job.cancel",
            parameters={"job_id": "headless-job-1"},
        )
    )

    jobs.cancel.assert_awaited_once_with("headless-job-1")
    assert result.success is True
    assert result.result["status"] == "cancelled"


@pytest.mark.asyncio
async def test_job_list_delegates_to_job_manager() -> None:
    provider, _, jobs = make_provider()
    jobs.list_jobs.return_value = {
        "jobs": [
            {
                "job_id": "headless-job-1",
                "status": "queued",
            }
        ]
    }

    result = await provider.execute(
        make_request("job.list")
    )

    jobs.list_jobs.assert_called_once_with()
    assert result.success is True
    assert result.result == {
        "jobs": [
            {
                "job_id": "headless-job-1",
                "status": "queued",
            }
        ]
    }


@pytest.mark.asyncio
async def test_unsupported_capability_returns_failure() -> None:
    provider, executor, jobs = make_provider()

    result = await provider.execute(
        make_request("scene.get_info")
    )

    executor.execute.assert_not_awaited()
    jobs.create_job.assert_not_awaited()
    assert result.success is False
    assert result.error is not None
    assert "does not support capability" in result.error


@pytest.mark.asyncio
async def test_missing_job_id_returns_failure() -> None:
    provider, _, jobs = make_provider()

    result = await provider.execute(
        make_request("job.status")
    )

    jobs.get_status.assert_not_called()
    assert result.success is False
    assert result.error is not None
    assert "job_id" in result.error
    assert result.metadata["exception_type"] == "ValueError"


@pytest.mark.asyncio
async def test_executor_exception_is_normalized() -> None:
    provider, executor, _ = make_provider()
    executor.execute.side_effect = RuntimeError("boom")

    result = await provider.execute(
        make_request(
            "python.execute",
            parameters={"code": "pass"},
        )
    )

    assert result.success is False
    assert result.error == "boom"
    assert result.metadata["exception_type"] == "RuntimeError"


@pytest.mark.asyncio
async def test_exception_without_message_uses_class_name() -> None:
    provider, executor, _ = make_provider()
    executor.execute.side_effect = RuntimeError()

    result = await provider.execute(
        make_request(
            "python.execute",
            parameters={"code": "pass"},
        )
    )

    assert result.success is False
    assert result.error == "RuntimeError"
    assert result.metadata["exception_type"] == "RuntimeError"

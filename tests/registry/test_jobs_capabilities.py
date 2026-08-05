from blender_mcp_server.capabilities.loader import (
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import OperationType, SecurityLevel

JOBS_MODULE = "blender_mcp_server.capabilities.jobs"


def test_jobs_module_loads() -> None:
    module = load_capability_module(JOBS_MODULE)

    assert module.__name__ == JOBS_MODULE


def test_jobs_module_defines_expected_capability_ids() -> None:
    module = load_capability_module(JOBS_MODULE)
    capabilities = get_module_capabilities(module)

    assert [capability.id for capability in capabilities] == [
        "job.status",
        "job.cancel",
        "job.list",
    ]


def test_job_operation_types() -> None:
    registry = load_capabilities([JOBS_MODULE])

    assert registry.get("job.status").operation_type is OperationType.READ
    assert (
        registry.get("job.cancel").operation_type
        is OperationType.ADMINISTRATIVE
    )
    assert registry.get("job.list").operation_type is OperationType.READ


def test_job_security_levels() -> None:
    registry = load_capabilities([JOBS_MODULE])

    assert (
        registry.get("job.status").security_level
        is SecurityLevel.STANDARD
    )
    assert (
        registry.get("job.cancel").security_level
        is SecurityLevel.PRIVILEGED
    )
    assert (
        registry.get("job.list").security_level
        is SecurityLevel.STANDARD
    )


def test_job_capabilities_do_not_support_undo() -> None:
    module = load_capability_module(JOBS_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.undo_supported is False
        for capability in capabilities
    )


def test_job_capabilities_target_blender_36_or_newer() -> None:
    module = load_capability_module(JOBS_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.minimum_blender_version == "3.6"
        for capability in capabilities
    )


def test_job_status_metadata() -> None:
    registry = load_capabilities([JOBS_MODULE])
    capability = registry.get("job.status")

    assert capability.input_schema == "JobIdParams"
    assert capability.result_schema == "JobStatusResult"
    assert "lifecycle state" in capability.description
    assert "stdout" in capability.description
    assert "stderr" in capability.description
    assert "error information" in capability.description


def test_job_cancel_metadata() -> None:
    registry = load_capabilities([JOBS_MODULE])
    capability = registry.get("job.cancel")

    assert capability.input_schema == "JobIdParams"
    assert capability.result_schema == "JobCancelResult"
    assert "queued or running" in capability.description
    assert "cancellation event" in capability.description
    assert "stop gracefully" in capability.description


def test_job_list_metadata() -> None:
    registry = load_capabilities([JOBS_MODULE])
    capability = registry.get("job.list")

    assert capability.input_schema is None
    assert capability.result_schema == "JobListResult"
    assert "live bridge" in capability.description
    assert "headless job manager" in capability.description
    assert "creation timestamps" in capability.description

from blender_mcp_server.capabilities.loader import (
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import OperationType, SecurityLevel

PYTHON_MODULE = "blender_mcp_server.capabilities.python"


def test_python_module_loads() -> None:
    module = load_capability_module(PYTHON_MODULE)

    assert module.__name__ == PYTHON_MODULE


def test_python_module_defines_expected_capability_ids() -> None:
    module = load_capability_module(PYTHON_MODULE)
    capabilities = get_module_capabilities(module)

    assert [capability.id for capability in capabilities] == [
        "python.execute",
        "python.execute_async",
    ]


def test_python_capabilities_are_execution_operations() -> None:
    module = load_capability_module(PYTHON_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.operation_type is OperationType.EXECUTION
        for capability in capabilities
    )


def test_python_capabilities_use_restricted_security() -> None:
    module = load_capability_module(PYTHON_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.security_level is SecurityLevel.RESTRICTED
        for capability in capabilities
    )


def test_python_capabilities_do_not_support_undo() -> None:
    module = load_capability_module(PYTHON_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.undo_supported is False
        for capability in capabilities
    )


def test_python_capabilities_target_blender_36_or_newer() -> None:
    module = load_capability_module(PYTHON_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.minimum_blender_version == "3.6"
        for capability in capabilities
    )


def test_python_execute_metadata() -> None:
    registry = load_capabilities([PYTHON_MODULE])
    capability = registry.get("python.execute")

    assert capability.input_schema == "PythonExecuteParams"
    assert capability.result_schema == "PythonExecuteResult"
    assert capability.async_supported is False
    assert "approved Python code" in capability.description
    assert "approved Python script" in capability.description
    assert "live Blender bridge" in capability.description
    assert "headless Blender process" in capability.description
    assert "timeout control" in capability.description


def test_python_execute_async_metadata() -> None:
    registry = load_capabilities([PYTHON_MODULE])
    capability = registry.get("python.execute_async")

    assert capability.input_schema == "PythonExecuteAsyncParams"
    assert capability.result_schema == "JobCreatedResult"
    assert capability.async_supported is True
    assert "long-running approved Python operation" in capability.description
    assert "job identifier immediately" in capability.description
    assert "cancellation checks" in capability.description
    assert "live Blender bridge" in capability.description
    assert "headless Blender process" in capability.description

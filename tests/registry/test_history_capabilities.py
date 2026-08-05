from blender_mcp_server.capabilities.loader import (
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import OperationType, SecurityLevel

HISTORY_MODULE = "blender_mcp_server.capabilities.history"


def test_history_module_loads() -> None:
    module = load_capability_module(HISTORY_MODULE)

    assert module.__name__ == HISTORY_MODULE


def test_history_module_defines_expected_capability_ids() -> None:
    module = load_capability_module(HISTORY_MODULE)
    capabilities = get_module_capabilities(module)

    assert [capability.id for capability in capabilities] == [
        "history.undo",
        "history.redo",
    ]


def test_history_capabilities_are_administrative_operations() -> None:
    module = load_capability_module(HISTORY_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.operation_type is OperationType.ADMINISTRATIVE
        for capability in capabilities
    )


def test_history_capabilities_use_privileged_security() -> None:
    module = load_capability_module(HISTORY_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.security_level is SecurityLevel.PRIVILEGED
        for capability in capabilities
    )


def test_history_capabilities_do_not_support_undo() -> None:
    module = load_capability_module(HISTORY_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.undo_supported is False
        for capability in capabilities
    )


def test_history_capabilities_target_blender_36_or_newer() -> None:
    module = load_capability_module(HISTORY_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.minimum_blender_version == "3.6"
        for capability in capabilities
    )


def test_history_undo_metadata() -> None:
    registry = load_capabilities([HISTORY_MODULE])
    capability = registry.get("history.undo")

    assert capability.input_schema is None
    assert capability.result_schema == "HistoryOperationResult"
    assert "Undo the last operation" in capability.description


def test_history_redo_metadata() -> None:
    registry = load_capabilities([HISTORY_MODULE])
    capability = registry.get("history.redo")

    assert capability.input_schema is None
    assert capability.result_schema == "HistoryOperationResult"
    assert "Redo the last undone operation" in capability.description

from blender_mcp_server.capabilities.loader import (
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import (
    OperationType,
    SecurityLevel,
)

EXPORT_MODULE = "blender_mcp_server.capabilities.export"


def test_export_module_loads() -> None:
    module = load_capability_module(EXPORT_MODULE)

    assert module.__name__ == EXPORT_MODULE


def test_export_module_defines_expected_capability_ids() -> None:
    module = load_capability_module(EXPORT_MODULE)
    capabilities = get_module_capabilities(module)

    assert [capability.id for capability in capabilities] == [
        "export.gltf",
        "export.obj",
        "export.fbx",
    ]


def test_export_capabilities_are_filesystem_operations() -> None:
    module = load_capability_module(EXPORT_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.operation_type is OperationType.FILESYSTEM
        for capability in capabilities
    )


def test_export_capabilities_use_restricted_security() -> None:
    module = load_capability_module(EXPORT_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.security_level is SecurityLevel.RESTRICTED
        for capability in capabilities
    )


def test_export_capabilities_do_not_support_undo() -> None:
    module = load_capability_module(EXPORT_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.undo_supported is False
        for capability in capabilities
    )


def test_export_capabilities_target_blender_36_or_newer() -> None:
    module = load_capability_module(EXPORT_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.minimum_blender_version == "3.6"
        for capability in capabilities
    )


def test_export_gltf_metadata() -> None:
    registry = load_capabilities([EXPORT_MODULE])
    capability = registry.get("export.gltf")

    assert capability.input_schema == "ExportFilepathParams"
    assert capability.result_schema == "ExportResult"
    assert "glTF or GLB" in capability.description
    assert "output file path" in capability.description


def test_export_obj_metadata() -> None:
    registry = load_capabilities([EXPORT_MODULE])
    capability = registry.get("export.obj")

    assert capability.input_schema == "ExportFilepathParams"
    assert capability.result_schema == "ExportResult"
    assert "OBJ" in capability.description
    assert "output file path" in capability.description


def test_export_fbx_metadata() -> None:
    registry = load_capabilities([EXPORT_MODULE])
    capability = registry.get("export.fbx")

    assert capability.input_schema == "ExportFilepathParams"
    assert capability.result_schema == "ExportResult"
    assert "FBX" in capability.description
    assert "output file path" in capability.description

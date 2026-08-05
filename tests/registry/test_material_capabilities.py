from blender_mcp_server.capabilities.loader import (
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import (
    OperationType,
    SecurityLevel,
)

MATERIAL_MODULE = "blender_mcp_server.capabilities.material"


def test_material_module_loads() -> None:
    module = load_capability_module(MATERIAL_MODULE)

    assert module.__name__ == MATERIAL_MODULE


def test_material_module_defines_expected_capability_ids() -> None:
    module = load_capability_module(MATERIAL_MODULE)
    capabilities = get_module_capabilities(module)

    assert [capability.id for capability in capabilities] == [
        "material.list",
        "material.create",
        "material.assign",
        "material.set_color",
        "material.set_texture",
    ]


def test_material_capability_operation_types() -> None:
    registry = load_capabilities([MATERIAL_MODULE])

    assert (
        registry.get("material.list").operation_type
        is OperationType.READ
    )

    for capability_id in [
        "material.create",
        "material.assign",
        "material.set_color",
    ]:
        assert (
            registry.get(capability_id).operation_type
            is OperationType.MODIFY
        )

    assert (
        registry.get("material.set_texture").operation_type
        is OperationType.FILESYSTEM
    )


def test_material_capabilities_use_expected_security_levels() -> None:
    registry = load_capabilities([MATERIAL_MODULE])

    for capability_id in [
        "material.list",
        "material.create",
        "material.assign",
        "material.set_color",
    ]:
        assert (
            registry.get(capability_id).security_level
            is SecurityLevel.STANDARD
        )

    assert (
        registry.get("material.set_texture").security_level
        is SecurityLevel.RESTRICTED
    )


def test_material_modify_capabilities_support_undo() -> None:
    registry = load_capabilities([MATERIAL_MODULE])

    for capability_id in [
        "material.create",
        "material.assign",
        "material.set_color",
        "material.set_texture",
    ]:
        assert registry.get(capability_id).undo_supported is True


def test_material_capabilities_target_blender_36_or_newer() -> None:
    module = load_capability_module(MATERIAL_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.minimum_blender_version == "3.6"
        for capability in capabilities
    )


def test_material_list_metadata() -> None:
    registry = load_capabilities([MATERIAL_MODULE])
    capability = registry.get("material.list")

    assert capability.input_schema is None
    assert capability.result_schema == "MaterialListResult"
    assert "List all materials" in capability.description


def test_material_create_metadata() -> None:
    registry = load_capabilities([MATERIAL_MODULE])
    capability = registry.get("material.create")

    assert capability.input_schema == "MaterialCreateParams"
    assert capability.result_schema == "MaterialCreateResult"
    assert "Create a new material" in capability.description
    assert "RGB values" in capability.description


def test_material_assign_metadata() -> None:
    registry = load_capabilities([MATERIAL_MODULE])
    capability = registry.get("material.assign")

    assert capability.input_schema == "MaterialAssignParams"
    assert capability.result_schema == "MaterialAssignResult"
    assert "Assign an existing material" in capability.description


def test_material_set_color_metadata() -> None:
    registry = load_capabilities([MATERIAL_MODULE])
    capability = registry.get("material.set_color")

    assert capability.input_schema == "MaterialSetColorParams"
    assert capability.result_schema == "MaterialUpdateResult"
    assert "base color" in capability.description
    assert "RGB values" in capability.description


def test_material_set_texture_metadata() -> None:
    registry = load_capabilities([MATERIAL_MODULE])
    capability = registry.get("material.set_texture")

    assert capability.input_schema == "MaterialSetTextureParams"
    assert capability.result_schema == "MaterialUpdateResult"
    assert "image file" in capability.description
    assert "base-color texture" in capability.description

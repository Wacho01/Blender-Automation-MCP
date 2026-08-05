from blender_mcp_server.capabilities.loader import (
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import (
    OperationType,
    SecurityLevel,
)

OBJECT_MODULE = "blender_mcp_server.capabilities.object"


def test_object_module_loads() -> None:
    module = load_capability_module(OBJECT_MODULE)

    assert module.__name__ == OBJECT_MODULE


def test_object_module_defines_expected_capability_ids() -> None:
    module = load_capability_module(OBJECT_MODULE)
    capabilities = get_module_capabilities(module)

    assert [capability.id for capability in capabilities] == [
        "object.get_transform",
        "object.get_hierarchy",
        "object.create_mesh",
        "object.delete",
        "object.translate",
        "object.rotate",
        "object.scale",
        "object.duplicate",
    ]


def test_object_capability_operation_types() -> None:
    registry = load_capabilities([OBJECT_MODULE])

    assert registry.get(
        "object.get_transform"
    ).operation_type is OperationType.READ
    assert registry.get(
        "object.get_hierarchy"
    ).operation_type is OperationType.READ

    for capability_id in [
        "object.create_mesh",
        "object.delete",
        "object.translate",
        "object.rotate",
        "object.scale",
        "object.duplicate",
    ]:
        assert (
            registry.get(capability_id).operation_type
            is OperationType.MODIFY
        )


def test_object_modify_capabilities_support_undo() -> None:
    registry = load_capabilities([OBJECT_MODULE])

    for capability_id in [
        "object.create_mesh",
        "object.delete",
        "object.translate",
        "object.rotate",
        "object.scale",
        "object.duplicate",
    ]:
        assert registry.get(capability_id).undo_supported is True


def test_object_read_capabilities_do_not_support_undo() -> None:
    registry = load_capabilities([OBJECT_MODULE])

    assert registry.get("object.get_transform").undo_supported is False
    assert registry.get("object.get_hierarchy").undo_supported is False


def test_object_capabilities_use_standard_security() -> None:
    module = load_capability_module(OBJECT_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.security_level is SecurityLevel.STANDARD
        for capability in capabilities
    )


def test_object_capabilities_target_blender_36_or_newer() -> None:
    module = load_capability_module(OBJECT_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.minimum_blender_version == "3.6"
        for capability in capabilities
    )


def test_object_get_transform_metadata() -> None:
    registry = load_capabilities([OBJECT_MODULE])
    capability = registry.get("object.get_transform")

    assert capability.category == "object"
    assert capability.input_schema == "ObjectNameParams"
    assert capability.result_schema == "ObjectTransformResult"
    assert "position" in capability.description
    assert "rotation" in capability.description
    assert "scale" in capability.description


def test_object_get_hierarchy_metadata() -> None:
    registry = load_capabilities([OBJECT_MODULE])
    capability = registry.get("object.get_hierarchy")

    assert capability.category == "object"
    assert capability.input_schema == "ObjectHierarchyParams"
    assert capability.result_schema == "ObjectHierarchyResult"
    assert "parent" in capability.description
    assert "child" in capability.description


def test_object_create_mesh_metadata() -> None:
    registry = load_capabilities([OBJECT_MODULE])
    capability = registry.get("object.create_mesh")

    assert capability.input_schema == "ObjectCreateMeshParams"
    assert capability.result_schema == "ObjectCreateResult"
    assert "mesh object" in capability.description
    assert "primitive type" in capability.description


def test_object_delete_metadata() -> None:
    registry = load_capabilities([OBJECT_MODULE])
    capability = registry.get("object.delete")

    assert capability.input_schema == "ObjectNameParams"
    assert capability.result_schema == "ObjectDeleteResult"
    assert "Delete an object" in capability.description


def test_object_transform_metadata() -> None:
    registry = load_capabilities([OBJECT_MODULE])

    translate = registry.get("object.translate")
    rotate = registry.get("object.rotate")
    scale = registry.get("object.scale")

    assert translate.input_schema == "ObjectTranslateParams"
    assert translate.result_schema == "ObjectTransformResult"
    assert "absolute location" in translate.description
    assert "relative offset" in translate.description

    assert rotate.input_schema == "ObjectRotateParams"
    assert rotate.result_schema == "ObjectTransformResult"
    assert "degrees" in rotate.description

    assert scale.input_schema == "ObjectScaleParams"
    assert scale.result_schema == "ObjectTransformResult"
    assert "three-axis scale" in scale.description


def test_object_duplicate_metadata() -> None:
    registry = load_capabilities([OBJECT_MODULE])
    capability = registry.get("object.duplicate")

    assert capability.input_schema == "ObjectDuplicateParams"
    assert capability.result_schema == "ObjectCreateResult"
    assert "Duplicate an object" in capability.description
    assert "new name" in capability.description

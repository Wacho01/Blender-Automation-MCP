from blender_mcp_server.capabilities.loader import (
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import (
    OperationType,
    SecurityLevel,
)

SCENE_MODULE = "blender_mcp_server.capabilities.scene"


def test_scene_module_loads() -> None:
    module = load_capability_module(SCENE_MODULE)

    assert module.__name__ == SCENE_MODULE


def test_scene_module_defines_expected_capability_ids() -> None:
    module = load_capability_module(SCENE_MODULE)
    capabilities = get_module_capabilities(module)

    assert [capability.id for capability in capabilities] == [
        "scene.get_info",
        "scene.list_objects",
    ]


def test_scene_capabilities_are_read_only() -> None:
    module = load_capability_module(SCENE_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.operation_type is OperationType.READ
        for capability in capabilities
    )
    assert all(
        capability.undo_supported is False
        for capability in capabilities
    )


def test_scene_capabilities_use_standard_security() -> None:
    module = load_capability_module(SCENE_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.security_level is SecurityLevel.STANDARD
        for capability in capabilities
    )


def test_scene_capabilities_target_blender_36_or_newer() -> None:
    module = load_capability_module(SCENE_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.minimum_blender_version == "3.6"
        for capability in capabilities
    )


def test_scene_get_info_metadata() -> None:
    registry = load_capabilities([SCENE_MODULE])
    capability = registry.get("scene.get_info")

    assert capability.category == "scene"
    assert capability.input_schema is None
    assert capability.result_schema == "SceneInfoResult"
    assert "frame range" in capability.description
    assert "object count" in capability.description


def test_scene_list_objects_metadata() -> None:
    registry = load_capabilities([SCENE_MODULE])
    capability = registry.get("scene.list_objects")

    assert capability.category == "scene"
    assert capability.input_schema == "SceneListObjectsParams"
    assert capability.result_schema == "SceneObjectListResult"
    assert "filter by type" in capability.description

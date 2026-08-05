from blender_mcp_server.capabilities.loader import (
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import (
    OperationType,
    SecurityLevel,
)

RENDER_MODULE = "blender_mcp_server.capabilities.render"


def test_render_module_loads() -> None:
    module = load_capability_module(RENDER_MODULE)

    assert module.__name__ == RENDER_MODULE


def test_render_module_defines_expected_capability_ids() -> None:
    module = load_capability_module(RENDER_MODULE)
    capabilities = get_module_capabilities(module)

    assert [capability.id for capability in capabilities] == [
        "render.still",
        "render.animation",
    ]


def test_render_capabilities_are_execution_operations() -> None:
    module = load_capability_module(RENDER_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.operation_type is OperationType.EXECUTION
        for capability in capabilities
    )


def test_render_capabilities_use_restricted_security() -> None:
    module = load_capability_module(RENDER_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.security_level is SecurityLevel.RESTRICTED
        for capability in capabilities
    )


def test_render_capabilities_do_not_support_undo() -> None:
    module = load_capability_module(RENDER_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.undo_supported is False
        for capability in capabilities
    )


def test_render_capabilities_target_blender_36_or_newer() -> None:
    module = load_capability_module(RENDER_MODULE)
    capabilities = get_module_capabilities(module)

    assert all(
        capability.minimum_blender_version == "3.6"
        for capability in capabilities
    )


def test_render_still_metadata() -> None:
    registry = load_capabilities([RENDER_MODULE])
    capability = registry.get("render.still")

    assert capability.input_schema == "RenderStillParams"
    assert capability.result_schema == "RenderStillResult"
    assert capability.async_supported is False
    assert "still image" in capability.description
    assert "live Blender bridge" in capability.description
    assert "headless Blender process" in capability.description
    assert "resolution" in capability.description
    assert "render engine" in capability.description


def test_render_animation_metadata() -> None:
    registry = load_capabilities([RENDER_MODULE])
    capability = registry.get("render.animation")

    assert capability.input_schema == "RenderAnimationParams"
    assert capability.result_schema == "RenderAnimationResult"
    assert capability.async_supported is True
    assert "Render an animation" in capability.description
    assert "live Blender bridge" in capability.description
    assert "headless Blender process" in capability.description
    assert "frame range" in capability.description
    assert "render engine" in capability.description

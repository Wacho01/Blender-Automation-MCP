from __future__ import annotations

import sys
from types import ModuleType

import pytest

from blender_mcp_server.capabilities import (
    CapabilityModuleLoadError,
    get_module_capabilities,
    load_capabilities,
    load_capability_module,
)
from blender_mcp_server.registry import (
    CapabilityAlreadyRegisteredError,
    CapabilityDefinition,
    CapabilityRegistry,
    OperationType,
)


def make_capability(
    capability_id: str,
    *,
    category: str = "scene",
) -> CapabilityDefinition:
    return CapabilityDefinition(
        id=capability_id,
        category=category,
        description=f"Test capability for {capability_id}.",
        operation_type=OperationType.READ,
    )


def install_test_module(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
    *,
    capabilities: list[CapabilityDefinition] | None = None,
    include_getter: bool = True,
    getter_error: Exception | None = None,
) -> ModuleType:
    module = ModuleType(module_name)

    if include_getter:

        def get_capabilities() -> list[CapabilityDefinition]:
            if getter_error is not None:
                raise getter_error

            return capabilities or []

        module.get_capabilities = get_capabilities  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, module_name, module)
    return module


def test_load_capability_module_imports_valid_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module_name = "tests.fake_capabilities.valid"
    expected_module = install_test_module(
        monkeypatch,
        module_name,
    )

    loaded_module = load_capability_module(module_name)

    assert loaded_module is expected_module


def test_load_capability_module_rejects_missing_module() -> None:
    with pytest.raises(
        CapabilityModuleLoadError,
        match="Unable to import",
    ):
        load_capability_module("tests.fake_capabilities.missing")


def test_load_capability_module_requires_getter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module_name = "tests.fake_capabilities.no_getter"
    install_test_module(
        monkeypatch,
        module_name,
        include_getter=False,
    )

    with pytest.raises(
        CapabilityModuleLoadError,
        match=r"get_capabilities\(\)",
    ):
        load_capability_module(module_name)


def test_get_module_capabilities_returns_definitions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capability = make_capability("scene.inspect")
    module = install_test_module(
        monkeypatch,
        "tests.fake_capabilities.scene",
        capabilities=[capability],
    )

    assert get_module_capabilities(module) == [capability]


def test_get_module_capabilities_rejects_invalid_item(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module_name = "tests.fake_capabilities.invalid_item"
    module = ModuleType(module_name)

    def get_capabilities() -> list[object]:
        return ["not-a-capability"]

    module.get_capabilities = get_capabilities  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, module_name, module)

    with pytest.raises(
        CapabilityModuleLoadError,
        match="not a CapabilityDefinition",
    ):
        get_module_capabilities(module)


def test_get_module_capabilities_wraps_getter_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = install_test_module(
        monkeypatch,
        "tests.fake_capabilities.error",
        getter_error=RuntimeError("test failure"),
    )

    with pytest.raises(
        CapabilityModuleLoadError,
        match="failed while returning",
    ):
        get_module_capabilities(module)


def test_load_capabilities_builds_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scene_capability = make_capability("scene.inspect")
    object_capability = make_capability(
        "object.inspect",
        category="object",
    )

    install_test_module(
        monkeypatch,
        "tests.fake_capabilities.scene",
        capabilities=[scene_capability],
    )
    install_test_module(
        monkeypatch,
        "tests.fake_capabilities.object",
        capabilities=[object_capability],
    )

    registry = load_capabilities(
        [
            "tests.fake_capabilities.scene",
            "tests.fake_capabilities.object",
        ]
    )

    assert registry.count() == 2
    assert registry.get("scene.inspect") is scene_capability
    assert registry.get("object.inspect") is object_capability


def test_load_capabilities_uses_existing_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = CapabilityRegistry(
        [make_capability("scene.existing")]
    )
    new_capability = make_capability("scene.new")

    install_test_module(
        monkeypatch,
        "tests.fake_capabilities.additional",
        capabilities=[new_capability],
    )

    returned_registry = load_capabilities(
        ["tests.fake_capabilities.additional"],
        registry=registry,
    )

    assert returned_registry is registry
    assert returned_registry.count() == 2


def test_load_capabilities_rejects_duplicate_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    duplicate = make_capability("scene.inspect")

    install_test_module(
        monkeypatch,
        "tests.fake_capabilities.first",
        capabilities=[duplicate],
    )
    install_test_module(
        monkeypatch,
        "tests.fake_capabilities.second",
        capabilities=[duplicate],
    )

    with pytest.raises(CapabilityAlreadyRegisteredError):
        load_capabilities(
            [
                "tests.fake_capabilities.first",
                "tests.fake_capabilities.second",
            ]
        )

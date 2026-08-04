import pytest

from blender_mcp_server.registry import (
    CapabilityAlreadyRegisteredError,
    CapabilityDefinition,
    CapabilityNotFoundError,
    CapabilityRegistry,
    OperationType,
    SecurityLevel,
)


def make_capability(
    capability_id: str = "scene.get_info",
    *,
    category: str = "scene",
    enabled: bool = True,
    deprecated: bool = False,
) -> CapabilityDefinition:
    return CapabilityDefinition(
        id=capability_id,
        category=category,
        description=f"Test capability for {capability_id}.",
        operation_type=OperationType.READ,
        security_level=SecurityLevel.STANDARD,
        enabled=enabled,
        deprecated=deprecated,
    )


def test_capability_requires_category_operation_id() -> None:
    with pytest.raises(ValueError, match="category.operation"):
        make_capability("invalid")


def test_capability_requires_description() -> None:
    with pytest.raises(ValueError, match="description"):
        CapabilityDefinition(
            id="scene.inspect",
            category="scene",
            description="",
            operation_type=OperationType.READ,
        )


def test_registry_registers_and_gets_capability() -> None:
    registry = CapabilityRegistry()
    capability = make_capability()

    returned = registry.register(capability)

    assert returned is capability
    assert registry.get("scene.get_info") is capability
    assert registry.contains("scene.get_info") is True
    assert registry.count() == 1


def test_registry_rejects_duplicate_ids() -> None:
    registry = CapabilityRegistry([make_capability()])

    with pytest.raises(
        CapabilityAlreadyRegisteredError,
        match="already registered",
    ):
        registry.register(make_capability())


def test_registry_raises_for_missing_capability() -> None:
    registry = CapabilityRegistry()

    with pytest.raises(
        CapabilityNotFoundError,
        match="not registered",
    ):
        registry.get("mesh.missing")


def test_registry_lists_capabilities_sorted_by_id() -> None:
    registry = CapabilityRegistry(
        [
            make_capability("mesh.inspect", category="mesh"),
            make_capability("scene.get_info", category="scene"),
            make_capability("object.inspect", category="object"),
        ]
    )

    assert [
        capability.id
        for capability in registry.list()
    ] == [
        "mesh.inspect",
        "object.inspect",
        "scene.get_info",
    ]


def test_registry_filters_by_category() -> None:
    registry = CapabilityRegistry(
        [
            make_capability("mesh.inspect", category="mesh"),
            make_capability("mesh.repair", category="mesh"),
            make_capability("scene.get_info", category="scene"),
        ]
    )

    assert [
        capability.id
        for capability in registry.list(category="mesh")
    ] == [
        "mesh.inspect",
        "mesh.repair",
    ]


def test_registry_filters_enabled_capabilities() -> None:
    registry = CapabilityRegistry(
        [
            make_capability("scene.enabled", enabled=True),
            make_capability("scene.disabled", enabled=False),
        ]
    )

    assert [
        capability.id
        for capability in registry.list(enabled_only=True)
    ] == [
        "scene.enabled",
    ]


def test_registry_can_exclude_deprecated_capabilities() -> None:
    registry = CapabilityRegistry(
        [
            make_capability("scene.current"),
            make_capability(
                "scene.legacy",
                deprecated=True,
            ),
        ]
    )

    assert [
        capability.id
        for capability in registry.list(
            include_deprecated=False,
        )
    ] == [
        "scene.current",
    ]


def test_registry_lists_categories() -> None:
    registry = CapabilityRegistry(
        [
            make_capability("scene.inspect", category="scene"),
            make_capability("mesh.inspect", category="mesh"),
            make_capability("object.inspect", category="object"),
        ]
    )

    assert registry.categories() == [
        "mesh",
        "object",
        "scene",
    ]


def test_registry_clear_removes_all_capabilities() -> None:
    registry = CapabilityRegistry([make_capability()])

    registry.clear()

    assert registry.count() == 0
    assert registry.list() == []

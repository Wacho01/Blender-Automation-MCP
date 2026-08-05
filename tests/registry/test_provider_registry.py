from __future__ import annotations

import pytest

from blender_mcp_server.providers import (
    CapabilityProvider,
    ProviderAlreadyRegisteredError,
    ProviderInfo,
    ProviderNotFoundError,
    ProviderRegistry,
    ProviderRequest,
    ProviderResult,
    ProviderUnavailableError,
)


class FakeProvider:
    def __init__(
        self,
        provider_id: str,
        *,
        capabilities: tuple[str, ...],
        available: bool = True,
    ) -> None:
        self._info = ProviderInfo(
            id=provider_id,
            name=f"{provider_id} provider",
            version="1.0.0",
            description=f"Test provider {provider_id}.",
            capabilities=capabilities,
            available=available,
        )

    def get_info(self) -> ProviderInfo:
        return self._info

    def supports(self, capability_id: str) -> bool:
        return capability_id in self._info.capabilities

    async def execute(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:
        return ProviderResult(
            request_id=request.request_id,
            provider_id=self._info.id,
            capability_id=request.capability_id,
            success=True,
            result={"provider": self._info.id},
        )


def test_fake_provider_satisfies_protocol() -> None:
    provider = FakeProvider(
        "bridge",
        capabilities=("scene.get_info",),
    )

    assert isinstance(provider, CapabilityProvider)


def test_registry_registers_and_gets_provider() -> None:
    provider = FakeProvider(
        "bridge",
        capabilities=("scene.get_info",),
    )
    registry = ProviderRegistry()

    returned = registry.register(provider)

    assert returned is provider
    assert registry.get("bridge") is provider
    assert registry.contains("bridge") is True
    assert registry.count() == 1


def test_registry_rejects_duplicate_provider_ids() -> None:
    registry = ProviderRegistry(
        [
            FakeProvider(
                "bridge",
                capabilities=("scene.get_info",),
            )
        ]
    )

    with pytest.raises(
        ProviderAlreadyRegisteredError,
        match="already registered",
    ):
        registry.register(
            FakeProvider(
                "bridge",
                capabilities=("object.get_transform",),
            )
        )


def test_registry_unregisters_provider() -> None:
    provider = FakeProvider(
        "bridge",
        capabilities=("scene.get_info",),
    )
    registry = ProviderRegistry([provider])

    removed = registry.unregister("bridge")

    assert removed is provider
    assert registry.contains("bridge") is False
    assert registry.count() == 0


def test_registry_raises_for_missing_provider() -> None:
    registry = ProviderRegistry()

    with pytest.raises(
        ProviderNotFoundError,
        match="not registered",
    ):
        registry.get("missing")


def test_registry_unregister_raises_for_missing_provider() -> None:
    registry = ProviderRegistry()

    with pytest.raises(
        ProviderNotFoundError,
        match="not registered",
    ):
        registry.unregister("missing")


def test_registry_lists_providers_sorted_by_id() -> None:
    registry = ProviderRegistry(
        [
            FakeProvider(
                "headless",
                capabilities=("render.still",),
            ),
            FakeProvider(
                "bridge",
                capabilities=("scene.get_info",),
            ),
        ]
    )

    assert [
        provider.get_info().id
        for provider in registry.list()
    ] == [
        "bridge",
        "headless",
    ]


def test_registry_filters_available_providers() -> None:
    registry = ProviderRegistry(
        [
            FakeProvider(
                "bridge",
                capabilities=("scene.get_info",),
                available=True,
            ),
            FakeProvider(
                "offline",
                capabilities=("scene.get_info",),
                available=False,
            ),
        ]
    )

    assert [
        provider.get_info().id
        for provider in registry.list(available_only=True)
    ] == [
        "bridge",
    ]


def test_registry_filters_by_capability() -> None:
    registry = ProviderRegistry(
        [
            FakeProvider(
                "bridge",
                capabilities=(
                    "scene.get_info",
                    "object.get_transform",
                ),
            ),
            FakeProvider(
                "headless",
                capabilities=("render.still",),
            ),
        ]
    )

    assert [
        provider.get_info().id
        for provider in registry.list(
            capability_id="scene.get_info"
        )
    ] == [
        "bridge",
    ]


def test_find_for_capability_excludes_unavailable_by_default() -> None:
    registry = ProviderRegistry(
        [
            FakeProvider(
                "bridge",
                capabilities=("render.still",),
                available=True,
            ),
            FakeProvider(
                "offline",
                capabilities=("render.still",),
                available=False,
            ),
        ]
    )

    assert [
        provider.get_info().id
        for provider in registry.find_for_capability(
            "render.still"
        )
    ] == [
        "bridge",
    ]


def test_find_for_capability_can_include_unavailable() -> None:
    registry = ProviderRegistry(
        [
            FakeProvider(
                "bridge",
                capabilities=("render.still",),
                available=True,
            ),
            FakeProvider(
                "offline",
                capabilities=("render.still",),
                available=False,
            ),
        ]
    )

    assert [
        provider.get_info().id
        for provider in registry.find_for_capability(
            "render.still",
            available_only=False,
        )
    ] == [
        "bridge",
        "offline",
    ]


def test_select_uses_preferred_provider_order() -> None:
    bridge = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    headless = FakeProvider(
        "headless",
        capabilities=("render.still",),
    )
    registry = ProviderRegistry([bridge, headless])

    selected = registry.select(
        "render.still",
        preferred_provider_ids=(
            "headless",
            "bridge",
        ),
    )

    assert selected is headless


def test_select_falls_back_to_sorted_provider_order() -> None:
    bridge = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    headless = FakeProvider(
        "headless",
        capabilities=("render.still",),
    )
    registry = ProviderRegistry([headless, bridge])

    selected = registry.select("render.still")

    assert selected is bridge


def test_select_skips_unavailable_preferred_provider() -> None:
    bridge = FakeProvider(
        "bridge",
        capabilities=("render.still",),
        available=True,
    )
    headless = FakeProvider(
        "headless",
        capabilities=("render.still",),
        available=False,
    )
    registry = ProviderRegistry([bridge, headless])

    selected = registry.select(
        "render.still",
        preferred_provider_ids=(
            "headless",
            "bridge",
        ),
    )

    assert selected is bridge


def test_select_raises_when_no_provider_is_available() -> None:
    registry = ProviderRegistry(
        [
            FakeProvider(
                "offline",
                capabilities=("render.still",),
                available=False,
            )
        ]
    )

    with pytest.raises(
        ProviderUnavailableError,
        match="No available provider supports",
    ):
        registry.select("render.still")


def test_registry_clear_removes_all_providers() -> None:
    registry = ProviderRegistry(
        [
            FakeProvider(
                "bridge",
                capabilities=("scene.get_info",),
            )
        ]
    )

    registry.clear()

    assert registry.count() == 0
    assert registry.list() == []

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from blender_mcp_server.providers import (
    CapabilityRouter,
    ProviderInfo,
    ProviderRegistry,
    ProviderRequest,
    ProviderResult,
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
        self.execute = AsyncMock(side_effect=self._execute)

    def get_info(self) -> ProviderInfo:
        return self._info

    def supports(self, capability_id: str) -> bool:
        return capability_id in self._info.capabilities

    async def _execute(
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


def make_request(
    capability_id: str = "render.still",
) -> ProviderRequest:
    return ProviderRequest(
        request_id="request-1",
        capability_id=capability_id,
        parameters={"output_path": "render.png"},
    )


@pytest.mark.asyncio
async def test_router_selects_available_provider() -> None:
    bridge = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    router = CapabilityRouter(
        ProviderRegistry([bridge])
    )

    result = await router.execute(make_request())

    bridge.execute.assert_awaited_once()
    assert result.success is True
    assert result.provider_id == "bridge"
    assert result.result == {"provider": "bridge"}
    assert result.metadata["selected_provider_id"] == "bridge"


@pytest.mark.asyncio
async def test_router_honors_default_preference_order() -> None:
    bridge = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    headless = FakeProvider(
        "headless",
        capabilities=("render.still",),
    )
    router = CapabilityRouter(
        ProviderRegistry([bridge, headless]),
        preferred_provider_ids=("headless", "bridge"),
    )

    result = await router.execute(make_request())

    assert result.provider_id == "headless"
    headless.execute.assert_awaited_once()
    bridge.execute.assert_not_awaited()
    assert result.metadata["preferred_provider_ids"] == (
        "headless",
        "bridge",
    )


@pytest.mark.asyncio
async def test_request_preference_overrides_default_order() -> None:
    bridge = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    headless = FakeProvider(
        "headless",
        capabilities=("render.still",),
    )
    router = CapabilityRouter(
        ProviderRegistry([bridge, headless]),
        preferred_provider_ids=("bridge", "headless"),
    )

    result = await router.execute(
        make_request(),
        preferred_provider_ids=("headless",),
    )

    assert result.provider_id == "headless"
    headless.execute.assert_awaited_once()
    bridge.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_router_skips_unavailable_preferred_provider() -> None:
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
    router = CapabilityRouter(
        ProviderRegistry([bridge, headless]),
        preferred_provider_ids=("headless", "bridge"),
    )

    result = await router.execute(make_request())

    assert result.provider_id == "bridge"
    bridge.execute.assert_awaited_once()
    headless.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_router_returns_failure_when_no_provider_exists() -> None:
    router = CapabilityRouter(ProviderRegistry())

    result = await router.execute(make_request())

    assert result.success is False
    assert result.provider_id == "router"
    assert result.error is not None
    assert "No available provider supports" in result.error
    assert result.metadata["routing_failure"] is True


@pytest.mark.asyncio
async def test_router_returns_failure_when_only_provider_is_offline() -> None:
    offline = FakeProvider(
        "offline",
        capabilities=("render.still",),
        available=False,
    )
    router = CapabilityRouter(
        ProviderRegistry([offline])
    )

    result = await router.execute(make_request())

    offline.execute.assert_not_awaited()
    assert result.success is False
    assert result.provider_id == "router"
    assert result.metadata["routing_failure"] is True


@pytest.mark.asyncio
async def test_router_preserves_provider_failure_result() -> None:
    provider = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    provider.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="bridge",
            capability_id="render.still",
            success=False,
            error="Render failed",
            metadata={"provider_failure": True},
        )
    )
    router = CapabilityRouter(
        ProviderRegistry([provider])
    )

    result = await router.execute(make_request())

    assert result.success is False
    assert result.error == "Render failed"
    assert result.metadata["provider_failure"] is True
    assert result.metadata["selected_provider_id"] == "bridge"


@pytest.mark.asyncio
async def test_router_normalizes_unhandled_provider_exception() -> None:
    provider = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    provider.execute = AsyncMock(
        side_effect=RuntimeError("unexpected failure")
    )
    router = CapabilityRouter(
        ProviderRegistry([provider])
    )

    result = await router.execute(make_request())

    assert result.success is False
    assert result.provider_id == "bridge"
    assert result.error == "unexpected failure"
    assert result.metadata["exception_type"] == "RuntimeError"
    assert result.metadata["routing_failure"] is False


@pytest.mark.asyncio
async def test_router_uses_exception_class_when_message_is_empty() -> None:
    provider = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    provider.execute = AsyncMock(
        side_effect=RuntimeError()
    )
    router = CapabilityRouter(
        ProviderRegistry([provider])
    )

    result = await router.execute(make_request())

    assert result.success is False
    assert result.error == "RuntimeError"
    assert result.metadata["exception_type"] == "RuntimeError"


@pytest.mark.asyncio
async def test_router_preserves_request_identity() -> None:
    provider = FakeProvider(
        "bridge",
        capabilities=("scene.get_info",),
    )
    router = CapabilityRouter(
        ProviderRegistry([provider])
    )
    request = ProviderRequest(
        request_id="request-special",
        capability_id="scene.get_info",
    )

    result = await router.execute(request)

    assert result.request_id == "request-special"
    assert result.capability_id == "scene.get_info"


@pytest.mark.asyncio
async def test_router_does_not_replace_existing_routing_metadata() -> None:
    provider = FakeProvider(
        "bridge",
        capabilities=("render.still",),
    )
    provider.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="bridge",
            capability_id="render.still",
            success=True,
            result={"ok": True},
            metadata={
                "selected_provider_id": "custom-provider",
                "preferred_provider_ids": ("custom",),
            },
        )
    )
    router = CapabilityRouter(
        ProviderRegistry([provider])
    )

    result = await router.execute(make_request())

    assert (
        result.metadata["selected_provider_id"]
        == "custom-provider"
    )
    assert result.metadata["preferred_provider_ids"] == (
        "custom",
    )

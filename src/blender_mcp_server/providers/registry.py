from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from blender_mcp_server.providers.base import CapabilityProvider


class ProviderAlreadyRegisteredError(ValueError):
    """Raised when a duplicate provider ID is registered."""


class ProviderNotFoundError(KeyError):
    """Raised when a requested provider does not exist."""


class ProviderUnavailableError(RuntimeError):
    """Raised when no available provider can satisfy a capability."""


class ProviderRegistry:
    """Store, query, and select capability providers."""

    def __init__(
        self,
        providers: Iterable[CapabilityProvider] | None = None,
    ) -> None:
        self._providers: dict[str, CapabilityProvider] = {}

        if providers is not None:
            for provider in providers:
                self.register(provider)

    def register(
        self,
        provider: CapabilityProvider,
    ) -> CapabilityProvider:
        provider_id = provider.get_info().id

        if provider_id in self._providers:
            raise ProviderAlreadyRegisteredError(
                f"Provider '{provider_id}' is already registered."
            )

        self._providers[provider_id] = provider
        return provider

    def unregister(self, provider_id: str) -> CapabilityProvider:
        try:
            return self._providers.pop(provider_id)
        except KeyError as exc:
            raise ProviderNotFoundError(
                f"Provider '{provider_id}' is not registered."
            ) from exc

    def get(self, provider_id: str) -> CapabilityProvider:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise ProviderNotFoundError(
                f"Provider '{provider_id}' is not registered."
            ) from exc

    def contains(self, provider_id: str) -> bool:
        return provider_id in self._providers

    def list(
        self,
        *,
        available_only: bool = False,
        capability_id: str | None = None,
    ) -> builtins.list[CapabilityProvider]:
        providers = builtins.list(self._providers.values())

        if available_only:
            providers = [
                provider
                for provider in providers
                if provider.get_info().available
            ]

        if capability_id is not None:
            providers = [
                provider
                for provider in providers
                if provider.supports(capability_id)
            ]

        return sorted(
            providers,
            key=lambda provider: provider.get_info().id,
        )

    def find_for_capability(
        self,
        capability_id: str,
        *,
        available_only: bool = True,
    ) -> builtins.list[CapabilityProvider]:
        return self.list(
            available_only=available_only,
            capability_id=capability_id,
        )

    def select(
        self,
        capability_id: str,
        *,
        preferred_provider_ids: Iterable[str] | None = None,
    ) -> CapabilityProvider:
        available = self.find_for_capability(
            capability_id,
            available_only=True,
        )

        if not available:
            raise ProviderUnavailableError(
                f"No available provider supports capability "
                f"'{capability_id}'."
            )

        available_by_id: dict[str, CapabilityProvider] = {
            provider.get_info().id: provider
            for provider in available
        }

        if preferred_provider_ids is not None:
            for provider_id in preferred_provider_ids:
                provider = available_by_id.get(provider_id)

                if provider is not None:
                    return provider

        return available[0]

    def count(self) -> int:
        return len(self._providers)

    def clear(self) -> None:
        self._providers.clear()

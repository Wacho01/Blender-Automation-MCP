from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from blender_mcp_server.registry.capability import CapabilityDefinition


class CapabilityAlreadyRegisteredError(ValueError):
    """Raised when a duplicate capability ID is registered."""


class CapabilityNotFoundError(KeyError):
    """Raised when a capability ID does not exist."""


class CapabilityRegistry:
    """Store and query registered Blender capabilities."""

    def __init__(
        self,
        capabilities: Iterable[CapabilityDefinition] | None = None,
    ) -> None:
        self._capabilities: dict[str, CapabilityDefinition] = {}

        if capabilities is not None:
            for capability in capabilities:
                self.register(capability)

    def register(
        self,
        capability: CapabilityDefinition,
    ) -> CapabilityDefinition:
        if capability.id in self._capabilities:
            raise CapabilityAlreadyRegisteredError(
                f"Capability '{capability.id}' is already registered."
            )

        self._capabilities[capability.id] = capability
        return capability

    def get(self, capability_id: str) -> CapabilityDefinition:
        try:
            return self._capabilities[capability_id]
        except KeyError as exc:
            raise CapabilityNotFoundError(
                f"Capability '{capability_id}' is not registered."
            ) from exc

    def contains(self, capability_id: str) -> bool:
        return capability_id in self._capabilities

    def list(
        self,
        *,
        category: str | None = None,
        enabled_only: bool = False,
        include_deprecated: bool = True,
    ) -> builtins.list[CapabilityDefinition]:
        capabilities = builtins.list(self._capabilities.values())

        if category is not None:
            capabilities = [
                capability
                for capability in capabilities
                if capability.category == category
            ]

        if enabled_only:
            capabilities = [
                capability
                for capability in capabilities
                if capability.enabled
            ]

        if not include_deprecated:
            capabilities = [
                capability
                for capability in capabilities
                if not capability.deprecated
            ]

        return sorted(
            capabilities,
            key=lambda capability: capability.id,
        )

    def categories(self) -> builtins.list[str]:
        return sorted(
            {
                capability.category
                for capability in self._capabilities.values()
            }
        )

    def count(self) -> int:
        return len(self._capabilities)

    def clear(self) -> None:
        self._capabilities.clear()
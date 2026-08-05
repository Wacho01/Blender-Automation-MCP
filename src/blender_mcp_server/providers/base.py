from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class ProviderInfo:
    """Descriptive metadata for one execution provider."""

    id: str
    name: str
    version: str
    description: str
    capabilities: tuple[str, ...] = ()
    available: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        provider_id = self.id.strip()
        name = self.name.strip()
        version = self.version.strip()
        description = self.description.strip()

        if not provider_id:
            raise ValueError("Provider id cannot be empty.")

        if not name:
            raise ValueError("Provider name cannot be empty.")

        if not version:
            raise ValueError("Provider version cannot be empty.")

        if not description:
            raise ValueError("Provider description cannot be empty.")

        object.__setattr__(self, "id", provider_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "description", description)
        object.__setattr__(
            self,
            "capabilities",
            tuple(sorted(set(self.capabilities))),
        )


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    """Normalized capability execution request sent to a provider."""

    request_id: str
    capability_id: str
    parameters: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float | None = None

    def __post_init__(self) -> None:
        request_id = self.request_id.strip()
        capability_id = self.capability_id.strip()

        if not request_id:
            raise ValueError("Provider request id cannot be empty.")

        if not capability_id:
            raise ValueError("Provider capability id cannot be empty.")

        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("Provider timeout must be greater than zero.")

        object.__setattr__(self, "request_id", request_id)
        object.__setattr__(self, "capability_id", capability_id)


@dataclass(frozen=True, slots=True)
class ProviderResult:
    """Normalized result returned by a provider."""

    request_id: str
    provider_id: str
    capability_id: str
    success: bool
    result: Any = None
    error: str | None = None
    warnings: tuple[str, ...] = ()
    duration_seconds: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        request_id = self.request_id.strip()
        provider_id = self.provider_id.strip()
        capability_id = self.capability_id.strip()

        if not request_id:
            raise ValueError("Provider result request id cannot be empty.")

        if not provider_id:
            raise ValueError("Provider result provider id cannot be empty.")

        if not capability_id:
            raise ValueError("Provider result capability id cannot be empty.")

        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError(
                "Provider result duration cannot be negative."
            )

        if self.success and self.error is not None:
            raise ValueError(
                "A successful provider result cannot include an error."
            )

        if not self.success and not self.error:
            raise ValueError(
                "A failed provider result must include an error."
            )

        object.__setattr__(self, "request_id", request_id)
        object.__setattr__(self, "provider_id", provider_id)
        object.__setattr__(self, "capability_id", capability_id)
        object.__setattr__(self, "warnings", tuple(self.warnings))


@runtime_checkable
class CapabilityProvider(Protocol):
    """Interface implemented by all capability execution providers."""

    def get_info(self) -> ProviderInfo:
        """Return provider identity, availability, and capability metadata."""

    def supports(self, capability_id: str) -> bool:
        """Return whether this provider supports a capability."""

    async def execute(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:
        """Execute one normalized capability request."""

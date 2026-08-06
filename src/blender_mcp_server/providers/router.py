from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING

from blender_mcp_server.providers.base import (
    ProviderRequest,
    ProviderResult,
)
from blender_mcp_server.providers.registry import (
    ProviderRegistry,
    ProviderUnavailableError,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


class CapabilityRouter:
    """Select a provider and execute normalized capability requests."""

    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        preferred_provider_ids: Iterable[str] | None = None,
    ) -> None:
        self._registry = registry
        self._preferred_provider_ids = tuple(
            preferred_provider_ids or ()
        )

    async def execute(
        self,
        request: ProviderRequest,
        *,
        preferred_provider_ids: Iterable[str] | None = None,
    ) -> ProviderResult:
        started_at = perf_counter()

        preferences = (
            tuple(preferred_provider_ids)
            if preferred_provider_ids is not None
            else self._preferred_provider_ids
        )

        try:
            provider = self._registry.select(
                request.capability_id,
                preferred_provider_ids=preferences,
            )
        except ProviderUnavailableError as exc:
            return ProviderResult(
                request_id=request.request_id,
                provider_id="router",
                capability_id=request.capability_id,
                success=False,
                error=str(exc),
                duration_seconds=perf_counter() - started_at,
                metadata={
                    "routing_failure": True,
                    "preferred_provider_ids": preferences,
                },
            )

        try:
            result = await provider.execute(request)
        except Exception as exc:
            return ProviderResult(
                request_id=request.request_id,
                provider_id=provider.get_info().id,
                capability_id=request.capability_id,
                success=False,
                error=str(exc) or exc.__class__.__name__,
                duration_seconds=perf_counter() - started_at,
                metadata={
                    "exception_type": exc.__class__.__name__,
                    "routing_failure": False,
                },
            )

        metadata = dict(result.metadata)
        metadata.setdefault(
            "selected_provider_id",
            provider.get_info().id,
        )
        metadata.setdefault(
            "preferred_provider_ids",
            preferences,
        )

        return ProviderResult(
            request_id=result.request_id,
            provider_id=result.provider_id,
            capability_id=result.capability_id,
            success=result.success,
            result=result.result,
            error=result.error,
            warnings=result.warnings,
            duration_seconds=result.duration_seconds,
            metadata=metadata,
        )

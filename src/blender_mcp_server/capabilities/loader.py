from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Protocol

from blender_mcp_server.registry import (
    CapabilityDefinition,
    CapabilityRegistry,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import ModuleType


class CapabilityModule(Protocol):
    """Protocol implemented by capability-definition modules."""

    def get_capabilities(self) -> Iterable[CapabilityDefinition]:
        """Return the capabilities defined by this module."""


class CapabilityModuleLoadError(RuntimeError):
    """Raised when a capability module cannot be loaded correctly."""


def load_capability_module(module_name: str) -> ModuleType:
    """Import and validate one capability module."""

    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise CapabilityModuleLoadError(
            f"Unable to import capability module '{module_name}'."
        ) from exc

    get_capabilities = getattr(module, "get_capabilities", None)

    if get_capabilities is None or not callable(get_capabilities):
        raise CapabilityModuleLoadError(
            f"Capability module '{module_name}' must define "
            "a callable get_capabilities() function."
        )

    return module


def get_module_capabilities(
    module: ModuleType,
) -> list[CapabilityDefinition]:
    """Read and validate capability definitions from a module."""

    get_capabilities = getattr(module, "get_capabilities", None)

    if get_capabilities is None or not callable(get_capabilities):
        raise CapabilityModuleLoadError(
            f"Capability module '{module.__name__}' must define "
            "a callable get_capabilities() function."
        )

    try:
        capabilities = list(get_capabilities())
    except Exception as exc:
        raise CapabilityModuleLoadError(
            f"Capability module '{module.__name__}' failed while "
            "returning capability definitions."
        ) from exc

    for capability in capabilities:
        if not isinstance(capability, CapabilityDefinition):
            raise CapabilityModuleLoadError(
                f"Capability module '{module.__name__}' returned an "
                "item that is not a CapabilityDefinition."
            )

    return capabilities


def load_capabilities(
    module_names: Iterable[str],
    *,
    registry: CapabilityRegistry | None = None,
) -> CapabilityRegistry:
    """Load capability modules into a registry."""

    target_registry = registry or CapabilityRegistry()

    for module_name in module_names:
        module = load_capability_module(module_name)

        for capability in get_module_capabilities(module):
            target_registry.register(capability)

    return target_registry

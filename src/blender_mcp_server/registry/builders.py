from __future__ import annotations

from blender_mcp_server.registry.capability import (
    CapabilityDefinition,
    OperationType,
    SecurityLevel,
)

DEFAULT_MINIMUM_BLENDER_VERSION = "3.6"


def read_capability(
    *,
    id: str,
    category: str,
    description: str,
    input_schema: str | None = None,
    result_schema: str | None = None,
    security_level: SecurityLevel = SecurityLevel.STANDARD,
    async_supported: bool = False,
    minimum_blender_version: str = DEFAULT_MINIMUM_BLENDER_VERSION,
    maximum_blender_version: str | None = None,
    enabled: bool = True,
    deprecated: bool = False,
) -> CapabilityDefinition:
    """Create metadata for a read-only capability."""

    return CapabilityDefinition(
        id=id,
        category=category,
        description=description,
        operation_type=OperationType.READ,
        security_level=security_level,
        undo_supported=False,
        async_supported=async_supported,
        enabled=enabled,
        deprecated=deprecated,
        minimum_blender_version=minimum_blender_version,
        maximum_blender_version=maximum_blender_version,
        input_schema=input_schema,
        result_schema=result_schema,
    )


def modify_capability(
    *,
    id: str,
    category: str,
    description: str,
    input_schema: str | None = None,
    result_schema: str | None = None,
    security_level: SecurityLevel = SecurityLevel.STANDARD,
    undo_supported: bool = True,
    async_supported: bool = False,
    minimum_blender_version: str = DEFAULT_MINIMUM_BLENDER_VERSION,
    maximum_blender_version: str | None = None,
    enabled: bool = True,
    deprecated: bool = False,
) -> CapabilityDefinition:
    """Create metadata for a state-modifying capability."""

    return CapabilityDefinition(
        id=id,
        category=category,
        description=description,
        operation_type=OperationType.MODIFY,
        security_level=security_level,
        undo_supported=undo_supported,
        async_supported=async_supported,
        enabled=enabled,
        deprecated=deprecated,
        minimum_blender_version=minimum_blender_version,
        maximum_blender_version=maximum_blender_version,
        input_schema=input_schema,
        result_schema=result_schema,
    )


def execution_capability(
    *,
    id: str,
    category: str,
    description: str,
    input_schema: str | None = None,
    result_schema: str | None = None,
    security_level: SecurityLevel = SecurityLevel.RESTRICTED,
    undo_supported: bool = False,
    async_supported: bool = False,
    minimum_blender_version: str = DEFAULT_MINIMUM_BLENDER_VERSION,
    maximum_blender_version: str | None = None,
    enabled: bool = True,
    deprecated: bool = False,
) -> CapabilityDefinition:
    """Create metadata for a capability that executes code or a long task."""

    return CapabilityDefinition(
        id=id,
        category=category,
        description=description,
        operation_type=OperationType.EXECUTION,
        security_level=security_level,
        undo_supported=undo_supported,
        async_supported=async_supported,
        enabled=enabled,
        deprecated=deprecated,
        minimum_blender_version=minimum_blender_version,
        maximum_blender_version=maximum_blender_version,
        input_schema=input_schema,
        result_schema=result_schema,
    )


def filesystem_capability(
    *,
    id: str,
    category: str,
    description: str,
    input_schema: str | None = None,
    result_schema: str | None = None,
    security_level: SecurityLevel = SecurityLevel.RESTRICTED,
    undo_supported: bool = False,
    async_supported: bool = False,
    minimum_blender_version: str = DEFAULT_MINIMUM_BLENDER_VERSION,
    maximum_blender_version: str | None = None,
    enabled: bool = True,
    deprecated: bool = False,
) -> CapabilityDefinition:
    """Create metadata for a capability that reads or writes files."""

    return CapabilityDefinition(
        id=id,
        category=category,
        description=description,
        operation_type=OperationType.FILESYSTEM,
        security_level=security_level,
        undo_supported=undo_supported,
        async_supported=async_supported,
        enabled=enabled,
        deprecated=deprecated,
        minimum_blender_version=minimum_blender_version,
        maximum_blender_version=maximum_blender_version,
        input_schema=input_schema,
        result_schema=result_schema,
    )


def administrative_capability(
    *,
    id: str,
    category: str,
    description: str,
    input_schema: str | None = None,
    result_schema: str | None = None,
    security_level: SecurityLevel = SecurityLevel.PRIVILEGED,
    undo_supported: bool = False,
    async_supported: bool = False,
    minimum_blender_version: str = DEFAULT_MINIMUM_BLENDER_VERSION,
    maximum_blender_version: str | None = None,
    enabled: bool = True,
    deprecated: bool = False,
) -> CapabilityDefinition:
    """Create metadata for administrative platform operations."""

    return CapabilityDefinition(
        id=id,
        category=category,
        description=description,
        operation_type=OperationType.ADMINISTRATIVE,
        security_level=security_level,
        undo_supported=undo_supported,
        async_supported=async_supported,
        enabled=enabled,
        deprecated=deprecated,
        minimum_blender_version=minimum_blender_version,
        maximum_blender_version=maximum_blender_version,
        input_schema=input_schema,
        result_schema=result_schema,
    )

from __future__ import annotations

from blender_mcp_server.registry import (
    CapabilityDefinition,
    OperationType,
    SecurityLevel,
)


def get_capabilities() -> list[CapabilityDefinition]:
    """Return the existing scene capabilities exposed by the Blender bridge."""

    return [
        CapabilityDefinition(
            id="scene.get_info",
            category="scene",
            description=(
                "Get information about the current Blender scene including "
                "name, frame range, render engine, resolution, and object count."
            ),
            operation_type=OperationType.READ,
            security_level=SecurityLevel.STANDARD,
            undo_supported=False,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema=None,
            result_schema="SceneInfoResult",
        ),
        CapabilityDefinition(
            id="scene.list_objects",
            category="scene",
            description=(
                "List all objects in the current Blender scene. Optionally "
                "filter by type such as MESH, CAMERA, LIGHT, EMPTY, or CURVE."
            ),
            operation_type=OperationType.READ,
            security_level=SecurityLevel.STANDARD,
            undo_supported=False,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="SceneListObjectsParams",
            result_schema="SceneObjectListResult",
        ),
    ]

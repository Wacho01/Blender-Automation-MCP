from __future__ import annotations

from blender_mcp_server.registry import (
    CapabilityDefinition,
    OperationType,
    SecurityLevel,
)


def get_capabilities() -> list[CapabilityDefinition]:
    """Return the existing object capabilities exposed by the Blender bridge."""

    return [
        CapabilityDefinition(
            id="object.get_transform",
            category="object",
            description=(
                "Get the position, rotation, and scale of a Blender object "
                "by name."
            ),
            operation_type=OperationType.READ,
            security_level=SecurityLevel.STANDARD,
            undo_supported=False,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="ObjectNameParams",
            result_schema="ObjectTransformResult",
        ),
        CapabilityDefinition(
            id="object.get_hierarchy",
            category="object",
            description=(
                "Get the parent and child hierarchy of Blender objects. "
                "Optionally return the subtree for one named object."
            ),
            operation_type=OperationType.READ,
            security_level=SecurityLevel.STANDARD,
            undo_supported=False,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="ObjectHierarchyParams",
            result_schema="ObjectHierarchyResult",
        ),
        CapabilityDefinition(
            id="object.create_mesh",
            category="object",
            description=(
                "Create a Blender mesh object from a supported primitive type, "
                "with an optional name, location, and size."
            ),
            operation_type=OperationType.MODIFY,
            security_level=SecurityLevel.STANDARD,
            undo_supported=True,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="ObjectCreateMeshParams",
            result_schema="ObjectCreateResult",
        ),
        CapabilityDefinition(
            id="object.delete",
            category="object",
            description="Delete an object from the Blender scene by name.",
            operation_type=OperationType.MODIFY,
            security_level=SecurityLevel.STANDARD,
            undo_supported=True,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="ObjectNameParams",
            result_schema="ObjectDeleteResult",
        ),
        CapabilityDefinition(
            id="object.translate",
            category="object",
            description=(
                "Move an object using either an absolute location or a "
                "relative offset."
            ),
            operation_type=OperationType.MODIFY,
            security_level=SecurityLevel.STANDARD,
            undo_supported=True,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="ObjectTranslateParams",
            result_schema="ObjectTransformResult",
        ),
        CapabilityDefinition(
            id="object.rotate",
            category="object",
            description=(
                "Set an object's rotation using three-axis angles, interpreted "
                "as degrees by default."
            ),
            operation_type=OperationType.MODIFY,
            security_level=SecurityLevel.STANDARD,
            undo_supported=True,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="ObjectRotateParams",
            result_schema="ObjectTransformResult",
        ),
        CapabilityDefinition(
            id="object.scale",
            category="object",
            description="Set the three-axis scale of a Blender object.",
            operation_type=OperationType.MODIFY,
            security_level=SecurityLevel.STANDARD,
            undo_supported=True,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="ObjectScaleParams",
            result_schema="ObjectTransformResult",
        ),
        CapabilityDefinition(
            id="object.duplicate",
            category="object",
            description=(
                "Duplicate an object in the Blender scene and optionally assign "
                "the duplicate a new name."
            ),
            operation_type=OperationType.MODIFY,
            security_level=SecurityLevel.STANDARD,
            undo_supported=True,
            async_supported=False,
            minimum_blender_version="3.6",
            input_schema="ObjectDuplicateParams",
            result_schema="ObjectCreateResult",
        ),
    ]

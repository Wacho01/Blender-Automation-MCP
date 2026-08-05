from __future__ import annotations

from blender_mcp_server.registry import (
    filesystem_capability,
    modify_capability,
    read_capability,
)


def get_capabilities():
    """Return the existing material capabilities exposed by Blender."""

    return [
        read_capability(
            id="material.list",
            category="material",
            description="List all materials in the Blender file.",
            input_schema=None,
            result_schema="MaterialListResult",
        ),
        modify_capability(
            id="material.create",
            category="material",
            description=(
                "Create a new material and optionally set an initial base "
                "color using RGB values from 0 to 1."
            ),
            input_schema="MaterialCreateParams",
            result_schema="MaterialCreateResult",
        ),
        modify_capability(
            id="material.assign",
            category="material",
            description="Assign an existing material to a Blender object.",
            input_schema="MaterialAssignParams",
            result_schema="MaterialAssignResult",
        ),
        modify_capability(
            id="material.set_color",
            category="material",
            description=(
                "Set the base color of a material using RGB values from 0 to 1."
            ),
            input_schema="MaterialSetColorParams",
            result_schema="MaterialUpdateResult",
        ),
        filesystem_capability(
            id="material.set_texture",
            category="material",
            description=(
                "Set an image file as the base-color texture of a material."
            ),
            input_schema="MaterialSetTextureParams",
            result_schema="MaterialUpdateResult",
            undo_supported=True,
        ),
    ]

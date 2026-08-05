from __future__ import annotations

from blender_mcp_server.registry import filesystem_capability


def get_capabilities():
    """Return the existing export capabilities exposed by Blender."""

    return [
        filesystem_capability(
            id="export.gltf",
            category="export",
            description=(
                "Export the current Blender scene as glTF or GLB to the "
                "provided output file path."
            ),
            input_schema="ExportFilepathParams",
            result_schema="ExportResult",
        ),
        filesystem_capability(
            id="export.obj",
            category="export",
            description=(
                "Export the current Blender scene as OBJ to the provided "
                "output file path."
            ),
            input_schema="ExportFilepathParams",
            result_schema="ExportResult",
        ),
        filesystem_capability(
            id="export.fbx",
            category="export",
            description=(
                "Export the current Blender scene as FBX to the provided "
                "output file path."
            ),
            input_schema="ExportFilepathParams",
            result_schema="ExportResult",
        ),
    ]

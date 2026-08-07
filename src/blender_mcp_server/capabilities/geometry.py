from __future__ import annotations

from blender_mcp_server.registry import modify_capability


def get_capabilities():
    """Return geometry-editing capabilities exposed by Blender."""

    return [
        modify_capability(
            id="mesh.extrude",
            category="mesh",
            description=(
                "Extrude selected mesh geometry by a distance or vector."
            ),
            input_schema="MeshExtrudeParams",
            result_schema="MeshEditResult",
        ),
        modify_capability(
            id="mesh.bevel",
            category="mesh",
            description=(
                "Bevel selected mesh geometry using a width and segment count."
            ),
            input_schema="MeshBevelParams",
            result_schema="MeshEditResult",
        ),
        modify_capability(
            id="mesh.inset",
            category="mesh",
            description=(
                "Inset selected mesh faces by a thickness value."
            ),
            input_schema="MeshInsetParams",
            result_schema="MeshEditResult",
        ),
        modify_capability(
            id="mesh.boolean",
            category="mesh",
            description=(
                "Apply a boolean operation between two mesh objects."
            ),
            input_schema="MeshBooleanParams",
            result_schema="MeshBooleanResult",
        ),
        modify_capability(
            id="curve.create",
            category="curve",
            description=(
                "Create an editable Blender curve from control points."
            ),
            input_schema="CurveCreateParams",
            result_schema="CurveCreateResult",
        ),
        modify_capability(
            id="surface.create_nurbs",
            category="surface",
            description=(
                "Create an editable NURBS surface from control points."
            ),
            input_schema="SurfaceCreateNurbsParams",
            result_schema="SurfaceCreateResult",
        ),
    ]

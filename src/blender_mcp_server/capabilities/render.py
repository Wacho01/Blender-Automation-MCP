from __future__ import annotations

from blender_mcp_server.registry import execution_capability


def get_capabilities():
    """Return the existing render capabilities exposed by Blender."""

    return [
        execution_capability(
            id="render.still",
            category="render",
            description=(
                "Render a still image using either the live Blender bridge "
                "or a headless Blender process. Optionally configure output "
                "path, resolution, render engine, blend file, and factory "
                "startup behavior."
            ),
            input_schema="RenderStillParams",
            result_schema="RenderStillResult",
            async_supported=False,
        ),
        execution_capability(
            id="render.animation",
            category="render",
            description=(
                "Render an animation using either the live Blender bridge "
                "or a headless Blender process. Optionally configure output "
                "path, frame range, render engine, blend file, and factory "
                "startup behavior."
            ),
            input_schema="RenderAnimationParams",
            result_schema="RenderAnimationResult",
            async_supported=True,
        ),
    ]

from __future__ import annotations

from blender_mcp_server.registry import administrative_capability


def get_capabilities():
    """Return the existing history capabilities exposed by Blender."""

    return [
        administrative_capability(
            id="history.undo",
            category="history",
            description="Undo the last operation in Blender.",
            input_schema=None,
            result_schema="HistoryOperationResult",
            undo_supported=False,
        ),
        administrative_capability(
            id="history.redo",
            category="history",
            description="Redo the last undone operation in Blender.",
            input_schema=None,
            result_schema="HistoryOperationResult",
            undo_supported=False,
        ),
    ]

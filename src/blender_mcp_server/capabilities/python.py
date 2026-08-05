from __future__ import annotations

from blender_mcp_server.registry import execution_capability


def get_capabilities():
    """Return the existing Python execution capabilities."""

    return [
        execution_capability(
            id="python.execute",
            category="python",
            description=(
                "Execute approved Python code or an approved Python script "
                "inside Blender. Supports the live Blender bridge or a "
                "headless Blender process, optional arguments, timeout "
                "control, blend-file selection, and factory-startup behavior."
            ),
            input_schema="PythonExecuteParams",
            result_schema="PythonExecuteResult",
            async_supported=False,
        ),
        execution_capability(
            id="python.execute_async",
            category="python",
            description=(
                "Start a long-running approved Python operation in Blender "
                "and return a job identifier immediately. Supports the live "
                "Blender bridge or a headless Blender process, cancellation "
                "checks, optional arguments, timeout control, blend-file "
                "selection, and factory-startup behavior."
            ),
            input_schema="PythonExecuteAsyncParams",
            result_schema="JobCreatedResult",
            async_supported=True,
        ),
    ]

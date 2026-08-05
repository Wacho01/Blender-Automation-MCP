from __future__ import annotations

from blender_mcp_server.registry import (
    administrative_capability,
    read_capability,
)


def get_capabilities():
    """Return the existing asynchronous job capabilities."""

    return [
        read_capability(
            id="job.status",
            category="job",
            description=(
                "Get the status of an asynchronous Blender job, including "
                "its identifier, lifecycle state, timestamps, result, stdout, "
                "stderr, and error information."
            ),
            input_schema="JobIdParams",
            result_schema="JobStatusResult",
        ),
        administrative_capability(
            id="job.cancel",
            category="job",
            description=(
                "Cancel a queued or running asynchronous Blender job. "
                "Cooperative scripts can detect the cancellation event and "
                "stop gracefully."
            ),
            input_schema="JobIdParams",
            result_schema="JobCancelResult",
        ),
        read_capability(
            id="job.list",
            category="job",
            description=(
                "List known asynchronous Blender jobs from the live bridge "
                "and headless job manager, including identifiers, statuses, "
                "and creation timestamps."
            ),
            input_schema=None,
            result_schema="JobListResult",
        ),
    ]

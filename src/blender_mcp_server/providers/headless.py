from __future__ import annotations

from time import perf_counter
from typing import Any

from blender_mcp_server.headless import (
    HeadlessBlenderExecutor,
    HeadlessJobManager,
)
from blender_mcp_server.providers.base import (
    ProviderInfo,
    ProviderRequest,
    ProviderResult,
)

HEADLESS_CAPABILITIES = (
    "job.cancel",
    "job.list",
    "job.status",
    "python.execute",
    "python.execute_async",
)


class HeadlessProvider:
    """Execute supported capabilities through headless Blender processes."""

    def __init__(
        self,
        executor: HeadlessBlenderExecutor | None = None,
        job_manager: HeadlessJobManager | None = None,
        *,
        version: str = "1.0.0",
    ) -> None:
        self._executor = executor or HeadlessBlenderExecutor()
        self._jobs = job_manager or HeadlessJobManager()
        self._version = version

    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            id="headless",
            name="Headless Blender",
            version=self._version,
            description=(
                "Execute Python and asynchronous job capabilities through "
                "separate background Blender processes."
            ),
            capabilities=HEADLESS_CAPABILITIES,
            available=True,
            metadata={
                "transport": "headless",
                "blender_binary": self._executor.blender_binary,
                "background_process": True,
            },
        )

    def supports(self, capability_id: str) -> bool:
        return capability_id in HEADLESS_CAPABILITIES

    async def execute(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:
        started_at = perf_counter()

        if not self.supports(request.capability_id):
            return ProviderResult(
                request_id=request.request_id,
                provider_id="headless",
                capability_id=request.capability_id,
                success=False,
                error=(
                    "Headless Blender does not support capability "
                    f"'{request.capability_id}'."
                ),
                duration_seconds=perf_counter() - started_at,
            )

        try:
            result = await self._dispatch(request)
        except Exception as exc:
            return ProviderResult(
                request_id=request.request_id,
                provider_id="headless",
                capability_id=request.capability_id,
                success=False,
                error=str(exc) or exc.__class__.__name__,
                duration_seconds=perf_counter() - started_at,
                metadata={
                    "exception_type": exc.__class__.__name__,
                },
            )

        return ProviderResult(
            request_id=request.request_id,
            provider_id="headless",
            capability_id=request.capability_id,
            success=True,
            result=result,
            duration_seconds=perf_counter() - started_at,
        )

    async def _dispatch(
        self,
        request: ProviderRequest,
    ) -> Any:
        capability_id = request.capability_id
        parameters = request.parameters

        if capability_id == "python.execute":
            return await self._executor.execute(
                code=parameters.get("code"),
                script_path=parameters.get("script_path"),
                args=parameters.get("args"),
                timeout_seconds=self._resolve_timeout(request),
                blend_file=parameters.get("blend_file"),
                factory_startup=parameters.get("factory_startup"),
            )

        if capability_id == "python.execute_async":
            job_id = await self._jobs.create_job(
                self._executor,
                code=parameters.get("code"),
                script_path=parameters.get("script_path"),
                args=parameters.get("args"),
                timeout_seconds=self._resolve_timeout(request),
                blend_file=parameters.get("blend_file"),
                factory_startup=parameters.get("factory_startup"),
            )
            return {"job_id": job_id}

        if capability_id == "job.status":
            return self._jobs.get_status(
                self._require_job_id(parameters)
            )

        if capability_id == "job.cancel":
            return await self._jobs.cancel(
                self._require_job_id(parameters)
            )

        if capability_id == "job.list":
            return self._jobs.list_jobs()

        raise RuntimeError(
            f"Unhandled headless capability '{capability_id}'."
        )

    @staticmethod
    def _require_job_id(parameters: dict[str, Any]) -> str:
        job_id = parameters.get("job_id")

        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("Parameter 'job_id' must be a non-empty string.")

        return job_id.strip()

    @staticmethod
    def _resolve_timeout(
        request: ProviderRequest,
    ) -> int | None:
        timeout = request.timeout_seconds

        if timeout is None:
            parameter_timeout = request.parameters.get("timeout_seconds")

            if parameter_timeout is None:
                return None

            timeout = float(parameter_timeout)

        return max(1, int(timeout))

from __future__ import annotations

from typing import Any

import pytest

from blender_mcp_server.providers import (
    CapabilityProvider,
    ProviderInfo,
    ProviderRequest,
    ProviderResult,
)


class ExampleProvider:
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            id="example",
            name="Example Provider",
            version="1.0.0",
            description="Provider used by unit tests.",
            capabilities=("scene.get_info",),
        )

    def supports(self, capability_id: str) -> bool:
        return capability_id == "scene.get_info"

    async def execute(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:
        return ProviderResult(
            request_id=request.request_id,
            provider_id="example",
            capability_id=request.capability_id,
            success=True,
            result={"name": "Scene"},
        )


def test_provider_info_normalizes_values() -> None:
    info = ProviderInfo(
        id="  blender-bridge ",
        name=" Blender Bridge ",
        version=" 1.0.0 ",
        description=" Local Blender bridge provider. ",
        capabilities=(
            "scene.get_info",
            "object.get_transform",
            "scene.get_info",
        ),
    )

    assert info.id == "blender-bridge"
    assert info.name == "Blender Bridge"
    assert info.version == "1.0.0"
    assert info.description == "Local Blender bridge provider."
    assert info.capabilities == (
        "object.get_transform",
        "scene.get_info",
    )


@pytest.mark.parametrize(
    ("field_name", "kwargs", "message"),
    [
        (
            "id",
            {"id": " "},
            "Provider id cannot be empty",
        ),
        (
            "name",
            {"name": " "},
            "Provider name cannot be empty",
        ),
        (
            "version",
            {"version": " "},
            "Provider version cannot be empty",
        ),
        (
            "description",
            {"description": " "},
            "Provider description cannot be empty",
        ),
    ],
)
def test_provider_info_requires_identity_fields(
    field_name: str,
    kwargs: dict[str, str],
    message: str,
) -> None:
    values: dict[str, Any] = {
        "id": "provider",
        "name": "Provider",
        "version": "1.0.0",
        "description": "Provider description.",
    }
    values.update(kwargs)

    with pytest.raises(ValueError, match=message):
        ProviderInfo(**values)

    assert field_name in values


def test_provider_request_normalizes_values() -> None:
    request = ProviderRequest(
        request_id=" request-1 ",
        capability_id=" scene.get_info ",
        parameters={"detail": True},
        timeout_seconds=30,
    )

    assert request.request_id == "request-1"
    assert request.capability_id == "scene.get_info"
    assert request.parameters == {"detail": True}
    assert request.timeout_seconds == 30


def test_provider_request_requires_positive_timeout() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        ProviderRequest(
            request_id="request-1",
            capability_id="scene.get_info",
            timeout_seconds=0,
        )


def test_provider_result_success() -> None:
    result = ProviderResult(
        request_id="request-1",
        provider_id="blender-bridge",
        capability_id="scene.get_info",
        success=True,
        result={"name": "Scene"},
        warnings=["test warning"],
        duration_seconds=0.2,
    )

    assert result.success is True
    assert result.error is None
    assert result.result == {"name": "Scene"}
    assert result.warnings == ("test warning",)
    assert result.duration_seconds == 0.2


def test_provider_result_failure_requires_error() -> None:
    with pytest.raises(ValueError, match="must include an error"):
        ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="scene.get_info",
            success=False,
        )


def test_provider_result_success_rejects_error() -> None:
    with pytest.raises(ValueError, match="cannot include an error"):
        ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="scene.get_info",
            success=True,
            error="unexpected",
        )


def test_provider_result_rejects_negative_duration() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="scene.get_info",
            success=True,
            duration_seconds=-1,
        )


def test_example_provider_satisfies_protocol() -> None:
    provider = ExampleProvider()

    assert isinstance(provider, CapabilityProvider)
    assert provider.supports("scene.get_info") is True
    assert provider.supports("object.delete") is False


@pytest.mark.asyncio
async def test_example_provider_executes_request() -> None:
    provider = ExampleProvider()
    request = ProviderRequest(
        request_id="request-1",
        capability_id="scene.get_info",
    )

    result = await provider.execute(request)

    assert result.success is True
    assert result.provider_id == "example"
    assert result.capability_id == "scene.get_info"
    assert result.result == {"name": "Scene"}

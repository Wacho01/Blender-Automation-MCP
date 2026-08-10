from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from blender_mcp_server.providers import (
    BLENDER_BRIDGE_CAPABILITIES,
    BlenderBridgeProvider,
    CapabilityProvider,
    ProviderRequest,
)


class FakeConnection:
    def __init__(
        self,
        *,
        result: Any = None,
        error: Exception | None = None,
        connected: bool = True,
    ) -> None:
        self._writer = object() if connected else None
        self._result = result
        self._error = error
        self.send_command = AsyncMock(side_effect=self._send_command)

    async def _send_command(
        self,
        command: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        if self._error is not None:
            raise self._error

        return self._result


def test_blender_bridge_provider_satisfies_protocol() -> None:
    provider = BlenderBridgeProvider(FakeConnection())

    assert isinstance(provider, CapabilityProvider)


def test_blender_bridge_provider_info() -> None:
    provider = BlenderBridgeProvider(
        FakeConnection(connected=True),
        version="2.0.0",
    )

    info = provider.get_info()

    assert info.id == "blender-bridge"
    assert info.name == "Blender Bridge"
    assert info.version == "2.0.0"
    assert info.available is True
    assert info.metadata["transport"] == "tcp"
    assert info.metadata["connected"] is True
    assert info.metadata["auto_reconnect"] is True
    assert "live local Blender add-on" in info.description


def test_blender_bridge_provider_reports_disconnected_state() -> None:
    provider = BlenderBridgeProvider(
        FakeConnection(connected=False)
    )

    info = provider.get_info()

    assert info.available is True
    assert info.metadata["connected"] is False
    assert info.metadata["auto_reconnect"] is True


def test_blender_bridge_capability_inventory() -> None:
    assert len(BLENDER_BRIDGE_CAPABILITIES) == 30
    assert tuple(
        sorted(BLENDER_BRIDGE_CAPABILITIES)
    ) == BLENDER_BRIDGE_CAPABILITIES
    assert len(set(BLENDER_BRIDGE_CAPABILITIES)) == 30

    for capability_id in [
        "scene.get_info",
        "object.create_mesh",
        "material.set_texture",
        "render.still",
        "export.gltf",
        "history.undo",
        "python.execute_async",
        "job.cancel",
    ]:
        assert capability_id in BLENDER_BRIDGE_CAPABILITIES


def test_blender_bridge_provider_supports_registered_capabilities() -> None:
    provider = BlenderBridgeProvider(FakeConnection())

    assert provider.supports("scene.get_info") is True
    assert provider.supports("object.translate") is True
    assert provider.supports("future.unsupported") is False


@pytest.mark.asyncio
async def test_execute_forwards_capability_and_parameters() -> None:
    connection = FakeConnection(
        result={"name": "Scene"},
    )
    provider = BlenderBridgeProvider(connection)
    request = ProviderRequest(
        request_id="request-1",
        capability_id="scene.get_info",
        parameters={"detail": True},
    )

    result = await provider.execute(request)

    connection.send_command.assert_awaited_once_with(
        "scene.get_info",
        {"detail": True},
    )
    assert result.request_id == "request-1"
    assert result.provider_id == "blender-bridge"
    assert result.capability_id == "scene.get_info"
    assert result.success is True
    assert result.result == {"name": "Scene"}
    assert result.error is None
    assert result.duration_seconds is not None
    assert result.duration_seconds >= 0


@pytest.mark.asyncio
async def test_execute_forwards_empty_parameters() -> None:
    connection = FakeConnection(result=[])
    provider = BlenderBridgeProvider(connection)
    request = ProviderRequest(
        request_id="request-2",
        capability_id="material.list",
    )

    result = await provider.execute(request)

    connection.send_command.assert_awaited_once_with(
        "material.list",
        {},
    )
    assert result.success is True
    assert result.result == []


@pytest.mark.asyncio
async def test_execute_returns_failure_for_unsupported_capability() -> None:
    connection = FakeConnection()
    provider = BlenderBridgeProvider(connection)
    request = ProviderRequest(
        request_id="request-3",
        capability_id="future.unsupported",
    )

    result = await provider.execute(request)

    connection.send_command.assert_not_awaited()
    assert result.success is False
    assert result.error is not None
    assert "does not support capability" in result.error
    assert result.capability_id == "future.unsupported"


@pytest.mark.asyncio
async def test_execute_normalizes_runtime_error() -> None:
    connection = FakeConnection(
        error=RuntimeError("Object not found"),
    )
    provider = BlenderBridgeProvider(connection)
    request = ProviderRequest(
        request_id="request-4",
        capability_id="object.get_transform",
        parameters={"name": "Missing"},
    )

    result = await provider.execute(request)

    assert result.success is False
    assert result.error == "Object not found"
    assert result.metadata["exception_type"] == "RuntimeError"
    assert result.result is None


@pytest.mark.asyncio
async def test_execute_normalizes_connection_error() -> None:
    connection = FakeConnection(
        error=ConnectionError("Lost connection to Blender"),
        connected=False,
    )
    provider = BlenderBridgeProvider(connection)
    request = ProviderRequest(
        request_id="request-5",
        capability_id="scene.get_info",
    )

    result = await provider.execute(request)

    assert result.success is False
    assert result.error == "Lost connection to Blender"
    assert result.metadata["exception_type"] == "ConnectionError"
    assert result.duration_seconds is not None


@pytest.mark.asyncio
async def test_execute_normalizes_exception_without_message() -> None:
    connection = FakeConnection(error=RuntimeError())
    provider = BlenderBridgeProvider(connection)
    request = ProviderRequest(
        request_id="request-6",
        capability_id="scene.get_info",
    )

    result = await provider.execute(request)

    assert result.success is False
    assert result.error == "RuntimeError"
    assert result.metadata["exception_type"] == "RuntimeError"

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    history_redo,
    history_undo,
)

HistoryFunction = Callable[..., Awaitable[str]]


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_history_undo_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="history.undo",
            success=True,
            result={
                "undone": True,
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await history_undo(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "history.undo"
    assert request.parameters == {}
    assert json.loads(result) == {
        "undone": True,
    }


@pytest.mark.asyncio
async def test_history_redo_routes_through_router() -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="history.redo",
            success=True,
            result={
                "redone": True,
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await history_redo(ctx)

    request = router.execute.await_args.args[0]

    assert request.capability_id == "history.redo"
    assert request.parameters == {}
    assert json.loads(result) == {
        "redone": True,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function", "capability_id"),
    [
        (
            history_undo,
            "history.undo",
        ),
        (
            history_redo,
            "history.redo",
        ),
    ],
)
async def test_history_tools_raise_for_provider_failure(
    function: HistoryFunction,
    capability_id: str,
) -> None:
    ctx = make_context()
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-failure",
            provider_id="blender-bridge",
            capability_id=capability_id,
            success=False,
            error=f"{capability_id} failed",
        )
    )

    with (
        patch(
            "blender_mcp_server.server._get_router",
            return_value=router,
        ),
        pytest.raises(
            RuntimeError,
            match=rf"{capability_id} failed",
        ),
    ):
        await function(ctx)

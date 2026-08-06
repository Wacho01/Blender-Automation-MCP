from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp_server.providers import ProviderResult
from blender_mcp_server.server import (
    render_animation,
    render_still,
)

RenderFunction = Callable[..., Awaitable[str]]


def make_context() -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    return ctx


@pytest.mark.asyncio
async def test_render_still_routes_through_router() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-1",
            provider_id="blender-bridge",
            capability_id="render.still",
            success=True,
            result={
                "output": "C:/renders/image.png",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await render_still(
            ctx,
            output_path="C:/renders/image.png",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "render.still"
    assert request.parameters == {
        "output_path": "C:/renders/image.png",
    }

    assert json.loads(result) == {
        "output": "C:/renders/image.png",
    }


@pytest.mark.asyncio
async def test_render_animation_routes_through_router() -> None:
    ctx = make_context()

    router = MagicMock()
    router.execute = AsyncMock(
        return_value=ProviderResult(
            request_id="request-2",
            provider_id="blender-bridge",
            capability_id="render.animation",
            success=True,
            result={
                "output": "C:/renders/movie.mp4",
            },
        )
    )

    with patch(
        "blender_mcp_server.server._get_router",
        return_value=router,
    ):
        result = await render_animation(
            ctx,
            output_path="C:/renders/movie.mp4",
        )

    request = router.execute.await_args.args[0]

    assert request.capability_id == "render.animation"
    assert request.parameters == {
        "output_path": "C:/renders/movie.mp4",
    }

    assert json.loads(result) == {
        "output": "C:/renders/movie.mp4",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function", "capability_id", "kwargs"),
    [
        (
            render_still,
            "render.still",
            {
                "output_path": "image.png",
            },
        ),
        (
            render_animation,
            "render.animation",
            {
                "output_path": "movie.mp4",
            },
        ),
    ],
)
async def test_render_tools_raise_for_provider_failure(
    function: RenderFunction,
    capability_id: str,
    kwargs: dict[str, Any],
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
        await function(
            ctx,
            **kwargs,
        )

"""
Asynchronous utilities for the SDK
"""

import asyncio
from typing import Any, Awaitable, Callable, Optional, TypeVar

T = TypeVar("T")


async def sleep(ms: int) -> None:
    """
    Asynchronous sleep for the specified milliseconds

    Args:
        ms: Time to sleep in milliseconds
    """
    await asyncio.sleep(ms / 1000)  # Convert milliseconds to seconds


async def with_timeout(
    coro: Awaitable[T],
    timeout_ms: int,
    timeout_callback: Optional[Callable[[], Any]] = None,
) -> Optional[T]:
    """
    Run a coroutine with a timeout

    Args:
        coro: Coroutine to run
        timeout_ms: Timeout in milliseconds
        timeout_callback: Optional callback to run on timeout

    Returns:
        The result of the coroutine, or None if timed out
    """
    try:
        return await asyncio.wait_for(coro, timeout_ms / 1000)
    except asyncio.TimeoutError:
        if timeout_callback:
            timeout_callback()
        return None

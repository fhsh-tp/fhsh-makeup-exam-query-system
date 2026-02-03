"""
Async Utils - 同步函式非同步化工具

提供 @to_async 裝飾器，將同步函式轉換為非同步函式，
在 Thread Pool 中執行以避免阻塞事件迴圈。
"""
from functools import partial, wraps
from typing import Awaitable, Callable, TypeVar

import anyio

T = TypeVar("T")


def to_async(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    """
    將同步函式轉換為非同步函式。

    使用 anyio.to_thread.run_sync 在 Thread Pool 中執行同步函式，
    避免阻塞 asyncio 事件迴圈。

    Args:
        func: 要轉換的同步函式

    Returns:
        非同步版本的函式

    Example:
        >>> @to_async
        >>> def sync_heavy_task(data):
        >>>     # 執行 CPU 密集或 I/O 阻塞操作
        >>>     return process(data)
        >>>
        >>> # 現在可以 await 呼叫
        >>> result = await sync_heavy_task(data)
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        return await anyio.to_thread.run_sync(
            partial(func, *args, **kwargs)
        )
    return wrapper

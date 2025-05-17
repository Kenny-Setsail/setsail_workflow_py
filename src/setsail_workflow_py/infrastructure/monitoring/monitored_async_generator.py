from typing import AsyncGenerator, TypeVar, Callable, Awaitable, Generic, Optional
import asyncio

_T = TypeVar("_T")

class MonitoredAsyncGenerator(Generic[_T]):
    def __init__(
            self,
            agen: AsyncGenerator[_T, None],
            on_close: Callable[[Optional[_T]], Awaitable[None]] | None = None,
    ):
        self._agen = agen
        self._on_close = on_close
        self._last_value: Optional[_T] = None
        self._finalized = False
        self._lock = asyncio.Lock()

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = await self._agen.__anext__()
            self._last_value = value
            return value
        except StopAsyncIteration:
            await self._finalize_once()
            raise
        except Exception:
            await self._finalize_once()
            raise

    async def _finalize_once(self):
        async with self._lock:
            if not self._finalized:
                self._finalized = True
                if self._on_close:
                    await self._on_close(self._last_value)

import asyncio
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import final

from payment_processing.presentation.outbox_worker.worker import (
    OutboxWorker,
)


@final
@dataclass(slots=True, frozen=True)
class OutboxApplication:
    worker: OutboxWorker
    lifespan: Callable[[], AbstractAsyncContextManager[None]]

    async def run(self, *, stop_event: asyncio.Event) -> None:
        async with self.lifespan():
            await self.worker.run(stop_event=stop_event)

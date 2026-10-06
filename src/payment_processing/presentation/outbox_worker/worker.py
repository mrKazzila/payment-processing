import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import final

import structlog
from sqlalchemy.exc import (
    OperationalError,
    TimeoutError as SQLAlchemyTimeoutError,
)

from payment_processing.application.exceptions import MessagePublishError

logger = structlog.get_logger(__name__)


@final
@dataclass(slots=True, frozen=True)
class OutboxWorker:
    publish_once: Callable[[], Awaitable[bool]]
    poll_interval: float
    error_delay: float
    iteration_timeout: float

    async def run(self, *, stop_event: asyncio.Event) -> None:
        while not stop_event.is_set():
            try:
                async with asyncio.timeout(self.iteration_timeout):
                    published = await self.publish_once()

            except (
                MessagePublishError,
                OperationalError,
                SQLAlchemyTimeoutError,
                TimeoutError,
            ):
                logger.exception("outbox_iteration_failed")
                delay = self.error_delay

            else:
                if published:
                    logger.debug("outbox_message_published")
                    await asyncio.sleep(0)
                    continue

                delay = self.poll_interval

            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=delay,
                )
            except TimeoutError:
                pass

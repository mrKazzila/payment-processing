import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import final
from uuid import UUID

import structlog
from faststream.rabbit.message import RabbitMessage
from pydantic import ValidationError

from payment_processing.presentation.payment_worker.payments.schemas import (
    PaymentCreatedMessage,
)
from payment_processing.presentation.payment_worker.retry.policy import (
    get_retry_delay,
    validate_attempt,
)
from payment_processing.presentation.payment_worker.retry.ports import (
    RetryPublisher,
)

logger = structlog.get_logger(__name__)


@final
@dataclass(slots=True, frozen=True)
class PaymentMessageHandler:
    process_payment: Callable[[UUID], Awaitable[None]]
    retry_publisher: RetryPublisher
    processing_attempt_header: str
    processing_timeout: float = 30.0
    forwarding_error_delay: float = 1.0

    async def handle(self, *, message: RabbitMessage) -> None:
        # Any delivery failure must
        # result in the message being returned to the queue.

        # noinspection PyBroadException
        try:
            await self._handle(message=message)
        except Exception:
            logger.exception(
                "payment_message_delivery_failed",
                message_id=message.message_id,
            )

            await asyncio.sleep(self.forwarding_error_delay)
            await message.nack(requeue=True)

    async def _handle(self, *, message: RabbitMessage) -> None:
        attempt = 1

        try:
            attempt = validate_attempt(
                value=message.headers.get(
                    self.processing_attempt_header,
                    1,
                ),
            )
            payload = PaymentCreatedMessage.model_validate_json(
                message.raw_message.body,
            )

        except (ValueError, ValidationError) as exc:
            logger.warning(
                "payment_message_invalid",
                message_id=message.message_id,
                error_type=type(exc).__name__,
            )

            await self.retry_publisher.publish_dead_letter(
                message=message,
                failed_attempt=attempt,
            )
            await message.ack()
            return

        # Any processing error is counted as a failed attempt.
        # noinspection PyBroadException
        try:
            async with asyncio.timeout(self.processing_timeout):
                await self.process_payment(payload.payment_id)
        except Exception:
            logger.exception(
                "payment_processing_attempt_failed",
                payment_id=str(payload.payment_id),
                attempt=attempt,
            )

            delay = get_retry_delay(failed_attempt=attempt)

            if delay is None:
                await self.retry_publisher.publish_dead_letter(
                    message=message,
                    failed_attempt=attempt,
                )
            else:
                await self.retry_publisher.publish_retry(
                    message=message,
                    next_attempt=attempt + 1,
                    delay_seconds=delay,
                )

            await message.ack()
            return

        await message.ack()

        logger.info(
            "payment_message_processed",
            payment_id=str(payload.payment_id),
            attempt=attempt,
        )

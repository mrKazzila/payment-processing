import asyncio
from dataclasses import dataclass
from typing import final

from aio_pika.exceptions import AMQPException
from faststream.rabbit import RabbitBroker
from faststream.rabbit.message import RabbitMessage

from payment_processing.application.exceptions import MessagePublishError
from payment_processing.infrastructure.messaging.topology import (
    PAYMENTS_DLQ,
    PAYMENTS_DLX,
    PAYMENTS_RETRY_QUEUES,
)

PROCESSING_ATTEMPT_HEADER = "x-processing-attempt"


@final
@dataclass(slots=True, frozen=True)
class RabbitRetryPublisher:
    broker: RabbitBroker
    publish_timeout: float = 5.0

    async def publish_retry(
        self,
        *,
        message: RabbitMessage,
        next_attempt: int,
        delay_seconds: float,
    ) -> None:
        queue = PAYMENTS_RETRY_QUEUES[delay_seconds]

        await self._publish(
            message=message,
            attempt=next_attempt,
            exchange="",
            routing_key=queue.name,
        )

    async def publish_dead_letter(
        self,
        *,
        message: RabbitMessage,
        failed_attempt: int,
    ) -> None:
        await self._publish(
            message=message,
            attempt=failed_attempt,
            exchange=PAYMENTS_DLX.name,
            routing_key=PAYMENTS_DLQ.routing_key,
        )

    async def _publish(
        self,
        *,
        message: RabbitMessage,
        attempt: int,
        exchange: str,
        routing_key: str,
    ) -> None:
        raw_message = message.raw_message

        headers = dict(raw_message.headers)
        headers[PROCESSING_ATTEMPT_HEADER] = attempt

        try:
            async with asyncio.timeout(self.publish_timeout):
                confirmation = await self.broker.publish(
                    message=raw_message.body,
                    exchange=exchange,
                    routing_key=routing_key,
                    headers=headers,
                    content_type=raw_message.content_type,
                    content_encoding=raw_message.content_encoding,
                    message_id=raw_message.message_id,
                    correlation_id=raw_message.correlation_id,
                    timestamp=raw_message.timestamp,
                    mandatory=True,
                    persist=True,
                    timeout=self.publish_timeout,
                )

        except (AMQPException, OSError, TimeoutError) as exc:
            raise MessagePublishError(
                f"Failed to forward payment message {raw_message.message_id}."
            ) from exc

        if not confirmation:
            raise MessagePublishError(
                "No confirmation while forwarding payment message "
                f"{raw_message.message_id}."
            )

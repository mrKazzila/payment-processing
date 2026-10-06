import asyncio
from dataclasses import dataclass
from typing import final

from aio_pika.exceptions import AMQPException
from faststream.rabbit import RabbitBroker

from payment_processing.application.dtos.outbox import OutboxMessage
from payment_processing.application.exceptions import MessagePublishError


@final
@dataclass(slots=True, frozen=True)
class RabbitMessagePublisher:
    broker: RabbitBroker
    publish_timeout: float = 5.0

    async def publish(self, *, message: OutboxMessage) -> None:
        try:
            async with asyncio.timeout(self.publish_timeout):
                confirmation = await self.broker.publish(
                    message=message.payload,
                    routing_key=message.routing_key,
                    exchange="",
                    mandatory=True,
                    persist=True,
                    message_id=str(message.id),
                    timestamp=message.created_at,
                    timeout=self.publish_timeout,
                )

        except (AMQPException, OSError, TimeoutError) as exc:
            raise MessagePublishError(
                f"Failed to publish outbox message {message.id}."
            ) from exc

        if not confirmation:
            raise MessagePublishError(
                f"No publisher confirmation for message {message.id}."
            )

from typing import Protocol

from payment_processing.application.dtos.outbox import OutboxMessage


class MessagePublisher(Protocol):
    async def publish(self, *, message: OutboxMessage) -> None: ...

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final

from payment_processing.application.ports.outbox import (
    OutboxRepository,
)
from payment_processing.application.ports.publisher import (
    MessagePublisher,
)
from payment_processing.application.ports.transactions import (
    TransactionManager,
)


@final
@dataclass(slots=True, frozen=True)
class PublishOutboxMessage:
    outbox: OutboxRepository
    publisher: MessagePublisher
    transactions: TransactionManager

    async def execute(self) -> bool:
        async with self.transactions.begin():
            message = await self.outbox.get_next_for_update()

            if message is None:
                return False

            await self.publisher.publish(message=message)

            await self.outbox.mark_published(
                message_id=message.id,
                published_at=datetime.now(UTC),
            )

        return True

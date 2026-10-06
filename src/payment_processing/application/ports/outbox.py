from datetime import datetime
from typing import Protocol
from uuid import UUID

from payment_processing.application.dtos.outbox import OutboxMessage


class OutboxRepository(Protocol):
    async def add_payment_created(
        self,
        *,
        payment_id: UUID,
        occurred_at: datetime,
    ) -> None: ...

    async def get_next_for_update(self) -> OutboxMessage | None: ...

    async def mark_published(
        self,
        *,
        message_id: UUID,
        published_at: datetime,
    ) -> None: ...

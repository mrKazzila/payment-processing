from dataclasses import dataclass
from datetime import datetime
from typing import final
from uuid import UUID, uuid4

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from payment_processing.application.dtos.outbox import OutboxMessage
from payment_processing.infrastructure.database.mappers.outbox import (
    outbox_to_message,
)
from payment_processing.infrastructure.database.models.outbox import (
    OutboxModel,
)


@final
@dataclass(slots=True, frozen=True)
class SQLAlchemyOutboxRepository:
    session: AsyncSession

    async def add_payment_created(
        self,
        *,
        payment_id: UUID,
        occurred_at: datetime,
    ) -> None:
        statement = insert(OutboxModel).values(
            id=uuid4(),
            routing_key="payments.new",
            payload={"payment_id": str(payment_id)},
            created_at=occurred_at,
            published_at=None,
        )

        await self.session.execute(statement)

    async def get_next_for_update(self) -> OutboxMessage | None:
        statement = (
            select(OutboxModel)
            .where(OutboxModel.published_at.is_(None))
            .order_by(OutboxModel.created_at, OutboxModel.id)
            .limit(1)
            .with_for_update(skip_locked=True)
            .execution_options(populate_existing=True)
        )

        model: OutboxModel | None = await self.session.scalar(statement)
        if model is None:
            return None

        return outbox_to_message(model=model)

    async def mark_published(
        self,
        *,
        message_id: UUID,
        published_at: datetime,
    ) -> None:
        statement = (
            update(OutboxModel)
            .where(
                OutboxModel.id == message_id,
                OutboxModel.published_at.is_(None),
            )
            .values(published_at=published_at)
            .returning(OutboxModel.id)
            .execution_options(synchronize_session="fetch")
        )

        updated_id = await self.session.scalar(statement)

        if updated_id is None:
            raise RuntimeError(
                f"Outbox message {message_id} is missing or already published."
            )

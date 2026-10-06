from dataclasses import dataclass
from typing import final
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from payment_processing.application.exceptions import (
    DuplicateIdempotencyKeyError,
    PaymentNotFoundError,
)
from payment_processing.domain.payment import Payment
from payment_processing.infrastructure.database.mappers.payments import (
    payment_to_domain,
)
from payment_processing.infrastructure.database.models.payment import (
    PAYMENT_IDEMPOTENCY_CONSTRAINT,
    PaymentModel,
)


@final
@dataclass(slots=True, frozen=True)
class SQLAlchemyPaymentRepository:
    session: AsyncSession

    async def get_by_id(self, *, payment_id: UUID) -> Payment | None:
        statement = select(PaymentModel).where(
            PaymentModel.id == payment_id,
        )

        model: PaymentModel | None = await self.session.scalar(statement)
        if model is None:
            return None

        return payment_to_domain(model=model)

    async def get_by_idempotency_key(
        self,
        *,
        idempotency_key: str,
    ) -> Payment | None:
        statement = select(PaymentModel).where(
            PaymentModel.idempotency_key == idempotency_key,
        )

        model: PaymentModel | None = await self.session.scalar(statement)
        if model is None:
            return None

        return payment_to_domain(model=model)

    async def get_by_id_for_update(
        self,
        *,
        payment_id: UUID,
    ) -> Payment | None:
        statement = (
            select(PaymentModel)
            .where(PaymentModel.id == payment_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

        model: PaymentModel | None = await self.session.scalar(statement)
        if model is None:
            return None

        return payment_to_domain(model=model)

    async def add(self, *, payment: Payment) -> None:
        statement = (
            insert(PaymentModel)
            .values(
                id=payment.id,
                amount=payment.amount,
                currency=payment.currency.value,
                description=payment.description,
                metadata_json=payment.metadata,
                idempotency_key=payment.idempotency_key,
                webhook_url=payment.webhook_url,
                status=payment.status.value,
                created_at=payment.created_at,
                processed_at=payment.processed_at,
            )
            .on_conflict_do_nothing(
                constraint=PAYMENT_IDEMPOTENCY_CONSTRAINT,
            )
            .returning(PaymentModel.id)
        )

        inserted_id = await self.session.scalar(statement)

        if inserted_id is None:
            raise DuplicateIdempotencyKeyError()

    async def update(self, *, payment: Payment) -> None:
        statement = (
            update(PaymentModel)
            .where(PaymentModel.id == payment.id)
            .values(
                status=payment.status.value,
                processed_at=payment.processed_at,
            )
            .returning(PaymentModel.id)
            .execution_options(synchronize_session="fetch")
        )

        updated_id = await self.session.scalar(statement)

        if updated_id is None:
            raise PaymentNotFoundError(payment_id=payment.id)

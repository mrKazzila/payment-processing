import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final
from uuid import uuid4

from payment_processing.application.dtos.payments import (
    CreatePaymentCommand,
)
from payment_processing.application.exceptions import (
    DuplicateIdempotencyKeyError,
    IdempotencyConflictError,
)
from payment_processing.application.ports.outbox import (
    OutboxRepository,
)
from payment_processing.application.ports.payments import (
    PaymentRepository,
)
from payment_processing.application.ports.transactions import (
    TransactionManager,
)
from payment_processing.domain.payment import Payment
from payment_processing.domain.types import JsonValue


def canonical_metadata(*, value: JsonValue) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def ensure_same_request(
    *,
    existing: Payment,
    requested: Payment,
) -> Payment:
    same_request = (
        existing.amount == requested.amount
        and existing.currency == requested.currency
        and existing.description == requested.description
        and existing.webhook_url == requested.webhook_url
        and canonical_metadata(value=existing.metadata)
        == canonical_metadata(value=requested.metadata)
    )

    if not same_request:
        raise IdempotencyConflictError()

    return existing


@final
@dataclass(slots=True, frozen=True)
class CreatePayment:
    payments: PaymentRepository
    outbox: OutboxRepository
    transactions: TransactionManager

    async def execute(self, *, command: CreatePaymentCommand) -> Payment:
        payment = Payment(
            id=uuid4(),
            amount=command.amount,
            currency=command.currency,
            description=command.description,
            metadata=command.metadata,
            idempotency_key=command.idempotency_key,
            webhook_url=command.webhook_url,
            created_at=datetime.now(UTC),
        )

        try:
            async with self.transactions.begin():
                existing = await self.payments.get_by_idempotency_key(
                    idempotency_key=payment.idempotency_key,
                )

                if existing is not None:
                    return ensure_same_request(
                        existing=existing,
                        requested=payment,
                    )

                await self.payments.add(payment=payment)
                await self.outbox.add_payment_created(
                    payment_id=payment.id,
                    occurred_at=payment.created_at,
                )

        except DuplicateIdempotencyKeyError:
            async with self.transactions.begin():
                existing = await self.payments.get_by_idempotency_key(
                    idempotency_key=payment.idempotency_key,
                )

                if existing is None:
                    raise

                return ensure_same_request(
                    existing=existing,
                    requested=payment,
                )

        return payment

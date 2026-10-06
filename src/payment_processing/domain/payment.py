from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import ROUND_DOWN, Decimal, localcontext
from uuid import UUID

from payment_processing.domain.enums import Currency, PaymentStatus
from payment_processing.domain.exceptions import (
    InvalidPaymentAmountError,
    InvalidPaymentStateError,
)
from payment_processing.domain.types import JsonValue

AMOUNT_QUANTUM = Decimal("0.01")
MAX_PAYMENT_AMOUNT = Decimal("9999999999999999.99")


def validate_amount(*, amount: Decimal) -> Decimal:
    if not isinstance(amount, Decimal):
        raise InvalidPaymentAmountError("Amount must be a Decimal.")

    if not amount.is_finite():
        raise InvalidPaymentAmountError("Amount must be finite.")

    if not Decimal("0") < amount <= MAX_PAYMENT_AMOUNT:
        raise InvalidPaymentAmountError(
            f"Amount must be positive and at most {MAX_PAYMENT_AMOUNT}."
        )

    with localcontext() as context:
        context.prec = 18
        normalized = amount.quantize(
            AMOUNT_QUANTUM,
            rounding=ROUND_DOWN,
        )

    if normalized != amount:
        raise InvalidPaymentAmountError(
            "Amount must have at most two decimal places."
        )

    return normalized


def validate_timestamp(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidPaymentStateError(
            f"{field_name} must include a timezone."
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Payment:
    id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: JsonValue
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    status: PaymentStatus = PaymentStatus.PENDING
    processed_at: datetime | None = None

    def __post_init__(self) -> None:
        normalized_amount = validate_amount(amount=self.amount)
        object.__setattr__(self, "amount", normalized_amount)

        if not isinstance(self.currency, Currency):
            raise InvalidPaymentStateError("Invalid payment currency.")

        if not isinstance(self.status, PaymentStatus):
            raise InvalidPaymentStateError("Invalid payment status.")

        validate_timestamp(self.created_at, field_name="created_at")

        if self.status is PaymentStatus.PENDING:
            if self.processed_at is not None:
                raise InvalidPaymentStateError(
                    "Pending payment cannot have processed_at."
                )
            return

        if self.processed_at is None:
            raise InvalidPaymentStateError(
                "Completed payment must have processed_at."
            )

        validate_timestamp(self.processed_at, field_name="processed_at")

        if self.processed_at < self.created_at:
            raise InvalidPaymentStateError(
                "processed_at cannot precede created_at."
            )

    def succeed(self, *, processed_at: datetime) -> Payment:
        return self._complete(
            status=PaymentStatus.SUCCEEDED,
            processed_at=processed_at,
        )

    def fail(self, *, processed_at: datetime) -> Payment:
        return self._complete(
            status=PaymentStatus.FAILED,
            processed_at=processed_at,
        )

    def _complete(
        self,
        *,
        status: PaymentStatus,
        processed_at: datetime,
    ) -> Payment:
        if self.status is not PaymentStatus.PENDING:
            raise InvalidPaymentStateError(
                f"Cannot complete payment in status {self.status.value}."
            )

        return replace(
            self,
            status=status,
            processed_at=processed_at,
        )

from dataclasses import dataclass
from typing import final
from uuid import UUID

from payment_processing.application.exceptions import (
    PaymentNotFoundError,
)
from payment_processing.application.ports.payments import (
    PaymentRepository,
)
from payment_processing.domain.payment import Payment


@final
@dataclass(slots=True, frozen=True)
class GetPayment:
    payments: PaymentRepository

    async def execute(self, *, payment_id: UUID) -> Payment:
        payment = await self.payments.get_by_id(
            payment_id=payment_id,
        )

        if payment is None:
            raise PaymentNotFoundError(payment_id=payment_id)

        return payment

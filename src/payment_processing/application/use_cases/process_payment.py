from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final
from uuid import UUID

from payment_processing.application.exceptions import (
    PaymentNotFoundError,
)
from payment_processing.application.ports.payment_gateway import (
    PaymentGateway,
)
from payment_processing.application.ports.payments import (
    PaymentRepository,
)
from payment_processing.application.ports.transactions import (
    TransactionManager,
)
from payment_processing.application.ports.webhooks import (
    WebhookSender,
)
from payment_processing.domain.enums import PaymentStatus


@final
@dataclass(slots=True, frozen=True)
class ProcessPayment:
    payments: PaymentRepository
    gateway: PaymentGateway
    webhooks: WebhookSender
    transactions: TransactionManager

    async def execute(self, *, payment_id: UUID) -> None:
        async with self.transactions.begin():
            payment = await self.payments.get_by_id_for_update(
                payment_id=payment_id,
            )

            if payment is None:
                raise PaymentNotFoundError(payment_id=payment_id)

            if payment.status is PaymentStatus.PENDING:
                succeeded = await self.gateway.charge(
                    payment=payment,
                )
                processed_at = datetime.now(UTC)

                if succeeded:
                    payment = payment.succeed(
                        processed_at=processed_at,
                    )
                else:
                    payment = payment.fail(
                        processed_at=processed_at,
                    )

                await self.payments.update(payment=payment)

        await self.webhooks.send_payment_result(payment=payment)

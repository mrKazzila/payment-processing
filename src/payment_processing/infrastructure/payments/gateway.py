import asyncio
import random
from typing import final

from payment_processing.domain.enums import PaymentStatus
from payment_processing.domain.exceptions import (
    InvalidPaymentStateError,
)
from payment_processing.domain.payment import Payment


@final
class SimulatedPaymentGateway:
    async def charge(self, *, payment: Payment) -> bool:
        if payment.status is not PaymentStatus.PENDING:
            raise InvalidPaymentStateError(
                "Only pending payments can be charged."
            )

        await asyncio.sleep(random.uniform(2.0, 5.0))

        return random.random() < 0.9

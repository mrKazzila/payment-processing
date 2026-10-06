from typing import Protocol

from payment_processing.domain.payment import Payment


class PaymentGateway(Protocol):
    async def charge(self, *, payment: Payment) -> bool: ...

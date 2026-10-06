from typing import Protocol

from payment_processing.domain.payment import Payment


class WebhookSender(Protocol):
    async def send_payment_result(self, *, payment: Payment) -> None: ...

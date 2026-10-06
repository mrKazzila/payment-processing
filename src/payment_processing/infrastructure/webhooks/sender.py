import asyncio
from dataclasses import dataclass
from typing import final

import httpx

from payment_processing.application.exceptions import (
    WebhookDeliveryError,
)
from payment_processing.domain.enums import PaymentStatus
from payment_processing.domain.exceptions import (
    InvalidPaymentStateError,
)
from payment_processing.domain.payment import Payment


@final
@dataclass(slots=True, frozen=True)
class HTTPXWebhookSender:
    client: httpx.AsyncClient
    delivery_timeout: float = 10.0

    async def send_payment_result(self, *, payment: Payment) -> None:
        if (
            payment.status is PaymentStatus.PENDING
            or payment.processed_at is None
        ):
            raise InvalidPaymentStateError(
                "Cannot send a webhook for an unfinished payment."
            )

        payload = {
            "payment_id": str(payment.id),
            "status": payment.status.value,
            "processed_at": payment.processed_at.isoformat(),
        }

        try:
            async with asyncio.timeout(self.delivery_timeout):
                async with self.client.stream(
                    method="POST",
                    url=payment.webhook_url,
                    json=payload,
                    follow_redirects=False,
                ) as response:
                    response.raise_for_status()

        except (httpx.HTTPError, TimeoutError) as exc:
            raise WebhookDeliveryError(
                f"Webhook delivery failed for payment {payment.id}."
            ) from exc

from copy import deepcopy

from payment_processing.domain.enums import Currency, PaymentStatus
from payment_processing.domain.payment import Payment
from payment_processing.infrastructure.database.models.payment import (
    PaymentModel,
)


def payment_to_domain(*, model: PaymentModel) -> Payment:
    return Payment(
        id=model.id,
        amount=model.amount,
        currency=Currency(model.currency),
        description=model.description,
        metadata=deepcopy(model.metadata_json),
        idempotency_key=model.idempotency_key,
        webhook_url=model.webhook_url,
        status=PaymentStatus(model.status),
        created_at=model.created_at,
        processed_at=model.processed_at,
    )

from copy import deepcopy

from payment_processing.application.dtos.payments import (
    CreatePaymentCommand,
)
from payment_processing.domain.payment import Payment
from payment_processing.presentation.api.endpoints.payments.schemas import (
    SCreatePaymentRequest,
    SCreatePaymentResponse,
    SPaymentResponse,
)


def to_create_payment_command(
    *,
    request: SCreatePaymentRequest,
    idempotency_key: str,
) -> CreatePaymentCommand:
    return CreatePaymentCommand(
        amount=request.amount,
        currency=request.currency,
        description=request.description,
        metadata=deepcopy(request.metadata),
        idempotency_key=idempotency_key,
        webhook_url=str(request.webhook_url),
    )


def to_create_payment_response(
    *,
    payment: Payment,
) -> SCreatePaymentResponse:
    return SCreatePaymentResponse(
        payment_id=payment.id,
        status=payment.status,
        created_at=payment.created_at,
    )


def to_payment_response(*, payment: Payment) -> SPaymentResponse:
    return SPaymentResponse(
        payment_id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        metadata=deepcopy(payment.metadata),
        status=payment.status,
        idempotency_key=payment.idempotency_key,
        webhook_url=payment.webhook_url,
        created_at=payment.created_at,
        processed_at=payment.processed_at,
    )

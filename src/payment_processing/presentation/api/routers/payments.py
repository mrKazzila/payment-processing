from typing import Annotated
from uuid import UUID

from dishka import FromComponent
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Header, status

from payment_processing.application.use_cases.create_payment import (
    CreatePayment,
)
from payment_processing.application.use_cases.get_payment import GetPayment
from payment_processing.presentation.api.mappers.payments import (
    to_create_payment_command,
    to_create_payment_response,
    to_payment_response,
)
from payment_processing.presentation.api.schemas.payments import (
    SCreatePaymentRequest,
    SCreatePaymentResponse,
    SPaymentResponse,
)

router = APIRouter(
    prefix="/api/v1/payments",
    tags=["Payments"],
    route_class=DishkaRoute,
)
IdempotencyKeyHeader = Annotated[
    str,
    Header(
        alias="Idempotency-Key",
        min_length=1,
        pattern=r"\S",
    ),
]


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=SCreatePaymentResponse,
)
async def create_payment(
    body: SCreatePaymentRequest,
    idempotency_key: IdempotencyKeyHeader,
    use_case: Annotated[CreatePayment, FromComponent()],
) -> SCreatePaymentResponse:
    command = to_create_payment_command(
        request=body,
        idempotency_key=idempotency_key,
    )
    payment = await use_case.execute(command=command)

    return to_create_payment_response(payment=payment)


@router.get(
    "/{payment_id}",
    response_model=SPaymentResponse,
)
async def get_payment(
    payment_id: UUID,
    use_case: Annotated[GetPayment, FromComponent()],
) -> SPaymentResponse:
    payment = await use_case.execute(payment_id=payment_id)

    return to_payment_response(payment=payment)

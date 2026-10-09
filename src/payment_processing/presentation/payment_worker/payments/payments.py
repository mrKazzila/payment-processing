from typing import Annotated

from dishka import FromComponent
from dishka_faststream import inject
from faststream import AckPolicy
from faststream.rabbit import RabbitQueue, RabbitRouter
from faststream.rabbit.annotations import (
    RabbitMessage as RabbitMessageContext,
)
from faststream.rabbit.message import RabbitMessage
from pydantic import SkipValidation

from payment_processing.presentation.payment_worker.payments.handler import (
    PaymentMessageHandler,
)
from payment_processing.presentation.payment_worker.payments.schemas import (
    PaymentCreatedMessage,
)


async def decode_raw(message: RabbitMessage) -> bytes:
    return message.raw_message.body


@inject
async def process_payment(
    payload: Annotated[PaymentCreatedMessage, SkipValidation],  # noqa: ARG001
    message: RabbitMessageContext,
    handler: Annotated[PaymentMessageHandler, FromComponent()],
) -> None:
    await handler.handle(message=message)


def create_router(*, queue: RabbitQueue) -> RabbitRouter:
    router = RabbitRouter()
    router.subscriber(
        queue,
        ack_policy=AckPolicy.MANUAL,
        decoder=decode_raw,
        no_reply=True,
        title="payments.new:Consume",
        description=(
            "Processes a payment and delivers a webhook. "
            "On failure, makes up to three attempts "
            "before sending the message to the dead-letter queue (DLQ)."
        ),
    )(process_payment)
    return router

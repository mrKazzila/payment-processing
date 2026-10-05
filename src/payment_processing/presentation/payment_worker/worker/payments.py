from faststream import AckPolicy
from faststream.rabbit import RabbitRouter

from payment_processing.infrastructure.messaging.topology import (
    PAYMENTS_QUEUE,
)
from payment_processing.presentation.payment_worker.schemas.payments import (
    PaymentCreatedMessage,
)

router = RabbitRouter()


@router.subscriber(
    PAYMENTS_QUEUE,
    ack_policy=AckPolicy.REJECT_ON_ERROR,
    title="payments.new:Consume",
    description=(
        "Принимает идентификатор платежа для асинхронной обработки. "
        "Сообщение должно соответствовать PaymentCreatedMessage. "
        "Обработка платежа пока не реализована."
    ),
)
async def process_payment(message: PaymentCreatedMessage) -> None:
    raise NotImplementedError("use case обработки платежа")

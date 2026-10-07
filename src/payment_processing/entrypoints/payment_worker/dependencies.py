from collections.abc import AsyncIterator
from uuid import UUID

from dishka import AsyncContainer, Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker
from httpx import AsyncClient

from payment_processing.application.ports.payment_gateway import (
    PaymentGateway,
)
from payment_processing.application.ports.webhooks import WebhookSender
from payment_processing.application.use_cases.process_payment import (
    ProcessPayment,
)
from payment_processing.infrastructure.messaging.retry_publisher import (
    PROCESSING_ATTEMPT_HEADER,
    RabbitRetryPublisher,
)
from payment_processing.infrastructure.payments.gateway import (
    SimulatedPaymentGateway,
)
from payment_processing.infrastructure.webhooks.client import (
    create_webhook_client,
)
from payment_processing.infrastructure.webhooks.sender import (
    HTTPXWebhookSender,
)
from payment_processing.presentation.payment_worker.payments.handler import (
    PaymentMessageHandler,
)


class PaymentWorkerProvider(Provider):
    broker = from_context(
        provides=RabbitBroker,
        scope=Scope.APP,
    )

    gateway = provide(
        SimulatedPaymentGateway,
        provides=PaymentGateway,
        scope=Scope.APP,
    )

    @provide(scope=Scope.APP)
    def webhooks(
        self,
        client: AsyncClient,
    ) -> WebhookSender:
        return HTTPXWebhookSender(client=client)

    @provide(scope=Scope.APP)
    def retry_publisher(
        self,
        broker: RabbitBroker,
    ) -> RabbitRetryPublisher:
        return RabbitRetryPublisher(broker=broker)

    process_payment = provide(
        ProcessPayment,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.APP)
    async def webhook_client(self) -> AsyncIterator[AsyncClient]:
        async with create_webhook_client() as client:
            yield client

    @provide(scope=Scope.REQUEST)
    def message_handler(
        self,
        container: AsyncContainer,
        retry_publisher: RabbitRetryPublisher,
    ) -> PaymentMessageHandler:
        async def process_payment(payment_id: UUID) -> None:
            use_case = await container.get(ProcessPayment)
            await use_case.execute(payment_id=payment_id)

        return PaymentMessageHandler(
            process_payment=process_payment,
            retry_publisher=retry_publisher,
            processing_attempt_header=PROCESSING_ATTEMPT_HEADER,
        )

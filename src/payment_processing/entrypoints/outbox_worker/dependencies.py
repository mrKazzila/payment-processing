from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker

from payment_processing.application.ports.publisher import MessagePublisher
from payment_processing.application.use_cases.publish_outbox_message import (
    PublishOutboxMessage,
)
from payment_processing.config.settings import Settings
from payment_processing.infrastructure.messaging.publisher import (
    RabbitMessagePublisher,
)


class OutboxProvider(Provider):
    broker = from_context(
        provides=RabbitBroker,
        scope=Scope.APP,
    )

    publish_message = provide(
        PublishOutboxMessage,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.APP)
    def publisher(
        self,
        broker: RabbitBroker,
        settings: Settings,
    ) -> MessagePublisher:
        return RabbitMessagePublisher(
            broker=broker,
            publish_timeout=settings.outbox.publish_timeout,
        )

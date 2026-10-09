import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import structlog
from dishka import AsyncContainer, make_async_container
from faststream.rabbit import Channel, RabbitBroker

from payment_processing.application.use_cases.publish_outbox_message import (
    PublishOutboxMessage,
)
from payment_processing.config.settings import Settings
from payment_processing.entrypoints.di.database import (
    DatabaseProvider,
    RepositoryProvider,
)
from payment_processing.entrypoints.outbox_worker.dependencies import (
    OutboxProvider,
)
from payment_processing.infrastructure.messaging.topology import (
    declare_topology,
)
from payment_processing.infrastructure.observability.logger_setup import (
    setup_logging,
)
from payment_processing.presentation.outbox_worker.application import (
    OutboxApplication,
)
from payment_processing.presentation.outbox_worker.worker import (
    OutboxWorker,
)

logger = structlog.get_logger(__name__)


def create_application(*, settings: Settings) -> OutboxApplication:
    logging_config = settings.outbox.logging.to_config()
    setup_logging(config=logging_config)

    broker = RabbitBroker(
        str(settings.outbox.rabbitmq_url),
        timeout=10.0,
        default_channel=Channel(
            publisher_confirms=True,
            on_return_raises=True,
        ),
        logger=logging.getLogger("payment_processing.outbox"),
        log_level=logging_config.resolved_level(),
    )

    container = make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        OutboxProvider(),
        context={
            Settings: settings,
            RabbitBroker: broker,
        },
    )

    async def publish_once() -> bool:
        async with container() as scope:
            use_case = await scope.get(PublishOutboxMessage)
            return await use_case.execute()

    worker = OutboxWorker(
        publish_once=publish_once,
        poll_interval=settings.outbox.poll_interval,
        error_delay=settings.outbox.error_delay,
        iteration_timeout=settings.outbox.iteration_timeout,
    )

    return OutboxApplication(
        worker=worker,
        lifespan=create_lifespan(
            broker=broker,
            container=container,
        ),
    )


def create_lifespan(
    *,
    broker: RabbitBroker,
    container: AsyncContainer,
) -> Callable[[], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan() -> AsyncIterator[None]:
        try:
            async with broker:
                await declare_topology(broker=broker)

                logger.info("outbox_worker_started")
                yield
        finally:
            await container.close()
            logger.info("outbox_worker_stopped")

    return lifespan

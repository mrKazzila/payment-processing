import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from dishka import make_async_container
from dishka_faststream import setup_dishka
from faststream import FastStream
from faststream.rabbit import Channel, RabbitBroker

from payment_processing.config.settings import Settings
from payment_processing.entrypoints.di.database import (
    DatabaseProvider,
    RepositoryProvider,
)
from payment_processing.entrypoints.payment_worker.dependencies import (
    PaymentWorkerProvider,
)
from payment_processing.infrastructure.messaging.topology import (
    PAYMENTS_QUEUE,
    declare_topology,
)
from payment_processing.infrastructure.observability.logger_setup import (
    setup_logging,
)
from payment_processing.presentation.payment_worker.application import (
    create_app as create_worker_app,
)
from payment_processing.presentation.payment_worker.middlewares import (
    MIDDLEWARES,
)
from payment_processing.presentation.payment_worker.worker.payments import (
    create_router,
)

logger = structlog.get_logger(__name__)


def create_application(*, settings: Settings) -> FastStream:
    logging_config = settings.worker.logging.to_config()
    setup_logging(config=logging_config)

    broker = RabbitBroker(
        str(settings.worker.rabbitmq_url),
        timeout=10.0,
        graceful_timeout=40.0,
        default_channel=Channel(
            prefetch_count=1,
            publisher_confirms=True,
            on_return_raises=True,
        ),
        specification_url=settings.worker.specification_url,
        logger=logging.getLogger("payment_processing.rabbitmq"),
        log_level=logging_config.resolved_level(),
        middlewares=[*MIDDLEWARES],
    )

    container = make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        PaymentWorkerProvider(),
        context={
            Settings: settings,
            RabbitBroker: broker,
        },
    )

    @asynccontextmanager
    async def lifespan() -> AsyncIterator[None]:
        try:
            yield
        finally:
            await container.close()
            logger.info("payment_worker_stopped")

    app = create_worker_app(
        broker=broker,
        router=create_router(queue=PAYMENTS_QUEUE),
        lifespan=lifespan,
        title=settings.worker.name,
        version=settings.app.version,
    )

    setup_dishka(
        container=container,
        broker=broker,
    )

    @app.on_startup
    async def on_starting() -> None:
        await broker.connect()
        await declare_topology(broker=broker)

    @app.after_startup
    async def on_started() -> None:
        logger.info("payment_worker_ready")

    return app

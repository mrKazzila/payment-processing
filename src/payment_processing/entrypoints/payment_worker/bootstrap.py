import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import structlog
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from payment_processing.config.logging import LoggingConfig
from payment_processing.config.settings import Settings
from payment_processing.infrastructure.messaging.topology import (
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

logger = structlog.get_logger(__name__)


def create_lifespan() -> Callable[[], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan() -> AsyncIterator[None]:
        try:
            yield
        finally:
            logger.info("payment_worker_stopped")

    return lifespan


def create_application(*, settings: Settings) -> FastStream:
    config = LoggingConfig(
        level=settings.worker.log_level,
        renderer=settings.worker.log_renderer,
        enable_diagnostics=settings.worker.enable_log_diagnostics,
        use_utc_timestamps=settings.worker.use_utc_timestamps,
    )
    setup_logging(config=config)

    broker = RabbitBroker(
        str(settings.worker.rabbitmq_url),
        specification_url=settings.worker.specification_url,
        description=(
            "RabbitMQ сервиса обработки платежей. "
            "В документации указан демонстрационный адрес."
        ),
        logger=logging.getLogger("payment_processing.rabbitmq"),
        log_level=config.resolved_level(),
        middlewares=[*MIDDLEWARES],
    )
    app = create_worker_app(
        broker=broker,
        lifespan=create_lifespan(),
        title=settings.worker.name,
        version=settings.app.version,
    )

    @app.on_startup
    async def on_starting() -> None:
        await broker.connect()
        await declare_topology(broker)

    @app.after_startup
    async def on_started() -> None:
        logger.info("payment_worker_ready")

    return app

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from starlette.types import Lifespan

from payment_processing.config.logging import LoggingConfig
from payment_processing.config.settings import Settings
from payment_processing.infrastructure.observability.logger_setup import (
    setup_logging,
)
from payment_processing.presentation.api.application import (
    create_app as create_http_app,
)

logger = structlog.getLogger(__name__)


def create_lifespan() -> Lifespan[FastAPI]:

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logger.info(
            "application_ready, app_version=%s",
            app.version,
        )

        yield

        logger.info("application_stopped")

    return lifespan


def create_application(
    *,
    settings: Settings,
) -> FastAPI:
    setup_logging(
        config=LoggingConfig(
            level=settings.app.log_level,
        ),
    )

    return create_http_app(
        title=settings.app.name,
        version=settings.app.version,
        debug=True,
        lifespan=create_lifespan(),
    )

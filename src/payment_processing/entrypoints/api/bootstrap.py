from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import structlog
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from payment_processing.config.settings import Settings
from payment_processing.entrypoints.api.dependencies import PaymentProvider
from payment_processing.entrypoints.di.database import (
    DatabaseProvider,
    RepositoryProvider,
)
from payment_processing.infrastructure.observability.logger_setup import (
    setup_logging,
)
from payment_processing.presentation.api.application import (
    create_app as create_http_app,
)

logger = structlog.getLogger(__name__)


def create_lifespan(
    *,
    container: AsyncContainer,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            logger.info(
                "application_ready",
                app_version=app.version,
            )
            yield
        finally:
            await container.close()
            logger.info("application_stopped")

    return lifespan


def create_application(
    *,
    settings: Settings,
) -> FastAPI:
    setup_logging(config=settings.app.logging.to_config())

    api_key = settings.app.api_key

    if api_key is None or not api_key.get_secret_value().strip():
        raise ValueError("PP_APP__API_KEY must be configured and non-blank")

    container = make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        PaymentProvider(),
        context={Settings: settings},
    )

    app = create_http_app(
        title=settings.app.name,
        version=settings.app.version,
        debug=settings.environment == "local",
        enable_docs=settings.environment == "local",
        lifespan=create_lifespan(container=container),
    )

    setup_dishka(container=container, app=app)

    return app

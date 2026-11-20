from collections.abc import Iterable

from dishka import AsyncContainer, Provider, make_async_container
from faststream.rabbit import RabbitBroker

from payment_processing.config.settings import Settings
from payment_processing.entrypoints.di.database import (
    DatabaseProvider,
    RepositoryProvider,
)


def create_container(
    *,
    settings: Settings,
    providers: Iterable[Provider],
    broker: RabbitBroker | None = None,
) -> AsyncContainer:
    context = {Settings: settings}

    if broker is not None:
        context[RabbitBroker] = broker

    return make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        *providers,
        context=context,
    )

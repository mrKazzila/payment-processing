import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitRouter

from payment_processing.presentation.payment_worker.specification import (
    create_specification,
)


def create_app(
    *,
    broker: RabbitBroker,
    router: RabbitRouter,
    lifespan: Callable[[], AbstractAsyncContextManager[None]],
    title: str,
    version: str,
) -> FastStream:
    broker.include_router(router)
    # noinspection PyTypeChecker
    return FastStream(
        broker,
        lifespan=lifespan,
        logger=logging.getLogger("payment_processing.payment_worker"),
        specification=create_specification(
            title=title,
            version=version,
        ),
    )

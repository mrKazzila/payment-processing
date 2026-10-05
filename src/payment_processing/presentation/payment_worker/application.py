import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from payment_processing.presentation.payment_worker.docs.docs import (
    create_specification,
)
from payment_processing.presentation.payment_worker.worker.payments import (
    router,
)


# noinspection PyTypeChecker
def create_app(
    *,
    broker: RabbitBroker,
    lifespan: Callable[[], AbstractAsyncContextManager[None]],
    title: str,
    version: str,
) -> FastStream:
    broker.include_router(router)

    return FastStream(
        broker,
        lifespan=lifespan,
        logger=logging.getLogger("payment_processing.payment_worker"),
        specification=create_specification(
            title=title,
            version=version,
        ),
    )

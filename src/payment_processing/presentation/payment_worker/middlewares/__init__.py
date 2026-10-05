from payment_processing.presentation.payment_worker.middlewares.exception_middleware import (  # noqa: E501
    create_exception_middleware,
)
from payment_processing.presentation.payment_worker.middlewares.logging_context_middleware import (  # noqa: E501
    MessageLoggingContextMiddleware,
)

MIDDLEWARES = (
    MessageLoggingContextMiddleware,
    create_exception_middleware(),
)

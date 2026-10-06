from payment_processing.presentation.payment_worker.middlewares.logging_context_middleware import (  # noqa: E501
    MessageLoggingContextMiddleware,
)

MIDDLEWARES = (MessageLoggingContextMiddleware,)

from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from faststream import BaseMiddleware, StreamMessage
from structlog.contextvars import bound_contextvars

logger = structlog.get_logger(__name__)


class MessageLoggingContextMiddleware(BaseMiddleware):
    async def consume_scope(
        self,
        call_next: Callable[[StreamMessage[Any]], Awaitable[Any]],
        msg: StreamMessage[Any],
    ) -> Any:
        log_context = self.context.get_local("log_context") or {}

        with bound_contextvars(
            message_id=msg.message_id,
            correlation_id=msg.correlation_id,
            queue=log_context.get("queue"),
            exchange=log_context.get("exchange"),
        ):
            return await call_next(msg)

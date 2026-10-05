from json import JSONDecodeError
from typing import Annotated, Any

import structlog
from faststream import Context, ExceptionMiddleware
from pydantic import ValidationError

logger = structlog.get_logger(__name__)


def create_exception_middleware() -> ExceptionMiddleware:
    middleware = ExceptionMiddleware()

    @middleware.add_handler(ValidationError)
    async def handle_validation_error(
        exc: ValidationError,
        message: Annotated[Any, Context("message")],
    ) -> None:
        logger.warning(
            "payment_message_validation_failed",
            message_id=message.message_id,
            correlation_id=message.correlation_id,
            errors=exc.errors(
                include_input=False,
                include_context=False,
                include_url=False,
            ),
        )
        await message.reject(requeue=False)

    @middleware.add_handler(JSONDecodeError)
    async def handle_json_error(
        exc: JSONDecodeError,
        message: Annotated[Any, Context("message")],
    ) -> None:
        logger.warning(
            "payment_message_json_invalid",
            message_id=message.message_id,
            correlation_id=message.correlation_id,
            position=exc.pos,
            reason=exc.msg,
        )
        await message.reject(requeue=False)

    return middleware

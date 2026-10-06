import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from payment_processing.application.exceptions import (
    IdempotencyConflictError,
    PaymentNotFoundError,
)

logger = structlog.get_logger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        PaymentNotFoundError,
        payment_not_found_handler,
    )
    app.add_exception_handler(
        IdempotencyConflictError,
        idempotency_conflict_handler,
    )
    app.add_exception_handler(
        Exception,
        unexpected_error_handler,
    )


async def payment_not_found_handler(
    _request: Request,
    _exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "code": "payment_not_found",
            "message": "Payment was not found.",
        },
    )


async def idempotency_conflict_handler(
    _request: Request,
    _exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "code": "idempotency_conflict",
            "message": (
                "Idempotency key was already used with different data."
            ),
        },
    )


async def unexpected_error_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "unhandled_request_error_type",
        error_type=type(exc).__name__,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "internal_error",
            "message": "Internal service error",
        },
    )

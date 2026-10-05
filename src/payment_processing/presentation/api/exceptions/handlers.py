import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:

    app.add_exception_handler(
        Exception,
        unexpected_error_handler,
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

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from fastapi import Depends, FastAPI

from payment_processing.presentation.api.endpoints import ROUTERS
from payment_processing.presentation.api.exception_handlers import (
    setup_exception_handlers,
)
from payment_processing.presentation.api.security import require_api_key
from payment_processing.presentation.api.specification import (
    API_DESCRIPTION,
    API_SUMMARY,
    OPENAPI_EXTERNAL_DOCS,
    OPENAPI_TAGS,
    SWAGGER_UI_PARAMETERS,
)


def create_app(
    *,
    title: str,
    version: str,
    debug: bool = False,
    enable_docs: bool = False,
    lifespan: Callable[[FastAPI], AbstractAsyncContextManager[None]],
) -> FastAPI:
    app = FastAPI(
        dependencies=[Depends(require_api_key)],
        title=title,
        version=version,
        debug=debug,
        summary=API_SUMMARY,
        description=API_DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
        openapi_external_docs=OPENAPI_EXTERNAL_DOCS,
        swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
        docs_url="/api/openapi" if enable_docs else None,
        redoc_url="/redoc" if enable_docs else None,
        openapi_url="/api/openapi.json" if enable_docs else None,
        lifespan=lifespan,
    )

    for router in ROUTERS:
        app.include_router(router)

    setup_exception_handlers(app)

    return app

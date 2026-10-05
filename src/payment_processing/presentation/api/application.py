from fastapi import FastAPI
from starlette.types import Lifespan

from payment_processing.presentation.api.docs.docs import (
    API_DESCRIPTION,
    API_SUMMARY,
    OPENAPI_EXTERNAL_DOCS,
    OPENAPI_TAGS,
    SWAGGER_UI_PARAMETERS,
)
from payment_processing.presentation.api.exceptions.handlers import (
    setup_exception_handlers,
)
from payment_processing.presentation.api.routers import ROUTERS


def create_app(
    *,
    title: str,
    version: str,
    debug: bool = False,
    lifespan: Lifespan[FastAPI],
) -> FastAPI:
    app = FastAPI(
        title=title,
        version=version,
        debug=debug,
        summary=API_SUMMARY,
        description=API_DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
        openapi_external_docs=OPENAPI_EXTERNAL_DOCS,
        swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
        docs_url="/api/openapi",
        redoc_url="/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    for router in ROUTERS:
        app.include_router(router)

    setup_exception_handlers(app)

    return app

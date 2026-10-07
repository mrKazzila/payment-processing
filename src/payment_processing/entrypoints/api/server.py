import uvicorn
from fastapi import FastAPI

from payment_processing.config.settings import AppServerSettings


def run_app(
    *,
    app: FastAPI,
    settings: AppServerSettings,
) -> None:
    uvicorn.run(
        app=app,
        host=settings.host,
        port=settings.port,
        loop=settings.loop,
        log_config=None,
        log_level=None,
        access_log=False,
    )

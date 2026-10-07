import uvicorn
from faststream import FastStream
from faststream.asgi import make_ping_asgi

from payment_processing.config.settings import WorkerServerSettings


def run_app(
    *,
    app: FastStream,
    settings: WorkerServerSettings,
) -> None:
    asgi_app = app.as_asgi(
        asgi_routes=[
            (
                "/health",
                make_ping_asgi(
                    app.brokers[0],
                    timeout=2.0,
                    include_in_schema=False,
                ),
            ),
        ],
    )

    uvicorn.run(
        app=asgi_app,
        host=settings.host,
        port=settings.port,
        lifespan=settings.lifespan,
        workers=settings.workers,
        loop=settings.loop,
        log_config=None,
        log_level=None,
        access_log=False,
    )

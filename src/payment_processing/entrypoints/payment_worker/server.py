import uvicorn
from faststream import FastStream
from faststream.asgi import make_ping_asgi


def run_app(
    *,
    app: FastStream,
    host: str,
    port: int,
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
        asgi_app,
        host=host,
        port=port,
        lifespan="on",
        workers=1,
        log_config=None,
        log_level=None,
        access_log=False,
    )

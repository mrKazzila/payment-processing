from typing import Literal

import uvicorn
from fastapi import FastAPI


def run_app(
    *,
    app: FastAPI,
    host: str,
    port: int,
    loop: Literal["none", "auto", "uvloop"] | str = "auto",
) -> None:
    uvicorn.run(
        app=app,
        host=host,
        port=port,
        loop=loop,
        log_config=None,
        log_level=None,
        access_log=False,
    )

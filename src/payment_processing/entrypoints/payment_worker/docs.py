import sys

from faststream import FastStream

from payment_processing.config.settings import get_settings
from payment_processing.entrypoints.payment_worker.bootstrap import (
    create_application,
)


def _ensure_docs_allowed() -> None:
    if get_settings().environment != "local":
        raise SystemExit(
            "Просмотр документации разрешён только при PP_ENVIRONMENT=local."
        )


def create_docs_app() -> FastStream:
    _ensure_docs_allowed()
    return create_application(settings=get_settings())


def main() -> None:
    _ensure_docs_allowed()

    from faststream.cli import cli

    cli(
        args=[
            "docs",
            "serve",
            (
                "payment_processing.entrypoints."
                "payment_worker.docs:create_docs_app"
            ),
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            "8081",
            *sys.argv[1:],
        ],
        prog_name="payment-processing-docs",
    )


if __name__ == "__main__":
    main()

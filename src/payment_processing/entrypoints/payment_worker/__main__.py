from payment_processing.config.settings import get_settings
from payment_processing.entrypoints.payment_worker.bootstrap import (
    create_application,
)
from payment_processing.entrypoints.payment_worker.server import run_app


def main() -> None:
    """Run payment worker application."""
    settings = get_settings()

    app = create_application(settings=settings)
    run_app(
        app=app,
        settings=settings.worker.server,
    )


if __name__ == "__main__":
    main()

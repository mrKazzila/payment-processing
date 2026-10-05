from payment_processing.config.settings import get_settings
from payment_processing.entrypoints.api.bootstrap import create_application
from payment_processing.entrypoints.api.server import run_app


def main() -> None:
    """Run API application."""
    settings = get_settings()
    app = create_application(settings=settings)

    run_app(
        app=app,
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    main()

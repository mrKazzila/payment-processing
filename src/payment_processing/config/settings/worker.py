__all__ = ("WorkerSettings",)

from pydantic import AmqpDsn, BaseModel

from payment_processing.config.logging import LogLevel, LogRenderer


class WorkerSettings(BaseModel):
    """Worker settings."""

    name: str = "Payment Processing Worker"
    specification_url: str = "amqp://rabbitmq.example.com:5672/"
    rabbitmq_url: AmqpDsn = AmqpDsn("amqp://guest:guest@localhost:5672/")

    host: str = "127.0.0.1"
    port: int = 8001

    log_level: LogLevel = "INFO"
    log_renderer: LogRenderer = "console"
    use_utc_timestamps: bool = True
    enable_log_diagnostics: bool = False

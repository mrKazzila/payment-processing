from pydantic import AmqpDsn, BaseModel, Field

from payment_processing.infrastructure.observability.config import (
    LogLevel,
    LogRenderer,
)


class OutboxSettings(BaseModel):
    rabbitmq_url: AmqpDsn = AmqpDsn("amqp://guest:guest@localhost:5672/")

    poll_interval: float = Field(default=1.0, gt=0)
    error_delay: float = Field(default=3.0, gt=0)
    publish_timeout: float = Field(default=5.0, gt=0)
    iteration_timeout: float = Field(default=15.0, gt=0)

    log_level: LogLevel = "INFO"
    log_renderer: LogRenderer = "console"
    use_utc_timestamps: bool = True
    enable_log_diagnostics: bool = False

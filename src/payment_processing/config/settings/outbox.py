from pydantic import AmqpDsn, BaseModel, Field

from payment_processing.config.settings.logging import LoggingSettings

__all__ = ("OutboxSettings",)


class OutboxSettings(BaseModel):
    rabbitmq_url: AmqpDsn = AmqpDsn("amqp://guest:guest@localhost:5672/")

    poll_interval: float = Field(default=1.0, gt=0)
    error_delay: float = Field(default=3.0, gt=0)
    publish_timeout: float = Field(default=5.0, gt=0)
    iteration_timeout: float = Field(default=15.0, gt=0)

    logging: LoggingSettings = LoggingSettings()

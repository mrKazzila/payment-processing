from typing import Literal

from pydantic import AmqpDsn, BaseModel, Field

from payment_processing.config.settings.logging import LoggingSettings

__all__ = ("WorkerSettings", "WorkerServerSettings")


class WorkerServerSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8001

    lifespan: Literal["auto", "on", "off"] = "on"
    loop: Literal["none", "auto", "uvloop"] | str = "auto"
    workers: int = Field(default=1, ge=1, le=10)


class WorkerSettings(BaseModel):
    """Worker settings."""

    name: str = "Payment Processing Worker"
    specification_url: str = "amqp://rabbitmq.example.com:5672/"
    rabbitmq_url: AmqpDsn = AmqpDsn("amqp://guest:guest@localhost:5672/")

    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    server: WorkerServerSettings = Field(default_factory=WorkerServerSettings)

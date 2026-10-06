from typing import Literal, final

from pydantic import Field

from payment_processing.config.settings._base_settings import BaseAppSettings
from payment_processing.config.settings.app import AppSettings
from payment_processing.config.settings.database import DatabaseSettings
from payment_processing.config.settings.outbox import OutboxSettings
from payment_processing.config.settings.worker import WorkerSettings

__all__ = ("Settings",)


@final
class Settings(BaseAppSettings):
    environment: Literal["local", "test", "production"] = "production"

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    app: AppSettings = Field(default_factory=AppSettings)
    worker: WorkerSettings = Field(default_factory=WorkerSettings)
    outbox: OutboxSettings = Field(default_factory=OutboxSettings)

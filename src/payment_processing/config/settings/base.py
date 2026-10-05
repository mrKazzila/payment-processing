from typing import final

from pydantic import Field

from payment_processing.config.settings._base_settings import BaseAppSettings
from payment_processing.config.settings.app import AppSettings
from payment_processing.config.settings.worker import WorkerSettings

__all__ = ("Settings",)


@final
class Settings(BaseAppSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    worker: WorkerSettings = Field(default_factory=WorkerSettings)

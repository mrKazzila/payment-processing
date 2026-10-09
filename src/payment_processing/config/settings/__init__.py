from functools import lru_cache

from payment_processing.config.settings.app import (
    AppServerSettings,
    AppSettings,
)
from payment_processing.config.settings.base import Settings
from payment_processing.config.settings.worker import (
    WorkerServerSettings,
    WorkerSettings,
)

__all__ = (
    "AppServerSettings",
    "AppSettings",
    "Settings",
    "WorkerServerSettings",
    "WorkerSettings",
    "get_settings",
)


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from payment_processing.config.settings.app import AppSettings
from payment_processing.config.settings.base import Settings
from payment_processing.config.settings.worker import WorkerSettings

__all__ = (
    "AppSettings",
    "Settings",
    "WorkerSettings",
    "get_settings",
)


@lru_cache
def get_settings() -> Settings:
    return Settings()

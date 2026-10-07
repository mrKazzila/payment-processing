from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, SecretStr

from payment_processing.config.settings.logging import LoggingSettings

__all__ = ("AppSettings", "AppServerSettings")


class AppServerSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    loop: Literal["none", "auto", "uvloop"] | str = "auto"


class AppSettings(BaseModel):
    """Application settings."""

    name: str = "Payment Processing API"
    version: str = "0.1.0"
    api_key: SecretStr | None = Field(default=None, min_length=1)

    server: AppServerSettings = Field(default_factory=AppServerSettings)
    logging: LoggingSettings = Field(
        default_factory=lambda: LoggingSettings(renderer="json")
    )

from pydantic import BaseModel

from payment_processing.config.logging import LogLevel, LogRenderer

__all__ = ("AppSettings",)


class AppSettings(BaseModel):
    """Application settings."""

    name: str = "Payment Processing API"
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False

    log_level: LogLevel = "INFO"
    log_renderer: LogRenderer = "json"
    enable_log_diagnostics: bool = False
    use_utc_timestamps: bool = True

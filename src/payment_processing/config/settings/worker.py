__all__ = ("WorkerSettings",)

from typing import Literal

from pydantic import BaseModel


class WorkerSettings(BaseModel):
    """Worker settings."""

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_renderer: Literal["console", "json"] = "console"
    use_utc_timestamps: bool = True
    enable_log_diagnostics: bool = False

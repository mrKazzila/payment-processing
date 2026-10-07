from pydantic import BaseModel

from payment_processing.infrastructure.observability.config import (
    LoggingConfig,
    LogLevel,
    LogRenderer,
)

__all__ = ("LoggingSettings",)


class LoggingSettings(BaseModel):
    level: LogLevel = "INFO"
    renderer: LogRenderer = "console"
    enable_diagnostics: bool = False
    use_utc_timestamps: bool = True

    def to_config(self) -> LoggingConfig:
        return LoggingConfig(
            level=self.level,
            renderer=self.renderer,
            enable_diagnostics=self.enable_diagnostics,
            use_utc_timestamps=self.use_utc_timestamps,
        )

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("BaseAppSettings",)


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="env/.env",
        env_file_encoding="utf-8",
        env_prefix="PP_",
        env_nested_delimiter="__",
        extra="allow",
    )

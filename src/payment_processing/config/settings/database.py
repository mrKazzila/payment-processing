from pydantic import BaseModel, Field, SecretStr


class DatabaseSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(default=5432, ge=1, le=65535)
    name: str = "payments"
    user: str = "payments"
    password: SecretStr = SecretStr("payments_dev")

    pool_size: int = Field(default=5, ge=1)
    max_overflow: int = Field(default=5, ge=0)
    pool_timeout: float = Field(default=30.0, gt=0)

import secrets
from dataclasses import dataclass, field
from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader


@dataclass(frozen=True, slots=True, kw_only=True)
class ApiKeyAuthConfig:
    expected_key: str | None = field(repr=False)


ApiKey = Annotated[
    str | None,
    Depends(
        APIKeyHeader(
            name="X-API-Key",
            auto_error=False,
        )
    ),
]


@inject
async def require_api_key(
    api_key: ApiKey,
    config: Annotated[ApiKeyAuthConfig, FromComponent()],
) -> None:
    expected = config.expected_key

    if expected is None:
        raise RuntimeError("API key is not configured")

    if api_key is None or not secrets.compare_digest(
        api_key.encode("utf-8"),
        expected.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "APIKey"},
        )

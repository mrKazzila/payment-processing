from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_database_url(
    *,
    user: str,
    password: str,
    host: str,
    port: int,
    name: str,
) -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=user,
        password=password,
        host=host,
        port=port,
        database=name,
    )


def create_database_engine(
    *,
    url: URL,
    pool_size: int,
    max_overflow: int,
    pool_timeout: float,
) -> AsyncEngine:
    return create_async_engine(
        url=url,
        isolation_level="READ COMMITTED",
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
    )

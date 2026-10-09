import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.rabbitmq import RabbitMqContainer

from payment_processing.infrastructure.database.models.outbox import (
    OutboxModel,
)
from payment_processing.infrastructure.database.models.payment import (
    PaymentModel,
)
from tests.factories import make_settings


@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer(
        "postgres:17-bookworm",
        username="test",
        password="test",
        dbname="payments_test",
        driver="psycopg",
    ) as container:
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("PP_")
        }
        environment.update(
            {
                "PP_ENVIRONMENT": "test",
                "PP_DATABASE__HOST": container.get_container_host_ip(),
                "PP_DATABASE__PORT": str(container.get_exposed_port(5432)),
                "PP_DATABASE__NAME": container.dbname,
                "PP_DATABASE__USER": container.username,
                "PP_DATABASE__PASSWORD": container.password,
            }
        )
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=Path(__file__).resolve().parents[2],
            env=environment,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        yield container


@pytest.fixture
def database_settings(postgres: PostgresContainer):
    return make_settings(
        database={
            "host": postgres.get_container_host_ip(),
            "port": int(postgres.get_exposed_port(5432)),
            "name": postgres.dbname,
            "user": postgres.username,
            "password": postgres.password,
        }
    )


@pytest.fixture
async def database_engine(postgres: PostgresContainer):
    engine = create_async_engine(postgres.get_connection_url())
    try:
        async with engine.begin() as connection:
            await connection.execute(delete(OutboxModel))
            await connection.execute(delete(PaymentModel))
        yield engine
    finally:
        try:
            async with engine.begin() as connection:
                await connection.execute(delete(OutboxModel))
                await connection.execute(delete(PaymentModel))
        finally:
            await engine.dispose()


@pytest.fixture
async def database_session(database_engine: AsyncEngine):
    async with AsyncSession(
        database_engine, expire_on_commit=False
    ) as session:
        yield session


@pytest.fixture(scope="session")
def rabbitmq_url():
    with RabbitMqContainer(
        "rabbitmq:4-management",
        username="test",
        password="test",
    ) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(5672)
        yield f"amqp://test:test@{host}:{port}/"

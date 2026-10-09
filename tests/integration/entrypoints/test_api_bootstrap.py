from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payment_processing.config.settings import Settings
from payment_processing.entrypoints.api.bootstrap import create_application
from payment_processing.infrastructure.database.models.outbox import (
    OutboxModel,
)
from tests.data.entrypoints import (
    generate_documentation_disabled_environment_data,
)
from tests.factories import make_request, make_settings


@pytest.mark.anyio
async def test_documentation_enabled_locally():
    app = create_application(settings=make_settings(environment="local"))
    client = AsyncClient(transport=ASGITransport(app), base_url="http://test")

    async with app.router.lifespan_context(app), client:
        response = await client.get("/api/openapi.json")

    assert response.status_code == 200
    assert app.debug is True
    assert "/api/v1/payments" in response.json()["paths"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "environment", generate_documentation_disabled_environment_data()
)
async def test_documentation_disabled(environment: str):
    app = create_application(settings=make_settings(environment=environment))
    client = AsyncClient(transport=ASGITransport(app), base_url="http://test")

    async with app.router.lifespan_context(app), client:
        response = await client.get("/api/openapi.json")

    assert response.status_code == 404
    assert app.debug is False


@pytest.mark.anyio
@pytest.mark.requires_docker
async def test_create_and_get_payment(
    database_settings: Settings, database_session: AsyncSession
):
    app = create_application(settings=database_settings)
    body = make_request()
    key = str(uuid4())
    headers = {"X-API-Key": "test-api-key", "Idempotency-Key": key}
    client = AsyncClient(transport=ASGITransport(app), base_url="http://test")

    async with app.router.lifespan_context(app), client:
        created = await client.post(
            "/api/v1/payments", json=body, headers=headers
        )
        payment_id = created.json()["payment_id"]
        fetched = await client.get(
            f"/api/v1/payments/{payment_id}", headers=headers
        )

    assert created.status_code == 202
    assert created.json()["status"] == "pending"
    assert fetched.status_code == 200
    assert fetched.json() == body | {
        "payment_id": payment_id,
        "status": "pending",
        "idempotency_key": key,
        "created_at": created.json()["created_at"],
        "processed_at": None,
    }
    entries = (await database_session.scalars(select(OutboxModel))).all()
    assert len(entries) == 1
    assert entries[0].payload == {"payment_id": payment_id}
    assert entries[0].routing_key == "payments.new"
    assert entries[0].published_at is None

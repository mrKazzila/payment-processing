from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from dishka import Provider, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from payment_processing.application.use_cases.create_payment import (
    CreatePayment,
)
from payment_processing.application.use_cases.get_payment import GetPayment
from payment_processing.presentation.api.application import create_app
from payment_processing.presentation.api.security import ApiKeyAuthConfig


@pytest.fixture
async def http_api():
    create_payment = AsyncMock(spec=CreatePayment)
    get_payment = AsyncMock(spec=GetPayment)
    provider = Provider(scope=Scope.APP)
    provider.provide(lambda: create_payment, provides=CreatePayment)
    provider.provide(lambda: get_payment, provides=GetPayment)
    provider.provide(
        lambda: ApiKeyAuthConfig(expected_key="test-api-key"),
        provides=ApiKeyAuthConfig,
    )
    container = make_async_container(provider)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            await container.close()

    app = create_app(title="Test API", version="test", lifespan=lifespan)
    setup_dishka(container=container, app=app)
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app), base_url="http://test"
        ) as client:
            yield SimpleNamespace(
                client=client, create=create_payment, get=get_payment
            )

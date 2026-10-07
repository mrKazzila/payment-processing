from types import SimpleNamespace
from uuid import uuid4

import pytest

from payment_processing.application.exceptions import (
    IdempotencyConflictError,
    PaymentNotFoundError,
)
from tests.data.presentation import (
    generate_invalid_authorization_data,
    generate_invalid_request_data,
)
from tests.factories import make_request

pytestmark = pytest.mark.anyio


async def test_authorization(http_api: SimpleNamespace):
    headers = {"X-API-Key": "test-api-key"}

    response = await http_api.client.get("/health", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


@pytest.mark.parametrize("headers", generate_invalid_authorization_data())
async def test_reject_invalid_authorization(
    http_api: SimpleNamespace, headers: dict
):
    response = await http_api.client.get("/health", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}
    assert response.headers["WWW-Authenticate"] == "APIKey"


@pytest.mark.parametrize(("field", "value"), generate_invalid_request_data())
async def test_invalid_payment_request(
    http_api: SimpleNamespace, field: str, value: str
):
    body = make_request() | {field: value}
    headers = {"X-API-Key": "test-api-key", "Idempotency-Key": "request-key"}

    response = await http_api.client.post(
        "/api/v1/payments", json=body, headers=headers
    )

    assert response.status_code == 422
    assert any(
        item["loc"] == ["body", field] for item in response.json()["detail"]
    )
    http_api.create.execute.assert_not_awaited()


async def test_payment_not_found_response(http_api: SimpleNamespace):
    payment_id = uuid4()
    http_api.get.execute.side_effect = PaymentNotFoundError(
        payment_id=payment_id
    )
    headers = {"X-API-Key": "test-api-key"}

    response = await http_api.client.get(
        f"/api/v1/payments/{payment_id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "payment_not_found",
        "message": "Payment was not found.",
    }
    http_api.get.execute.assert_awaited_once_with(payment_id=payment_id)


async def test_idempotency_conflict_response(http_api: SimpleNamespace):
    http_api.create.execute.side_effect = IdempotencyConflictError()
    headers = {"X-API-Key": "test-api-key", "Idempotency-Key": "request-key"}
    body = make_request()

    response = await http_api.client.post(
        "/api/v1/payments",
        json=body,
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "idempotency_conflict",
        "message": "Idempotency key was already used with different data.",
    }
    http_api.create.execute.assert_awaited_once()

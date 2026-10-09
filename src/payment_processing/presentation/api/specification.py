API_SUMMARY = "API for asynchronous payment processing."

API_DESCRIPTION = """
## Overview

Create payments and retrieve their current status.
Payments are processed asynchronously; results are sent to `webhook_url`.

## Payments

- `POST /api/v1/payments` — create a payment (`202 Accepted`).
- `GET /api/v1/payments/{payment_id}` — retrieve a payment and its status.

Creating a payment requires the `Idempotency-Key` header. Repeating a request
with the same key and data returns the existing payment; using different data
returns `409 Conflict`.
All API endpoints, including `/health`, require the `X-API-Key` header.

## Health check

- `GET /health` — check HTTP API availability; returns `{"status": "OK"}`.

## Documentation

Available in the local environment (`environment=local`).

- [Swagger UI](/api/openapi)
- [ReDoc](/redoc)
- [OpenAPI schema](/api/openapi.json)
"""

OPENAPI_TAGS = [
    {
        "name": "Payments",
        "description": "Create payments and retrieve their status.",
    },
    {
        "name": "Health",
        "description": "Check HTTP API availability.",
    },
]

OPENAPI_EXTERNAL_DOCS = {
    "description": "Payment Processing project repository.",
    "url": "https://github.com/mrKazzila/payment-processing",
}

SWAGGER_UI_PARAMETERS = {
    "displayRequestDuration": True,
    "filter": True,
}

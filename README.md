# payment-processing

## Getting started

Copy the configuration file and adjust the settings as needed.

```bash
cp env/.env.example env/.env
```

Start the project. The API will be available at `http://localhost:8000`.

```bash
docker compose --env-file env/.env up -d --build
```

## Try it with curl

Check whether the service is available:

```bash
curl http://localhost:8000/health \
  -H 'X-API-Key: local-development-key' \
  -w '\n'
```

Create a payment:

```bash
curl http://localhost:8000/api/v1/payments \
  -H 'X-API-Key: local-development-key' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-payment-1' \
  -w '\n' \
  -d '{
    "amount": "150.00",
    "currency": "RUB",
    "description": "Order #1",
    "metadata": {"order_id": "1"},
    "webhook_url": "http://payment-webhook:8080/ok"
  }'
```

Retrieve the payment, replacing `PASTE_PAYMENT_ID` with the `payment_id` from the response:

```bash
curl http://localhost:8000/api/v1/payments/PASTE_PAYMENT_ID \
  -w '\n' \
  -H 'X-API-Key: local-development-key'
```

## Tests

Install dependencies and run the tests that do not require external services:

```bash
uv sync --dev
uv run pytest -m "not requires_docker"
```

The full test suite requires Docker to be running. Testcontainers automatically
starts PostgreSQL 17 and RabbitMQ 4 on random ports and removes the containers
after the test run. Images must be downloaded on the first run. You do not need
to start the application's Docker Compose stack; its databases and queues are
not used by the tests.

```bash
uv run pytest
uv run pytest -n 2
```

Run only the tests that require Docker:

```bash
uv run pytest -m requires_docker
```

Each pytest process uses separate containers. The database schema is created
using real Alembic migrations, data is cleared between tests, and queues have
unique names. If Docker is unavailable, integration tests that require it fail
rather than being skipped. Docker connection settings and
`~/.testcontainers.properties`, if present, must point to a running Docker daemon.

Tests are grouped by the boundaries they exercise, with Clean Architecture
layers preserved within each group:

```text
tests/
├── unit/
│   ├── domain/
│   ├── application/
│   └── entrypoints/
├── integration/
│   ├── infrastructure/
│   ├── presentation/
│   └── entrypoints/
├── data/
├── fixtures/
└── factories.py
```

The `unit/` directory contains domain tests, use case tests with test doubles
for ports, and tests verifying that startup fails with an invalid API key.
The `integration/` directory contains adapter tests using PostgreSQL/RabbitMQ
and HTTP tests with real routers, validation, and dependency injection,
including documentation availability and payment creation.

The test level and Docker dependency are independent: HTTP tests with test
doubles for use cases are integration tests, but they do not require Docker.
The `requires_docker` marker applies only to tests that need containers.

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/integration -m "not requires_docker"
```

Tests cover all five Clean Architecture layers. Success and failure scenarios
use separate test functions without conditional branches. Parameterized test
cases are stored in `tests/data/`. Tests follow the Arrange–Act–Assert (AAA)
pattern, with blank lines separating the phases. There are no end-to-end (E2E)
tests yet.

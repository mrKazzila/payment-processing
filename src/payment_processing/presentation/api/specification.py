API_SUMMARY = "API сервиса асинхронной обработки платежей."

API_DESCRIPTION = """
## Описание

Создание платежей и получение их текущего состояния.
Платежи обрабатываются асинхронно; результат отправляется на `webhook_url`.

## Платежи

- `POST /api/v1/payments` — создание платежа (`202 Accepted`).
- `GET /api/v1/payments/{payment_id}` — получение платежа и его статуса.

Для создания обязателен заголовок `Idempotency-Key`. Повтор с тем же ключом
и данными возвращает существующий платёж; с другими данными — `409 Conflict`.
Все методы API, включая `/health`, требуют заголовок `X-API-Key`.

## Служебные методы

- `GET /health` — проверка доступности HTTP API; возвращает `{"status": "OK"}`.

## Документация

Доступна в локальном окружении (`environment=local`).

- [Swagger UI](/api/openapi)
- [ReDoc](/redoc)
- [Схема OpenAPI](/api/openapi.json)
"""

OPENAPI_TAGS = [
    {
        "name": "Payments",
        "description": "Создание платежей и получение их состояния.",
    },
    {
        "name": "Health",
        "description": "Проверка доступности HTTP API.",
    },
]

OPENAPI_EXTERNAL_DOCS = {
    "description": "Репозиторий проекта Payment Processing.",
    "url": "https://github.com/mrKazzila/payment-processing",
}

SWAGGER_UI_PARAMETERS = {
    "displayRequestDuration": True,
    "filter": True,
}

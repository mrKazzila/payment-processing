API_SUMMARY = "API сервиса асинхронной обработки платежей."

API_DESCRIPTION = """
## Описание

Payment Processing - проект сервиса асинхронной обработки платежей.
API находится в разработке.

## Служебные методы

- `GET /health` — проверка доступности HTTP API; возвращает `{"status": "OK"}`.

## Документация

- [Swagger UI](/api/openapi)
- [ReDoc](/redoc)
- [Схема OpenAPI](/api/openapi.json)
"""

OPENAPI_TAGS = [
    {
        "name": "Payments",
        "description": "Payment Processing API.",
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

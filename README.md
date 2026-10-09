# payment-processing

## Запуск

Скопировать настройки, при необходимости изменить.
```bash
cp env/.env.example env/.env
```

Запуск проекта, API будет доступен на `http://localhost:8000`.

```bash
docker compose --env-file env/.env up -d --build
```

## Попробовать через curl

Проверить, доступен ли сервис:

```bash
curl http://localhost:8000/health \
  -H 'X-API-Key: local-development-key' \
  -w '\n'
```

Создать платёж.

```bash
curl http://localhost:8000/api/v1/payments \
  -H 'X-API-Key: local-development-key' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-payment-1' \
  -w '\n' \
  -d '{
    "amount": "150.00",
    "currency": "RUB",
    "description": "Заказ №1",
    "metadata": {"order_id": "1"},
    "webhook_url": "http://payment-webhook:8080/ok"
  }'
```

Посмотреть платёж, подставь `payment_id` из ответа:

```bash
curl http://localhost:8000/api/v1/payments/PASTE_PAYMENT_ID \
  -w '\n' \
  -H 'X-API-Key: local-development-key'
```

## Тесты

Установить зависимости и запустить тесты без внешних сервисов:

```bash
uv sync --dev
uv run pytest -m "not requires_docker"
```

Полный набор требует запущенного Docker. Testcontainers автоматически
поднимает PostgreSQL 17 и RabbitMQ 4 на случайных портах и удаляет контейнеры
после запуска. При первом запуске потребуется скачать образы. Рабочий
Docker Compose поднимать не нужно, его базы и очереди не используются.

```bash
uv run pytest
uv run pytest -n 2
```

Только проверки с Docker:

```bash
uv run pytest -m requires_docker
```

Для каждого процесса pytest используются отдельные контейнеры. Схема БД
создаётся настоящими Alembic-миграциями, данные очищаются между тестами,
очереди имеют уникальные имена. Недоступный Docker приводит к ошибке
интеграционных тестов, а не к их пропуску. Настройки подключения Docker и
`~/.testcontainers.properties`, если этот файл есть, должны указывать
на работающий Docker daemon.

Тесты разделены по проверяемым границам, внутри сохранены слои ЧА:

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

В `unit/` находятся проверки домена, use cases с подменёнными портами
и отказа запуска с некорректным API-ключом. В `integration/` — проверки
адаптеров с PostgreSQL/RabbitMQ и HTTP-проверки с настоящими роутерами,
валидацией и DI, включая доступность документации и создание платежа.

Уровень теста и зависимость от Docker независимы: HTTP-тесты с подменёнными
use cases являются интеграционными, но Docker им не нужен. Маркер
`requires_docker` отмечает только проверки, которым нужны контейнеры.

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/integration -m "not requires_docker"
```

Тесты покрывают все пять слоёв ЧА. Успешные и ошибочные сценарии
разделены на самостоятельные функции без условных ветвлений.
Параметризованные случаи вынесены в `tests/data/`. Тесты используют AAA
с разделением пустыми строками. Сквозных E2E-тестов пока нет.

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

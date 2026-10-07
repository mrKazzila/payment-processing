from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from payment_processing.application.dtos.payments import CreatePaymentCommand
from payment_processing.config.settings import Settings
from payment_processing.domain.enums import Currency
from payment_processing.domain.payment import Payment


def make_payment(**overrides) -> Payment:
    values = {
        "id": uuid4(),
        "amount": Decimal("12.50"),
        "currency": Currency.RUB,
        "description": "Test payment",
        "metadata": {"order_id": "42"},
        "idempotency_key": str(uuid4()),
        "webhook_url": "https://example.com/webhook",
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    return Payment(**(values | overrides))


def make_command(payment: Payment) -> CreatePaymentCommand:
    return CreatePaymentCommand(
        **{
            name: getattr(payment, name)
            for name in CreatePaymentCommand.__dataclass_fields__
        }
    )


def make_request() -> dict:
    return {
        "amount": "12.50",
        "currency": "RUB",
        "description": "Test payment",
        "metadata": {"order_id": "42"},
        "webhook_url": "https://example.com/webhook",
    }


def make_settings(**overrides) -> Settings:
    values = {"environment": "test", "app": {"api_key": "test-api-key"}}
    return Settings(_env_file=None, **(values | overrides))

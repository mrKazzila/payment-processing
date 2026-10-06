from dataclasses import dataclass
from decimal import Decimal

from payment_processing.domain.enums import Currency
from payment_processing.domain.types import JsonValue


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePaymentCommand:
    amount: Decimal
    currency: Currency
    description: str
    metadata: JsonValue
    idempotency_key: str
    webhook_url: str

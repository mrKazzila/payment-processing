from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, JsonValue

from payment_processing.domain.enums import Currency, PaymentStatus
from payment_processing.domain.payment import MAX_PAYMENT_AMOUNT


class SCreatePaymentRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
    )

    amount: Decimal = Field(
        gt=0,
        le=MAX_PAYMENT_AMOUNT,
        max_digits=18,
        decimal_places=2,
    )
    currency: Currency
    description: str
    metadata: JsonValue
    webhook_url: AnyHttpUrl


class SCreatePaymentResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class SPaymentResponse(BaseModel):
    payment_id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: JsonValue
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None

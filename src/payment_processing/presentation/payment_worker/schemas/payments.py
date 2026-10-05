from uuid import UUID

from pydantic import BaseModel, Field


class PaymentCreatedMessage(BaseModel):
    """Событие о платеже, принятом для асинхронной обработки."""

    payment_id: UUID = Field(
        description="Идентификатор платежа в таблице payments.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

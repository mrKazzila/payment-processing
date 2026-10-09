from uuid import UUID

from pydantic import BaseModel, Field


class PaymentCreatedMessage(BaseModel):
    payment_id: UUID = Field(
        description="Payment ID in the payments table.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

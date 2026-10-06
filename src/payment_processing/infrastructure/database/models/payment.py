from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Numeric,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from payment_processing.domain.types import JsonValue
from payment_processing.infrastructure.database.models.base import Base

PAYMENT_IDEMPOTENCY_CONSTRAINT = "uq_payments_idempotency_key"


class PaymentModel(Base):
    __tablename__ = "payments"

    __table_args__ = (
        UniqueConstraint(
            "idempotency_key",
            name=PAYMENT_IDEMPOTENCY_CONSTRAINT,
        ),
        CheckConstraint(
            "amount > 0 AND amount <= 9999999999999999.99",
            name="amount_range",
        ),
        CheckConstraint(
            "currency IN ('RUB', 'USD', 'EUR')",
            name="currency",
        ),
        CheckConstraint(
            "status IN ('pending', 'succeeded', 'failed')",
            name="status",
        ),
        CheckConstraint(
            "(status = 'pending' AND processed_at IS NULL) OR "
            "(status IN ('succeeded', 'failed') "
            "AND processed_at IS NOT NULL)",
            name="processed_at_matches_status",
        ),
        CheckConstraint(
            "processed_at IS NULL OR processed_at >= created_at",
            name="processing_time",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    metadata_json: Mapped[JsonValue] = mapped_column(
        "metadata",
        JSONB(none_as_null=False),
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    webhook_url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

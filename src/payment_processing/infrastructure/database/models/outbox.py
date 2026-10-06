from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from payment_processing.domain.types import JsonValue
from payment_processing.infrastructure.database.models.base import Base


class OutboxModel(Base):
    __tablename__ = "outbox"

    __table_args__ = (
        Index(
            "ix_outbox_unpublished_created_at_id",
            "created_at",
            "id",
            postgresql_where=text("published_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    routing_key: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, JsonValue]] = mapped_column(
        JSONB,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

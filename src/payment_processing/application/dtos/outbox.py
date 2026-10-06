from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from payment_processing.domain.types import JsonValue


@dataclass(frozen=True, slots=True, kw_only=True)
class OutboxMessage:
    id: UUID
    routing_key: str
    payload: dict[str, JsonValue]
    created_at: datetime

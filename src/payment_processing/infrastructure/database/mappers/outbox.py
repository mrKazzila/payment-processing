from copy import deepcopy

from payment_processing.application.dtos.outbox import OutboxMessage
from payment_processing.infrastructure.database.models.outbox import (
    OutboxModel,
)


def outbox_to_message(*, model: OutboxModel) -> OutboxMessage:
    return OutboxMessage(
        id=model.id,
        routing_key=model.routing_key,
        payload=deepcopy(model.payload),
        created_at=model.created_at,
    )

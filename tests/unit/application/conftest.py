from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from payment_processing.application.ports.outbox import OutboxRepository
from payment_processing.application.ports.payment_gateway import PaymentGateway
from payment_processing.application.ports.payments import PaymentRepository
from payment_processing.application.ports.webhooks import WebhookSender


class FakeTransactions:
    def __init__(self) -> None:
        self.active = False
        self.commits = 0

    @asynccontextmanager
    async def begin(self):
        self.active = True
        try:
            yield
            self.commits += 1
        finally:
            self.active = False


@pytest.fixture
def ports():
    dependencies = SimpleNamespace(
        payments=AsyncMock(spec=PaymentRepository),
        outbox=AsyncMock(spec=OutboxRepository),
        gateway=AsyncMock(spec=PaymentGateway),
        webhooks=AsyncMock(spec=WebhookSender),
        transactions=FakeTransactions(),
        events=[],
    )

    def record_event(name: str):
        async def record(**_kwargs):
            dependencies.events.append(
                (
                    name,
                    dependencies.transactions.active,
                    dependencies.transactions.commits,
                )
            )

        return record

    dependencies.payments.add.side_effect = record_event("add payment")
    dependencies.outbox.add_payment_created.side_effect = record_event(
        "add outbox"
    )
    dependencies.payments.update.side_effect = record_event("update payment")
    dependencies.webhooks.send_payment_result.side_effect = record_event(
        "send webhook"
    )
    return dependencies

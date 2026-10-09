import json
from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from payment_processing.application.dtos.outbox import OutboxMessage
from payment_processing.application.exceptions import (
    DuplicateIdempotencyKeyError,
    MessagePublishError,
)
from payment_processing.infrastructure.database.repositories.payments import (
    SQLAlchemyPaymentRepository,
)
from tests.factories import make_payment

pytestmark = [pytest.mark.anyio, pytest.mark.requires_docker]


async def test_payment_roundtrip(
    database_session: AsyncSession, database_engine: AsyncEngine
):
    payment = make_payment()
    repository = SQLAlchemyPaymentRepository(database_session)
    async with database_session.begin():
        await repository.add(payment=payment)

    async with AsyncSession(database_engine) as reader:
        loaded = await SQLAlchemyPaymentRepository(reader).get_by_id(
            payment_id=payment.id
        )

    assert loaded == payment
    assert loaded.amount.as_tuple().exponent == -2


async def test_duplicate_idempotency_key(database_session: AsyncSession):
    payment = make_payment()
    duplicate = replace(payment, id=uuid4())
    repository = SQLAlchemyPaymentRepository(database_session)
    async with database_session.begin():
        await repository.add(payment=payment)

    with pytest.raises(DuplicateIdempotencyKeyError) as error:
        async with database_session.begin():
            await repository.add(payment=duplicate)

    assert str(error.value) == ""
    assert await repository.get_by_id(payment_id=duplicate.id) is None
    assert (
        await repository.get_by_idempotency_key(
            idempotency_key=payment.idempotency_key
        )
        == payment
    )


async def test_publish_message(messaging: SimpleNamespace):
    payment = make_payment()
    message = OutboxMessage(
        id=uuid4(),
        routing_key=messaging.queue.name,
        payload={"payment_id": str(payment.id)},
        created_at=payment.created_at,
    )

    await messaging.publisher.publish(message=message)

    received = await messaging.queue.get(timeout=5)
    assert json.loads(received.body) == message.payload
    assert received.message_id == str(message.id)
    await received.ack()


async def test_reject_unroutable_message(messaging: SimpleNamespace):
    payment = make_payment()
    message = OutboxMessage(
        id=uuid4(),
        routing_key=f"missing.{uuid4()}",
        payload={"payment_id": str(payment.id)},
        created_at=payment.created_at,
    )

    with pytest.raises(MessagePublishError) as error:
        await messaging.publisher.publish(message=message)

    assert str(message.id) in str(error.value)
    assert await messaging.queue.get(fail=False, timeout=5) is None

from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

import pytest

from payment_processing.application.exceptions import IdempotencyConflictError
from payment_processing.application.use_cases.create_payment import (
    CreatePayment,
)
from payment_processing.application.use_cases.process_payment import (
    ProcessPayment,
)
from payment_processing.domain.enums import PaymentStatus
from tests.data.application import (
    generate_completed_payment_data,
    generate_processing_data,
)
from tests.factories import make_command, make_payment

pytestmark = pytest.mark.anyio


async def test_create_payment_with_outbox(ports: SimpleNamespace):
    command = make_command(make_payment())
    ports.payments.get_by_idempotency_key.return_value = None
    use_case = CreatePayment(ports.payments, ports.outbox, ports.transactions)

    payment = await use_case.execute(command=command)

    assert make_command(payment) == command
    assert payment.status is PaymentStatus.PENDING
    ports.payments.add.assert_awaited_once_with(payment=payment)
    ports.outbox.add_payment_created.assert_awaited_once_with(
        payment_id=payment.id,
        occurred_at=payment.created_at,
    )
    assert ports.transactions.commits == 1
    assert ports.events == [("add payment", True, 0), ("add outbox", True, 0)]


async def test_idempotent_creation(ports: SimpleNamespace):
    existing = make_payment()
    command = make_command(existing)
    ports.payments.get_by_idempotency_key.return_value = existing
    use_case = CreatePayment(ports.payments, ports.outbox, ports.transactions)

    result = await use_case.execute(command=command)

    assert result is existing
    ports.payments.add.assert_not_awaited()
    ports.outbox.add_payment_created.assert_not_awaited()


async def test_reject_idempotency_conflict(ports: SimpleNamespace):
    existing = make_payment()
    command = replace(make_command(existing), description="Different request")
    ports.payments.get_by_idempotency_key.return_value = existing
    use_case = CreatePayment(ports.payments, ports.outbox, ports.transactions)

    with pytest.raises(IdempotencyConflictError) as error:
        await use_case.execute(command=command)

    assert (
        str(error.value)
        == "Idempotency key was already used with different data."
    )
    ports.payments.add.assert_not_awaited()
    ports.outbox.add_payment_created.assert_not_awaited()


@pytest.mark.parametrize(
    ("succeeded", "expected_status"), generate_processing_data()
)
async def test_process_payment(
    ports: SimpleNamespace, succeeded: bool, expected_status: PaymentStatus
):
    payment = make_payment()
    ports.payments.get_by_id_for_update.return_value = payment
    ports.gateway.charge.return_value = succeeded
    use_case = ProcessPayment(
        ports.payments, ports.gateway, ports.webhooks, ports.transactions
    )

    await use_case.execute(payment_id=payment.id)

    ports.gateway.charge.assert_awaited_once_with(payment=payment)
    ports.payments.update.assert_awaited_once()
    completed = ports.payments.update.await_args.kwargs["payment"]
    assert completed.status is expected_status
    assert completed.processed_at >= payment.created_at
    ports.webhooks.send_payment_result.assert_awaited_once_with(
        payment=completed
    )
    assert ports.transactions.commits == 1
    assert not ports.transactions.active
    assert ports.events == [
        ("update payment", True, 0),
        ("send webhook", False, 1),
    ]


@pytest.mark.parametrize("status", generate_completed_payment_data())
async def test_redelivered_payment(
    ports: SimpleNamespace, status: PaymentStatus
):
    original = make_payment()
    payment = replace(
        original,
        status=status,
        processed_at=original.created_at + timedelta(seconds=1),
    )
    ports.payments.get_by_id_for_update.return_value = payment
    use_case = ProcessPayment(
        ports.payments, ports.gateway, ports.webhooks, ports.transactions
    )

    await use_case.execute(payment_id=payment.id)

    ports.gateway.charge.assert_not_awaited()
    ports.payments.update.assert_not_awaited()
    ports.webhooks.send_payment_result.assert_awaited_once_with(
        payment=payment
    )
    assert ports.transactions.commits == 1
    assert not ports.transactions.active
    assert ports.events == [("send webhook", False, 1)]

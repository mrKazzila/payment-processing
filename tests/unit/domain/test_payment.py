from datetime import timedelta
from decimal import Decimal

import pytest

from payment_processing.domain.enums import PaymentStatus
from payment_processing.domain.exceptions import (
    InvalidPaymentAmountError,
    InvalidPaymentStateError,
)
from payment_processing.domain.payment import validate_amount
from tests.data.domain import (
    generate_invalid_money_data,
    generate_transition_data,
    generate_valid_amount_data,
)
from tests.factories import make_payment


@pytest.mark.parametrize(("raw", "expected"), generate_valid_amount_data())
def test_normalize_amount(raw: str, expected: str):
    amount = Decimal(raw)

    result = validate_amount(amount=amount)

    assert result == Decimal(expected)
    assert result.as_tuple().exponent == -2


@pytest.mark.parametrize(("amount", "message"), generate_invalid_money_data())
def test_reject_invalid_amount(amount: Decimal | str, message: str):
    with pytest.raises(InvalidPaymentAmountError) as error:
        validate_amount(amount=amount)

    assert str(error.value) == message


@pytest.mark.parametrize(("method", "status"), generate_transition_data())
def test_payment_transition(method: str, status: PaymentStatus):
    original = make_payment()
    processed_at = original.created_at + timedelta(seconds=1)

    result = getattr(original, method)(processed_at=processed_at)

    assert result.status is status
    assert result.processed_at == processed_at
    assert result.id == original.id
    assert original.status is PaymentStatus.PENDING
    assert original.processed_at is None


@pytest.mark.parametrize(("method", "status"), generate_transition_data())
def test_reject_repeated_completion(method: str, status: PaymentStatus):
    original = make_payment()
    processed_at = original.created_at + timedelta(seconds=1)
    payment = getattr(original, method)(processed_at=processed_at)

    with pytest.raises(InvalidPaymentStateError) as error:
        getattr(payment, method)(processed_at=processed_at)

    assert (
        str(error.value)
        == f"Cannot complete payment in status {status.value}."
    )
    assert payment.status is status
    assert payment.processed_at == processed_at
    assert original.status is PaymentStatus.PENDING
    assert original.processed_at is None

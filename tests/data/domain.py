from decimal import Decimal

import pytest

from payment_processing.domain.enums import PaymentStatus


def generate_valid_amount_data() -> list:
    return [
        pytest.param("1", "1.00", id="integer amount"),
        pytest.param("0.01", "0.01", id="minimum amount"),
        pytest.param("12.500", "12.50", id="trailing zero"),
        pytest.param(
            "9999999999999999.99", "9999999999999999.99", id="maximum amount"
        ),
    ]


def generate_invalid_money_data() -> list:
    limit = "Amount must be positive and at most 9999999999999999.99."
    return [
        pytest.param("1", "Amount must be a Decimal.", id="wrong type"),
        pytest.param(Decimal("0"), limit, id="zero amount"),
        pytest.param(Decimal("-1"), limit, id="negative amount"),
        pytest.param(
            Decimal("NaN"), "Amount must be finite.", id="not a number"
        ),
        pytest.param(
            Decimal("Infinity"), "Amount must be finite.", id="infinite amount"
        ),
        pytest.param(
            Decimal("0.001"),
            "Amount must have at most two decimal places.",
            id="excess precision",
        ),
        pytest.param(Decimal("10000000000000000"), limit, id="exceeds limit"),
    ]


def generate_transition_data() -> list:
    return [
        pytest.param("succeed", PaymentStatus.SUCCEEDED, id="succeed"),
        pytest.param("fail", PaymentStatus.FAILED, id="fail"),
    ]

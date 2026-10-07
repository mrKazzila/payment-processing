import pytest

from payment_processing.domain.enums import PaymentStatus


def generate_processing_data() -> list:
    return [
        pytest.param(True, PaymentStatus.SUCCEEDED, id="successful charge"),
        pytest.param(False, PaymentStatus.FAILED, id="failed charge"),
    ]


def generate_completed_payment_data() -> list:
    return [
        pytest.param(PaymentStatus.SUCCEEDED, id="redelivered success"),
        pytest.param(PaymentStatus.FAILED, id="redelivered failure"),
    ]

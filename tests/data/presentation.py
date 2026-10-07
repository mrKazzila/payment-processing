import pytest


def generate_invalid_authorization_data() -> list:
    return [
        pytest.param({}, id="missing key"),
        pytest.param({"X-API-Key": "wrong"}, id="invalid key"),
    ]


def generate_invalid_request_data() -> list:
    return [
        pytest.param("amount", "0", id="zero amount"),
        pytest.param("amount", "0.001", id="excess precision"),
        pytest.param("currency", "INVALID", id="invalid currency"),
        pytest.param("webhook_url", "not a URL", id="invalid webhook URL"),
    ]

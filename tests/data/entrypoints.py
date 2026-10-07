import pytest


def generate_invalid_api_key_data() -> list:
    return [
        pytest.param(None, id="missing key"),
        pytest.param("   ", id="blank key"),
    ]


def generate_documentation_disabled_environment_data() -> list:
    return [
        pytest.param("test", id="test docs disabled"),
        pytest.param("production", id="production docs disabled"),
    ]

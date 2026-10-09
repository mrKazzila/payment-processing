import pytest

pytest_plugins = ("tests.fixtures.services",)


@pytest.fixture
def anyio_backend():
    return "asyncio"

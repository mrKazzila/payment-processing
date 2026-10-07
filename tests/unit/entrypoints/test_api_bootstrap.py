import pytest

from payment_processing.entrypoints.api.bootstrap import create_application
from tests.data.entrypoints import generate_invalid_api_key_data
from tests.factories import make_settings


@pytest.mark.parametrize("key", generate_invalid_api_key_data())
def test_reject_invalid_api_key(key: str | None):
    settings = make_settings(app={"api_key": key})

    with pytest.raises(
        ValueError, match="^PP_APP__API_KEY must be configured and non-blank$"
    ) as error:
        create_application(settings=settings)

    assert (
        str(error.value) == "PP_APP__API_KEY must be configured and non-blank"
    )

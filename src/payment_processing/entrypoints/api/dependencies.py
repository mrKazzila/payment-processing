from dishka import Provider, Scope, provide

from payment_processing.application.use_cases.create_payment import (
    CreatePayment,
)
from payment_processing.application.use_cases.get_payment import GetPayment
from payment_processing.config.settings import Settings
from payment_processing.presentation.api.security import ApiKeyAuthConfig


class PaymentProvider(Provider):
    scope = Scope.REQUEST

    create_payment = provide(CreatePayment)
    get_payment = provide(GetPayment)

    @provide(scope=Scope.APP)
    def api_key_auth(self, settings: Settings) -> ApiKeyAuthConfig:
        api_key = settings.app.api_key
        return ApiKeyAuthConfig(
            expected_key=(
                api_key.get_secret_value() if api_key is not None else None
            ),
        )

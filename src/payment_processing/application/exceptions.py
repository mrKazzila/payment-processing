from uuid import UUID


class ApplicationError(Exception):
    pass


class PaymentNotFoundError(ApplicationError):
    def __init__(self, *, payment_id: UUID) -> None:
        self.payment_id = payment_id
        super().__init__(f"Payment {payment_id} was not found.")


class IdempotencyConflictError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            "Idempotency key was already used with different data."
        )


class DuplicateIdempotencyKeyError(ApplicationError):
    """Unique key conflict while saving payment."""


class PaymentGatewayUnavailableError(ApplicationError):
    """Failed to get payment processing result."""


class WebhookDeliveryError(ApplicationError):
    """Failed to deliver result notification."""


class MessagePublishError(ApplicationError):
    """Message publication not confirmed."""

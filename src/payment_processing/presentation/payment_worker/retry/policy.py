MAX_PROCESSING_ATTEMPTS = 3
INITIAL_RETRY_DELAY_SECONDS = 2


def get_retry_delay(*, failed_attempt: int) -> float | None:
    if failed_attempt < 1:
        raise ValueError("Attempt number must be positive.")

    if failed_attempt >= MAX_PROCESSING_ATTEMPTS:
        return None

    return float(INITIAL_RETRY_DELAY_SECONDS * 2 ** (failed_attempt - 1))


def validate_attempt(*, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 1 <= value <= MAX_PROCESSING_ATTEMPTS
    ):
        raise ValueError(
            "Processing attempt must be an integer between "
            f"1 and {MAX_PROCESSING_ATTEMPTS}."
        )

    return value

from typing import Annotated

from fastapi import Header

IdempotencyKeyHeader = Annotated[
    str,
    Header(
        alias="Idempotency-Key",
        min_length=1,
        pattern=r"\S",
    ),
]

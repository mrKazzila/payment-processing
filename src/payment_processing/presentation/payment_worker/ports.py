from typing import Protocol

from faststream.rabbit.message import RabbitMessage


class RetryPublisher(Protocol):
    async def publish_retry(
        self,
        *,
        message: RabbitMessage,
        next_attempt: int,
        delay_seconds: float,
    ) -> None: ...

    async def publish_dead_letter(
        self,
        *,
        message: RabbitMessage,
        failed_attempt: int,
    ) -> None: ...

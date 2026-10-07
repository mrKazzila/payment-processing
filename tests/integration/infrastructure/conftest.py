from types import SimpleNamespace
from uuid import uuid4

import aio_pika
import pytest
from faststream.rabbit import Channel, RabbitBroker

from payment_processing.infrastructure.messaging.publisher import (
    RabbitMessagePublisher,
)


@pytest.fixture
async def messaging(rabbitmq_url: str):
    connection = await aio_pika.connect_robust(rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(
            f"test.{uuid4()}", exclusive=True, auto_delete=True
        )
        try:
            async with RabbitBroker(
                rabbitmq_url,
                default_channel=Channel(
                    publisher_confirms=True,
                    on_return_raises=True,
                ),
            ) as broker:
                yield SimpleNamespace(
                    queue=queue,
                    publisher=RabbitMessagePublisher(broker),
                )
        finally:
            await queue.delete(if_unused=False, if_empty=False)

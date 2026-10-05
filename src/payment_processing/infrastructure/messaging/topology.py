from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitQueue,
)
from faststream.rabbit.schemas.queue import ClassicQueueArgs

PAYMENTS_DLX = RabbitExchange(
    "payments.dlx",
    type=ExchangeType.DIRECT,
    durable=True,
)

PAYMENTS_DLQ = RabbitQueue(
    "payments.dlq",
    durable=True,
    routing_key="payments.failed",
)

payments_queue_args: ClassicQueueArgs = {
    "x-dead-letter-exchange": PAYMENTS_DLX.name,
    "x-dead-letter-routing-key": PAYMENTS_DLQ.routing_key,
}

PAYMENTS_QUEUE = RabbitQueue(
    "payments.new",
    durable=True,
    arguments=payments_queue_args,
)


async def declare_topology(*, broker: RabbitBroker) -> None:
    exchange = await broker.declare_exchange(PAYMENTS_DLX)
    queue = await broker.declare_queue(PAYMENTS_DLQ)

    await queue.bind(
        exchange,
        routing_key=PAYMENTS_DLQ.routing_key,
    )

    await broker.declare_queue(PAYMENTS_QUEUE)

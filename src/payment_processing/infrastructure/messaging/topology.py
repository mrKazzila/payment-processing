from faststream.rabbit import (
    ExchangeType,
    QueueType,
    RabbitBroker,
    RabbitExchange,
    RabbitQueue,
)
from faststream.rabbit.schemas.queue import (
    ClassicQueueArgs,
    QuorumQueueArgs,
)

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
PAYMENTS_RETRY_EXCHANGE = RabbitExchange(
    "payments.retry.return",
    type=ExchangeType.DIRECT,
    durable=True,
)


def create_retry_queue(
    *,
    name: str,
    delay_seconds: int,
) -> RabbitQueue:
    arguments: QuorumQueueArgs = {
        "x-message-ttl": delay_seconds * 1000,
        "x-dead-letter-exchange": PAYMENTS_RETRY_EXCHANGE.name,
        "x-dead-letter-routing-key": PAYMENTS_QUEUE.name,
        "x-dead-letter-strategy": "at-least-once",
        "x-overflow": "reject-publish",
    }

    return RabbitQueue(
        name,
        queue_type=QueueType.QUORUM,
        durable=True,
        arguments=arguments,
    )


PAYMENTS_RETRY_QUEUES: dict[float, RabbitQueue] = {
    2.0: create_retry_queue(
        name="payments.retry.2s",
        delay_seconds=2,
    ),
    4.0: create_retry_queue(
        name="payments.retry.4s",
        delay_seconds=4,
    ),
}


async def declare_topology(*, broker: RabbitBroker) -> None:
    dead_letter_exchange = await broker.declare_exchange(
        PAYMENTS_DLX,
    )
    dead_letter_queue = await broker.declare_queue(
        PAYMENTS_DLQ,
    )
    await dead_letter_queue.bind(
        dead_letter_exchange,
        routing_key=PAYMENTS_DLQ.routing_key,
    )

    payments_queue = await broker.declare_queue(PAYMENTS_QUEUE)

    retry_exchange = await broker.declare_exchange(
        PAYMENTS_RETRY_EXCHANGE,
    )
    await payments_queue.bind(
        retry_exchange,
        routing_key=PAYMENTS_QUEUE.name,
    )

    for retry_queue in PAYMENTS_RETRY_QUEUES.values():
        await broker.declare_queue(retry_queue)

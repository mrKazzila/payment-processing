from faststream.specification import AsyncAPI, Contact

WORKER_DESCRIPTION = """
# Payment processing service

Consumer for the `payments.new` queue.

## Responsibilities
- Validate incoming events.
- Process payments through a simulated payment gateway.
- Persist processing results.
- Deliver webhooks with retries.

## Error handling
Invalid messages are sent to the dead-letter queue (DLQ).
Transient failures are retried;
once all attempts are exhausted, the message is sent to the DLQ.
"""


def create_specification(
    *,
    title: str,
    version: str,
) -> AsyncAPI:
    return AsyncAPI(
        title=title,
        version=version,
        description=WORKER_DESCRIPTION,
        contact=Contact(name="mrKazzila"),
        schema_version="3.0.0",
    )

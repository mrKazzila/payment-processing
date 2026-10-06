import asyncio
import signal

from payment_processing.config.settings import get_settings
from payment_processing.entrypoints.outbox_worker.bootstrap import (
    run_application,
)


async def run() -> None:
    settings = get_settings()
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    signals = (signal.SIGINT, signal.SIGTERM)

    for received_signal in signals:
        loop.add_signal_handler(
            received_signal,
            stop_event.set,
        )

    try:
        await run_application(
            settings=settings,
            stop_event=stop_event,
        )
    finally:
        for received_signal in signals:
            loop.remove_signal_handler(received_signal)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()

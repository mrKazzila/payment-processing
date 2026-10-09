import asyncio
import signal

from payment_processing.presentation.outbox_worker.application import (
    OutboxApplication,
)


async def _run_app(*, app: OutboxApplication) -> None:
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    installed_signals: list[signal.Signals] = []

    try:
        for received_signal in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                received_signal,
                stop_event.set,
            )
            installed_signals.append(received_signal)

        await app.run(stop_event=stop_event)
    finally:
        for received_signal in installed_signals:
            loop.remove_signal_handler(received_signal)


def run_app(*, app: OutboxApplication) -> None:
    asyncio.run(_run_app(app=app))

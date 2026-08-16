#!/usr/bin/env python3
"""Exercise the real py-trinnov-altitude client against a live device the same
way the Home Assistant coordinator does, and log every runtime/power state
transition with timestamps. Meant to reproduce the network-standby wake flow
end-to-end (client.start() while off -> client.power_on() -> watch until
synced) so we can see exactly where/why it diverges from a normal wake.

Usage:
    python3 trinnov_lifecycle_probe.py <ip> <mac> [max-seconds]

Requires the sibling py-trinnov-altitude checkout on PYTHONPATH.
"""

import asyncio
import sys
import time

sys.path.insert(0, "/Users/adam/Development/py-trinnov-altitude")

from trinnov_altitude.client import TrinnovAltitudeClient  # noqa: E402
from trinnov_altitude import exceptions  # noqa: E402


async def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    host = sys.argv[1]
    mac = sys.argv[2]
    max_seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 180.0

    t0 = time.monotonic()

    def ts() -> str:
        return f"+{time.monotonic() - t0:6.2f}s"

    def log(msg: str) -> None:
        print(f"[{ts()}] {msg}")

    last_runtime = None

    def on_event(event: str, message: object) -> None:
        nonlocal last_runtime
        if event == "received_message":
            return
        log(f"EVENT: {event}")

    client = TrinnovAltitudeClient(host=host, mac=mac, reconnect_max_backoff=10.0)
    client.register_callback(on_event)

    log("Calling client.start() (expect this to fail since device is off)...")
    try:
        await client.start()
        log("client.start() succeeded immediately (device was already reachable).")
    except (exceptions.ConnectionFailedError, exceptions.ConnectionTimeoutError) as err:
        log(f"client.start() raised as expected: {type(err).__name__}: {err}")
        log("Scheduling background retry loop (mirrors coordinator._schedule_bootstrap_retry)...")

        async def retry_until_synced() -> None:
            while not client.state.synced:
                try:
                    await client.start()
                    await client.wait_synced(timeout=5.0)
                    if client.state.synced:
                        return
                except (exceptions.ConnectionFailedError, exceptions.ConnectionTimeoutError, asyncio.TimeoutError):
                    pass
                await asyncio.sleep(5.0)

        retry_task = asyncio.create_task(retry_until_synced())

        log("Calling client.power_on() (sends WOL magic packet)...")
        client.power_on()
        log(f"runtime.power = {client.runtime.power}")

        deadline = time.monotonic() + max_seconds
        last_power = None
        last_transport = None
        last_sync = None
        while time.monotonic() < deadline:
            if (
                client.runtime.power != last_power
                or client.runtime.transport != last_transport
                or client.runtime.sync != last_sync
            ):
                log(
                    f"runtime: power={client.runtime.power} transport={client.runtime.transport} "
                    f"sync={client.runtime.sync} control={client.runtime.control} "
                    f"state.synced={client.state.synced}"
                )
                last_power, last_transport, last_sync = (
                    client.runtime.power,
                    client.runtime.transport,
                    client.runtime.sync,
                )
            if client.state.synced:
                log("SYNCED. Success.")
                break
            await asyncio.sleep(0.5)
        else:
            log(f"TIMED OUT after {max_seconds}s without becoming synced.")

        retry_task.cancel()

    await client.stop()
    log("Stopped.")


if __name__ == "__main__":
    asyncio.run(main())

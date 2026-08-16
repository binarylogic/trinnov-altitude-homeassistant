#!/usr/bin/env python3
"""Standalone Trinnov Altitude control-port probe (no dependencies).

Connects to the Altitude's control TCP port (default 44100) and logs, with
timestamps, exactly what happens: whether the connect succeeds/fails/times
out, and whatever raw lines the device sends after we say "id" and ask for
"get_current_state". Run this once with the device fully ON, and once with
it in the new network-standby mode, and compare the two logs.

Usage:
    python3 trinnov_probe.py <altitude-ip> [port]

Ctrl+C to stop. It will keep listening for up to 15s after sending commands
so we can see if anything trickles in late.
"""

import socket
import sys
import time


def ts() -> str:
    return time.strftime("%H:%M:%S")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 44100

    print(f"[{ts()}] Connecting to {host}:{port} (connect timeout 5s)...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    start = time.monotonic()
    try:
        sock.connect((host, port))
    except Exception as err:
        print(f"[{ts()}] CONNECT FAILED after {time.monotonic() - start:.2f}s: {type(err).__name__}: {err}")
        return
    print(f"[{ts()}] CONNECT OK after {time.monotonic() - start:.2f}s")

    sock.settimeout(3.0)

    def read_for(seconds: float) -> None:
        deadline = time.monotonic() + seconds
        buf = b""
        while time.monotonic() < deadline:
            remaining = max(0.1, deadline - time.monotonic())
            sock.settimeout(min(3.0, remaining))
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                continue
            except Exception as err:
                print(f"[{ts()}] READ ERROR: {type(err).__name__}: {err}")
                return
            if chunk == b"":
                print(f"[{ts()}] PEER CLOSED CONNECTION")
                return
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                print(f"[{ts()}] RECV: {line!r}")

    print(f"[{ts()}] Listening for any unsolicited data for 5s before sending anything...")
    read_for(5.0)

    for cmd in ["id trinnov_probe", "get_current_state", "upmixer"]:
        try:
            print(f"[{ts()}] SEND: {cmd!r}")
            sock.sendall((cmd + "\n").encode("ascii"))
        except Exception as err:
            print(f"[{ts()}] SEND FAILED: {type(err).__name__}: {err}")
            return
        read_for(3.0)

    print(f"[{ts()}] Final listen window (10s)...")
    read_for(10.0)

    sock.close()
    print(f"[{ts()}] Done.")


if __name__ == "__main__":
    main()

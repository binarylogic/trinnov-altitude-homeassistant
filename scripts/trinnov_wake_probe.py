#!/usr/bin/env python3
"""Send a Wake-on-LAN magic packet, then poll the Trinnov control port until
it accepts a connection, and log the full handshake with timestamps relative
to the WOL send. This is meant to compare a "fast boot" wake (from the new
network-standby mode) against a normal cold boot.

Usage:
    python3 trinnov_wake_probe.py <altitude-ip> <mac-address> [port]
"""

import re
import socket
import struct
import sys
import time


def send_magic_packet(mac: str, broadcast: str = "255.255.255.255", port: int = 9) -> None:
    mac_bytes = bytes.fromhex(re.sub(r"[:-]", "", mac))
    packet = b"\xff" * 6 + mac_bytes * 16
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(packet, (broadcast, port))
    sock.close()


def ts(t0: float) -> str:
    return f"+{time.monotonic() - t0:6.2f}s"


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    host = sys.argv[1]
    mac = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 44100

    t0 = time.monotonic()
    print(f"[{ts(t0)}] Sending WOL magic packet to {mac}...")
    send_magic_packet(mac)

    print(f"[{ts(t0)}] Polling {host}:{port} every 0.25s until it accepts a connection (giving up after 60s)...")
    sock: socket.socket | None = None
    deadline = time.monotonic() + 60
    attempts = 0
    while time.monotonic() < deadline:
        attempts += 1
        candidate = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        candidate.settimeout(0.5)
        try:
            candidate.connect((host, port))
            sock = candidate
            break
        except Exception:
            candidate.close()
            time.sleep(0.25)

    if sock is None:
        print(f"[{ts(t0)}] Gave up after {attempts} attempts; never connected.")
        return

    print(f"[{ts(t0)}] CONNECTED after {attempts} attempts.")
    sock.settimeout(2.0)

    def read_for(seconds: float) -> None:
        deadline_inner = time.monotonic() + seconds
        buf = b""
        while time.monotonic() < deadline_inner:
            remaining = max(0.1, deadline_inner - time.monotonic())
            sock.settimeout(min(2.0, remaining))
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                continue
            except Exception as err:
                print(f"[{ts(t0)}] READ ERROR: {type(err).__name__}: {err}")
                return
            if chunk == b"":
                print(f"[{ts(t0)}] PEER CLOSED CONNECTION")
                return
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                print(f"[{ts(t0)}] RECV: {line!r}")

    read_for(3.0)

    for cmd in ["id trinnov_probe", "get_current_state", "upmixer"]:
        try:
            print(f"[{ts(t0)}] SEND: {cmd!r}")
            sock.sendall((cmd + "\n").encode("ascii"))
        except Exception as err:
            print(f"[{ts(t0)}] SEND FAILED: {type(err).__name__}: {err}")
            return
        read_for(3.0)

    print(f"[{ts(t0)}] Final listen window (10s)...")
    read_for(10.0)

    sock.close()
    print(f"[{ts(t0)}] Done.")


if __name__ == "__main__":
    main()

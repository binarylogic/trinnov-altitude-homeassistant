"""Command service for Trinnov Altitude integration."""

from __future__ import annotations

from typing import Any

from trinnov_altitude.client import TrinnovAltitudeClient


class TrinnovAltitudeCommands:
    """Centralized command execution and optional ACK policy."""

    def __init__(self, client: TrinnovAltitudeClient) -> None:
        """Initialize command service."""
        self._client = client

    async def invoke(
        self, method_name: str, *args: Any, require_ack: bool = False
    ) -> None:
        """Invoke a client command by method name, with optional ACK wait."""
        if require_ack:
            line = self._build_line(method_name, args)
            if line is not None:
                await self._client.command(
                    line,
                    wait_for_ack=True,
                    ack_timeout=self._client.command_timeout,
                )
                return

        await getattr(self._client, method_name)(*args)

    def _build_line(self, method_name: str, args: tuple[Any, ...]) -> str | None:
        """Build raw protocol line for known methods."""
        if method_name == "power_off":
            return "power_off_SECURED_FHZMCH48FE"
        if method_name == "preset_set" and len(args) == 1:
            return f"loadp {int(args[0])}"
        if method_name == "source_set" and len(args) == 1:
            return f"profile {int(args[0])}"
        if method_name == "source_set_by_name" and len(args) == 1:
            source_name = str(args[0])
            for source_id, name in self._client.state.sources.items():
                if name == source_name:
                    return f"profile {source_id}"
            raise ValueError(f"Unknown source name: {source_name}")
        if method_name == "upmixer_set" and len(args) == 1:
            mode = args[0]
            mode_value = mode.value if hasattr(mode, "value") else str(mode)
            return f"upmixer {mode_value}"
        if method_name == "remapping_mode_set" and len(args) == 1:
            mode = args[0]
            mode_value = mode.value if hasattr(mode, "value") else str(mode)
            return f"remapping_mode {mode_value}"
        return None

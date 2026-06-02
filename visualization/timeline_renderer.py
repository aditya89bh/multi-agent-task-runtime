"""Render runtime events as a human-readable timeline."""

from __future__ import annotations

from typing import Iterable, List

from events.event import Event


class TimelineRenderer:
    """Converts chronological events into readable lines."""

    def render(self, events: Iterable[Event]) -> str:
        """Render events sorted by timestamp."""
        lines: List[str] = []
        for event in sorted(events, key=lambda item: item.timestamp):
            agent = event.agent_id or "system"
            payload = self._format_payload(event.payload)
            lines.append(f"{event.timestamp} | {agent} | {event.event_type} | {payload}")
        return "\n".join(lines)

    @staticmethod
    def _format_payload(payload: dict) -> str:
        if not payload:
            return "{}"
        return ", ".join(f"{key}={value!r}" for key, value in sorted(payload.items()))

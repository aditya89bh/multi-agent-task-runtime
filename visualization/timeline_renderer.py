"""Render runtime events as a human-readable timeline."""

from __future__ import annotations

from collections.abc import Iterable

from events.event import Event
from events.filters import filter_events


class TimelineRenderer:
    """Converts chronological events into readable lines."""

    def render(
        self,
        events: Iterable[Event],
        event_type: str | None = None,
        agent_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> str:
        """Render events sorted by timestamp, with optional filters."""
        selected = filter_events(events, event_type, agent_id, start_time, end_time)
        lines: list[str] = []
        for event in sorted(selected, key=lambda item: item.timestamp):
            agent = event.agent_id or "system"
            payload = self._format_payload(event.payload)
            lines.append(f"{event.timestamp} | {agent} | {event.event_type} | {payload}")
        return "\n".join(lines)

    @staticmethod
    def _format_payload(payload: dict) -> str:
        if not payload:
            return "{}"
        return ", ".join(f"{key}={value!r}" for key, value in sorted(payload.items()))

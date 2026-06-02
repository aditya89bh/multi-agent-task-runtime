"""Reusable event filtering helpers."""

from __future__ import annotations

from collections.abc import Iterable

from events.event import Event


def filter_events(
    events: Iterable[Event],
    event_type: str | None = None,
    agent_id: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
) -> list[Event]:
    """Filter events by type, agent, and timestamp window."""
    filtered: list[Event] = []
    for event in events:
        if event_type is not None and event.event_type != event_type:
            continue
        if agent_id is not None and event.agent_id != agent_id:
            continue
        if start_time is not None and event.timestamp < start_time:
            continue
        if end_time is not None and event.timestamp > end_time:
            continue
        filtered.append(event)
    return filtered

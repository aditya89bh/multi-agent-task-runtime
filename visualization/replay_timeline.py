"""Concise replay timeline rendering."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from events.event import Event
from events.filters import filter_events
from events import event_types

_LABELS = {
    event_types.AGENT_STARTED: "{agent} started",
    event_types.AGENT_FINISHED: "{agent} finished",
    event_types.MEMORY_READ: "Memory read",
    event_types.MEMORY_WRITE: "Memory write",
    event_types.TOOL_CALLED: "Tool call",
    event_types.TOOL_RETURNED: "Tool returned",
    event_types.CONFIDENCE_UPDATED: "Confidence updated",
    event_types.FAILURE_OCCURRED: "Failure occurred",
    event_types.RETRY_STARTED: "Retry started",
    event_types.RETRY_COMPLETED: "Retry completed",
    event_types.DRIFT_DETECTED: "Drift detected",
}


class ReplayTimelineRenderer:
    """Generate short readable timeline lines from replayed events."""

    def render(
        self,
        events: Iterable[Event],
        event_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> str:
        selected = filter_events(events, event_type, agent_id, start_time, end_time)
        lines: List[str] = []
        for event in sorted(selected, key=lambda item: item.timestamp):
            lines.append(f"[{self._time(event.timestamp)}] {self._label(event)}")
        return "\n".join(lines)

    @staticmethod
    def _time(timestamp: str) -> str:
        return datetime.fromisoformat(timestamp).strftime("%H:%M:%S")

    @staticmethod
    def _label(event: Event) -> str:
        agent = (event.agent_id or "system").replace("_", " ").title()
        template = _LABELS.get(event.event_type, event.event_type.replace("_", " ").title())
        return template.format(agent=agent)

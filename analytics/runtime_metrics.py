"""Runtime-wide event metrics."""

from __future__ import annotations

from collections.abc import Iterable

from events import event_types
from events.event import Event


class RuntimeMetricsCollector:
    """Summarize high-level runtime event counts."""

    def summarize(self, events: Iterable[Event]) -> dict[str, int]:
        event_list = list(events)
        return {
            "total_events": len(event_list),
            "tool_calls": self._count(event_list, event_types.TOOL_CALLED),
            "memory_reads": self._count(event_list, event_types.MEMORY_READ),
            "memory_writes": self._count(event_list, event_types.MEMORY_WRITE),
            "failures": self._count(event_list, event_types.FAILURE_OCCURRED),
            "retries": self._count(event_list, event_types.RETRY_STARTED),
        }

    @staticmethod
    def _count(events: Iterable[Event], event_type: str) -> int:
        return sum(1 for event in events if event.event_type == event_type)

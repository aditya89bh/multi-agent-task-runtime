"""Memory access analytics."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import Any

from events import event_types
from events.event import Event


class MemoryMetricsCollector:
    """Summarize memory reads, writes, and key access frequency."""

    def summarize(self, events: Iterable[Event]) -> dict[str, Any]:
        read_count = 0
        write_count = 0
        key_accesses: Counter[str] = Counter()
        for event in events:
            if event.event_type not in {event_types.MEMORY_READ, event_types.MEMORY_WRITE}:
                continue
            key = event.payload.get("key")
            if key is not None:
                key_accesses[str(key)] += 1
            if event.event_type == event_types.MEMORY_READ:
                read_count += 1
            elif event.event_type == event_types.MEMORY_WRITE:
                write_count += 1
        return {
            "read_count": read_count,
            "write_count": write_count,
            "most_accessed_keys": key_accesses.most_common(),
            "access_frequency": dict(key_accesses),
        }

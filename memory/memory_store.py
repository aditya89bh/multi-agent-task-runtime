"""Observable in-memory key-value store."""

from __future__ import annotations

from typing import Any

from events.event import Event
from events.event_types import MEMORY_READ, MEMORY_WRITE
from runtime.event_bus import EventBus


class MemoryStore:
    """A small memory store that emits read/write events."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self._memory: dict[str, Any] = {}

    def write(self, key: str, value: Any, agent_id: str | None = None) -> Any:
        """Write a value and emit MEMORY_WRITE."""
        self._memory[key] = value
        self.event_bus.publish(
            Event(
                event_type=MEMORY_WRITE,
                agent_id=agent_id,
                payload={"key": key, "value": value},
            )
        )
        return value

    def read(self, key: str, agent_id: str | None = None, default: Any = None) -> Any:
        """Read a value and emit MEMORY_READ."""
        value = self._memory.get(key, default)
        self.event_bus.publish(
            Event(
                event_type=MEMORY_READ,
                agent_id=agent_id,
                payload={"key": key, "value": value, "found": key in self._memory},
            )
        )
        return value

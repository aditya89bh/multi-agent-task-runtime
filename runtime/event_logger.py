"""JSONL event persistence for runtime observability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from events.event import Event
from runtime.event_bus import EventBus

PathLike = Union[str, Path]


class EventLogger:
    """Subscriber that writes every event to a JSONL file."""

    def __init__(self, event_bus: EventBus, output_path: PathLike = "logs/runtime_events.jsonl") -> None:
        self.event_bus = event_bus
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.event_bus.subscribe(self.handle_event)

    def handle_event(self, event: Event) -> None:
        """Persist one event as a JSON line."""
        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")

    def close(self) -> None:
        """Unsubscribe this logger from the event bus."""
        self.event_bus.unsubscribe(self.handle_event)

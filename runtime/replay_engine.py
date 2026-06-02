"""Replay runtime events from persisted logs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator, List, Union

from events.event import Event
from runtime.sqlite_store import SQLiteEventStore
from visualization.timeline_renderer import TimelineRenderer

PathLike = Union[str, Path]


class ReplayEngine:
    """Loads and replays persisted event streams."""

    def load_jsonl(self, path: PathLike) -> List[Event]:
        """Load events from a JSONL log file."""
        events: List[Event] = []
        with Path(path).open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                record = json.loads(line)
                events.append(Event(**record))
        return events

    def load_sqlite(self, db_path: PathLike) -> List[Event]:
        """Load events from SQLite storage."""
        return SQLiteEventStore(db_path).retrieve_events()

    def replay(self, events: Iterable[Event]) -> Iterator[Event]:
        """Yield events sequentially by timestamp."""
        yield from sorted(events, key=lambda event: event.timestamp)

    def reconstruct_timeline(self, events: Iterable[Event]) -> str:
        """Build a human-readable timeline from events."""
        return TimelineRenderer().render(self.replay(events))

"""Replay runtime events from persisted logs."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from events.event import Event
from runtime.sqlite_store import SQLiteEventStore
from visualization.timeline_renderer import TimelineRenderer

PathLike = str | Path


@dataclass(frozen=True)
class ReplaySummary:
    """Summary of a replay log load operation."""

    events: list[Event]
    skipped_events: int = 0
    skipped_lines: tuple[int, ...] = ()


class ReplayEngine:
    """Loads and replays persisted event streams."""

    def __init__(self) -> None:
        self.last_summary = ReplaySummary(events=[])

    def load_jsonl(self, path: PathLike) -> list[Event]:
        """Load valid events from a JSONL log file, skipping corrupted entries."""
        summary = self.load_jsonl_with_summary(path)
        return summary.events

    def load_jsonl_with_summary(self, path: PathLike) -> ReplaySummary:
        """Load JSONL events and expose corruption recovery statistics."""
        events: list[Event] = []
        skipped_lines: list[int] = []
        with Path(path).open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        raise ValueError("event record must be an object")
                    events.append(Event(**record))
                except (TypeError, ValueError, json.JSONDecodeError):
                    skipped_lines.append(line_number)
        self.last_summary = ReplaySummary(events=events, skipped_events=len(skipped_lines), skipped_lines=tuple(skipped_lines))
        return self.last_summary

    def load_sqlite(self, db_path: PathLike) -> list[Event]:
        """Load events from SQLite storage."""
        events = SQLiteEventStore(db_path).retrieve_events()
        self.last_summary = ReplaySummary(events=events)
        return events

    def replay(self, events: Iterable[Event]) -> Iterator[Event]:
        """Yield events sequentially by timestamp."""
        yield from sorted(events, key=lambda event: event.timestamp)

    def reconstruct_timeline(self, events: Iterable[Event]) -> str:
        """Build a human-readable timeline from events."""
        return TimelineRenderer().render(self.replay(events))

"""SQLite-backed event storage."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional, Union

from events.event import Event

PathLike = Union[str, Path]


class SQLiteEventStore:
    """Persist runtime events to SQLite."""

    def __init__(self, db_path: PathLike) -> None:
        self.db_path = Path(db_path)
        if self.db_path.parent != Path("."):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def store_event(self, event: Event) -> None:
        """Store one event, preserving all event fields."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO events (event_type, timestamp, agent_id, payload)
                VALUES (?, ?, ?, ?)
                """,
                (
                    event.event_type,
                    event.timestamp,
                    event.agent_id,
                    json.dumps(event.payload, sort_keys=True),
                ),
            )

    def store_events(self, events: Iterable[Event]) -> None:
        """Store multiple events."""
        for event in events:
            self.store_event(event)

    def retrieve_events(self) -> List[Event]:
        """Retrieve all stored events in insertion order."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT event_type, timestamp, agent_id, payload FROM events ORDER BY id ASC"
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    payload TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> Event:
        return Event(
            event_type=row["event_type"],
            timestamp=row["timestamp"],
            agent_id=row["agent_id"],
            payload=json.loads(row["payload"]),
        )

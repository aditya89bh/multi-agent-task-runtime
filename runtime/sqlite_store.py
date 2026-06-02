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
                INSERT INTO events (event_type, timestamp, agent_id, payload, schema_version)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event.event_type,
                    event.timestamp,
                    event.agent_id,
                    json.dumps(event.payload, sort_keys=True),
                    event.schema_version,
                ),
            )

    def store_events(self, events: Iterable[Event]) -> None:
        """Store multiple events."""
        for event in events:
            self.store_event(event)

    def retrieve_events(self) -> List[Event]:
        """Retrieve all stored events in insertion order."""
        return self.get_events()

    def get_events(
        self,
        event_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[Event]:
        """Query events by type, agent, and optional timestamp range."""
        clauses = []
        params = []
        if event_type is not None:
            clauses.append("event_type = ?")
            params.append(event_type)
        if agent_id is not None:
            clauses.append("agent_id = ?")
            params.append(agent_id)
        if start_time is not None:
            clauses.append("timestamp >= ?")
            params.append(start_time)
        if end_time is not None:
            clauses.append("timestamp <= ?")
            params.append(end_time)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT event_type, timestamp, agent_id, payload, schema_version FROM events{where} ORDER BY id ASC",
                params,
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
                    payload TEXT NOT NULL,
                    schema_version TEXT NOT NULL DEFAULT '1.0'
                )
                """
            )
            columns = {row[1] for row in conn.execute("PRAGMA table_info(events)").fetchall()}
            if "schema_version" not in columns:
                conn.execute("ALTER TABLE events ADD COLUMN schema_version TEXT NOT NULL DEFAULT '1.0'")

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
            schema_version=row["schema_version"],
        )

from events.event import Event
from events.event_types import AGENT_STARTED, FAILURE_OCCURRED, MEMORY_WRITE
from runtime.sqlite_store import SQLiteEventStore


def test_sqlite_event_store_creates_database_and_persists_all_event_fields(tmp_path):
    db_path = tmp_path / "events.db"
    store = SQLiteEventStore(db_path)
    event = Event(
        event_type=AGENT_STARTED,
        timestamp="2026-01-01T10:00:00+00:00",
        agent_id="planner",
        payload={"task": "plan"},
    )

    store.store_event(event)
    retrieved = store.retrieve_events()

    assert db_path.exists()
    assert retrieved == [event]
    assert retrieved[0].schema_version == "1.0"


def test_sqlite_event_store_persists_multiple_events_in_order(tmp_path):
    store = SQLiteEventStore(tmp_path / "events.db")
    first = Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:00+00:00", agent_id="planner")
    second = Event(event_type=MEMORY_WRITE, timestamp="2026-01-01T10:00:01+00:00", agent_id="planner", payload={"key": "plan"})

    store.store_events([first, second])

    assert store.retrieve_events() == [first, second]


def test_sqlite_event_store_filters_by_type_agent_and_time_range(tmp_path):
    store = SQLiteEventStore(tmp_path / "events.db")
    first = Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:00+00:00", agent_id="planner")
    second = Event(event_type=FAILURE_OCCURRED, timestamp="2026-01-01T10:00:02+00:00", agent_id="writer")
    third = Event(event_type=MEMORY_WRITE, timestamp="2026-01-01T10:00:04+00:00", agent_id="planner")
    store.store_events([first, second, third])

    assert store.get_events(event_type=FAILURE_OCCURRED) == [second]
    assert store.get_events(agent_id="planner") == [first, third]
    assert store.get_events(
        start_time="2026-01-01T10:00:01+00:00",
        end_time="2026-01-01T10:00:03+00:00",
    ) == [second]


def test_sqlite_event_store_records_schema_version(tmp_path):
    store = SQLiteEventStore(tmp_path / "events.db")

    assert store.schema_version() == SQLiteEventStore.CURRENT_SCHEMA_VERSION


def test_sqlite_event_store_migrates_legacy_database(tmp_path):
    import sqlite3

    db_path = tmp_path / "legacy.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                agent_id TEXT,
                payload TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO events (event_type, timestamp, agent_id, payload) VALUES (?, ?, ?, ?)",
            (AGENT_STARTED, "2026-01-01T10:00:00+00:00", "planner", "{}"),
        )

    store = SQLiteEventStore(db_path)

    assert store.schema_version() == SQLiteEventStore.CURRENT_SCHEMA_VERSION
    assert store.retrieve_events()[0].schema_version == "1.0"

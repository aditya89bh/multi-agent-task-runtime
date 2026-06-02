from events.event import Event
from events.event_types import AGENT_STARTED, MEMORY_WRITE
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


def test_sqlite_event_store_persists_multiple_events_in_order(tmp_path):
    store = SQLiteEventStore(tmp_path / "events.db")
    first = Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:00+00:00", agent_id="planner")
    second = Event(event_type=MEMORY_WRITE, timestamp="2026-01-01T10:00:01+00:00", agent_id="planner", payload={"key": "plan"})

    store.store_events([first, second])

    assert store.retrieve_events() == [first, second]

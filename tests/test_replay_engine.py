import json

from events.event import Event
from events.event_types import AGENT_STARTED, MEMORY_WRITE
from runtime.replay_engine import ReplayEngine
from runtime.sqlite_store import SQLiteEventStore


def test_replay_engine_loads_jsonl_and_replays_sequentially(tmp_path):
    path = tmp_path / "events.jsonl"
    later = Event(event_type=MEMORY_WRITE, timestamp="2026-01-01T10:00:02+00:00", agent_id="planner")
    earlier = Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:01+00:00", agent_id="planner")
    path.write_text("\n".join(json.dumps(event.to_dict()) for event in [later, earlier]), encoding="utf-8")

    engine = ReplayEngine()
    events = engine.load_jsonl(path)

    assert events == [later, earlier]
    assert list(engine.replay(events)) == [earlier, later]


def test_replay_engine_loads_sqlite_and_reconstructs_timeline(tmp_path):
    db_path = tmp_path / "events.db"
    store = SQLiteEventStore(db_path)
    event = Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:01+00:00", agent_id="planner")
    store.store_event(event)

    engine = ReplayEngine()
    timeline = engine.reconstruct_timeline(engine.load_sqlite(db_path))

    assert "planner" in timeline
    assert AGENT_STARTED in timeline

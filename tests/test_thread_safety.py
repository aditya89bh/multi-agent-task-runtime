from concurrent.futures import ThreadPoolExecutor

from events.event import Event
from events.event_types import AGENT_STARTED
from runtime.event_bus import EventBus
from runtime.event_logger import EventLogger
from runtime.replay_engine import ReplayEngine
from runtime.sqlite_store import SQLiteEventStore


def test_event_bus_logger_and_sqlite_store_are_thread_safe(tmp_path):
    bus = EventBus()
    logger = EventLogger(bus, tmp_path / "events.jsonl")
    store = SQLiteEventStore(tmp_path / "events.db")
    bus.subscribe(store.store_event)

    def publish(index: int) -> None:
        bus.publish(Event(event_type=AGENT_STARTED, agent_id=f"agent-{index % 5}", payload={"index": index}))

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(publish, range(200)))

    logger.close()
    logged_events = ReplayEngine().load_jsonl(tmp_path / "events.jsonl")
    stored_events = store.retrieve_events()

    assert len(logged_events) == 200
    assert len(stored_events) == 200
    assert {event.payload["index"] for event in stored_events} == set(range(200))

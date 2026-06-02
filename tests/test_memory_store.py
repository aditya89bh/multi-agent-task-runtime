from events.event_types import MEMORY_READ, MEMORY_WRITE
from memory.memory_store import MemoryStore
from runtime.event_bus import EventBus


def test_memory_store_emits_write_and_read_events():
    bus = EventBus()
    events = []
    bus.subscribe(events.append)
    store = MemoryStore(bus)

    store.write("plan", {"status": "draft"}, agent_id="planner")
    value = store.read("plan", agent_id="researcher")

    assert value == {"status": "draft"}
    assert [event.event_type for event in events] == [MEMORY_WRITE, MEMORY_READ]
    assert events[0].payload == {"key": "plan", "value": {"status": "draft"}}
    assert events[1].payload == {"key": "plan", "value": {"status": "draft"}, "found": True}


def test_memory_store_read_miss_emits_found_false():
    bus = EventBus()
    events = []
    bus.subscribe(events.append)
    store = MemoryStore(bus)

    assert store.read("missing", agent_id="planner") is None
    assert events[0].event_type == MEMORY_READ
    assert events[0].payload["found"] is False

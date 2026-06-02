import json

from events.event import Event
from events.event_types import AGENT_STARTED
from runtime.event_bus import EventBus
from runtime.event_logger import EventLogger


def test_event_logger_writes_events_to_jsonl(tmp_path):
    bus = EventBus()
    output = tmp_path / "runtime_events.jsonl"
    logger = EventLogger(bus, output_path=output)

    bus.publish(Event(event_type=AGENT_STARTED, agent_id="planner", payload={"task": "plan"}))
    logger.close()

    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["event_type"] == AGENT_STARTED
    assert record["agent_id"] == "planner"
    assert record["payload"] == {"task": "plan"}


def test_event_logger_can_unsubscribe(tmp_path):
    bus = EventBus()
    output = tmp_path / "runtime_events.jsonl"
    logger = EventLogger(bus, output_path=output)
    logger.close()

    bus.publish(Event(event_type=AGENT_STARTED, agent_id="planner"))

    assert not output.exists()

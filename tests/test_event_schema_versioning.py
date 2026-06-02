from events.event import Event
from events.event_types import AGENT_STARTED


def test_event_schema_version_defaults_to_one_point_zero():
    event = Event(event_type=AGENT_STARTED)

    assert event.schema_version == "1.0"
    assert event.to_dict()["schema_version"] == "1.0"


def test_event_creation_remains_backwards_compatible_without_schema_version():
    record = {"event_type": AGENT_STARTED, "agent_id": "planner", "payload": {}, "timestamp": "2026-01-01T10:00:00+00:00"}

    event = Event(**record)

    assert event.schema_version == "1.0"

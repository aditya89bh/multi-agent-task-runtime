from events.event import Event
from events.event_types import AGENT_STARTED


def test_event_model_serializes_to_dict():
    event = Event(
        event_type=AGENT_STARTED,
        agent_id="planner",
        payload={"task": "plan"},
    )

    assert event.to_dict()["event_type"] == AGENT_STARTED
    assert event.to_dict()["agent_id"] == "planner"
    assert event.to_dict()["payload"] == {"task": "plan"}
    assert event.timestamp

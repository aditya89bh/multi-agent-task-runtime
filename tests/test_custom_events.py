import json

import pytest

from events.event import Event
from events.registry import is_registered_event_type, register_event_type
from runtime.event_bus import EventBus
from runtime.event_logger import EventLogger
from runtime.replay_engine import ReplayEngine


def test_custom_event_registration_and_publishing_logging_replay(tmp_path):
    event_type = register_event_type("planning_decision")
    assert is_registered_event_type(event_type)
    event = Event(event_type=event_type, agent_id="planner", payload={"plan": "A"})
    received = []
    bus = EventBus()
    bus.subscribe(received.append)
    logger = EventLogger(bus, tmp_path / "events.jsonl")

    bus.publish(event)
    logger.close()

    assert received == [event]
    assert ReplayEngine().load_jsonl(tmp_path / "events.jsonl") == [event]


def test_custom_event_names_are_validated():
    with pytest.raises(ValueError):
        register_event_type("Bad Event")
    with pytest.raises(ValueError):
        Event(event_type="Bad Event")

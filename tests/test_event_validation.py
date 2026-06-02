import pytest

from events.event import Event
from events.event_types import AGENT_STARTED


def test_event_accepts_valid_fields():
    event = Event(
        event_type=AGENT_STARTED,
        agent_id="agent-1:planner",
        payload={"nested": {"ok": True}},
        timestamp="2026-01-01T10:00:00+00:00",
        schema_version="1.0",
    )

    assert event.event_type == AGENT_STARTED


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("event_type", "Bad Event"),
        ("agent_id", "bad agent"),
        ("payload", []),
        ("timestamp", "not-a-time"),
        ("schema_version", "1"),
    ],
)
def test_event_rejects_malformed_fields(field, value):
    kwargs = {
        "event_type": AGENT_STARTED,
        "agent_id": "planner",
        "payload": {},
        "timestamp": "2026-01-01T10:00:00+00:00",
        "schema_version": "1.0",
    }
    kwargs[field] = value

    with pytest.raises((TypeError, ValueError)):
        Event(**kwargs)


def test_event_rejects_non_json_payload():
    with pytest.raises(TypeError):
        Event(event_type=AGENT_STARTED, payload={"bad": object()})

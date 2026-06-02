import pytest

from analytics.confidence_tracker import ConfidenceTracker
from events.event_types import CONFIDENCE_UPDATED
from runtime.event_bus import EventBus


def test_confidence_tracker_records_history_and_emits_events():
    bus = EventBus()
    events = []
    bus.subscribe(events.append)
    tracker = ConfidenceTracker(bus)

    tracker.update_confidence("planner", 0.7, reason="initial plan")
    tracker.update_confidence("planner", 0.9, reason="tool validated")

    assert tracker.history_for("planner") == [0.7, 0.9]
    assert [event.event_type for event in events] == [CONFIDENCE_UPDATED, CONFIDENCE_UPDATED]
    assert events[0].payload == {"confidence": 0.7, "reason": "initial plan"}


def test_confidence_tracker_rejects_invalid_confidence():
    tracker = ConfidenceTracker(EventBus())

    with pytest.raises(ValueError):
        tracker.update_confidence("planner", 1.2)

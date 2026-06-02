from analytics.drift_detector import DriftDetector
from events.event import Event
from events.event_types import CONFIDENCE_UPDATED, DRIFT_DETECTED, FAILURE_OCCURRED, MEMORY_READ
from runtime.event_bus import EventBus


def test_drift_detector_detects_confidence_decay_and_emits_event():
    bus = EventBus()
    emitted = []
    bus.subscribe(emitted.append)
    detector = DriftDetector(bus)

    detections = detector.analyze(
        [
            Event(event_type=CONFIDENCE_UPDATED, agent_id="planner", payload={"confidence": 0.9}),
            Event(event_type=CONFIDENCE_UPDATED, agent_id="planner", payload={"confidence": 0.4}),
        ]
    )

    assert len(detections) == 1
    assert emitted == detections
    assert detections[0].event_type == DRIFT_DETECTED
    assert detections[0].payload["drift_type"] == "confidence_decay"


def test_drift_detector_detects_repeated_failures_changing_plans_and_memory_misses():
    detector = DriftDetector(EventBus())
    detections = detector.analyze(
        [
            Event(event_type=FAILURE_OCCURRED, agent_id="writer"),
            Event(event_type=FAILURE_OCCURRED, agent_id="writer"),
            Event(event_type="planning_decision", payload={"plan": "A"}),
            Event(event_type="planning_decision", payload={"plan": "B"}),
            Event(event_type=MEMORY_READ, payload={"key": "a", "found": False}),
            Event(event_type=MEMORY_READ, payload={"key": "b", "found": False}),
        ]
    )

    drift_types = {event.payload["drift_type"] for event in detections}
    assert drift_types == {"repeated_failures", "changing_plans", "inconsistent_memory_access"}

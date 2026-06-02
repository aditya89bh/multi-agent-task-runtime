from analytics.drift_detector import DriftDetector
from events.event import Event
from events.event_types import (
    CONFIDENCE_UPDATED,
    DRIFT_DETECTED,
    FAILURE_OCCURRED,
    MEMORY_READ,
    MEMORY_WRITE,
    RETRY_STARTED,
)
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

    assert emitted == detections
    drift_types = {event.payload["drift_type"] for event in detections}
    assert all(event.event_type == DRIFT_DETECTED for event in detections)
    assert "confidence_decay" in drift_types


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
    assert {"repeated_failures", "changing_plans", "inconsistent_memory_access"}.issubset(drift_types)


def test_drift_detector_detects_improved_heuristics():
    detections = DriftDetector(EventBus()).analyze(
        [
            Event(event_type=CONFIDENCE_UPDATED, agent_id="writer", payload={"confidence": 0.95}),
            Event(event_type=CONFIDENCE_UPDATED, agent_id="writer", payload={"confidence": 0.3}),
            Event(event_type=RETRY_STARTED, agent_id="writer"),
            Event(event_type=RETRY_STARTED, agent_id="writer"),
            Event(event_type=RETRY_STARTED, agent_id="writer"),
            Event(event_type=FAILURE_OCCURRED, agent_id="writer", payload={"reason": "tool timeout"}),
            Event(event_type=FAILURE_OCCURRED, agent_id="writer", payload={"reason": "tool timeout"}),
            Event(event_type=MEMORY_WRITE, payload={"key": "plan"}),
            Event(event_type=MEMORY_READ, payload={"key": "plan", "found": False}),
        ]
    )

    drift_types = {event.payload["drift_type"] for event in detections}
    assert "confidence_collapse" in drift_types
    assert "repeated_retry_loop" in drift_types
    assert "persistent_failure_pattern" in drift_types
    assert "memory_inconsistency" in drift_types

"""Behavioral drift detection heuristics."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Sequence

from events.event import Event
from events.event_types import CONFIDENCE_UPDATED, DRIFT_DETECTED, FAILURE_OCCURRED, MEMORY_READ
from runtime.event_bus import EventBus


class DriftDetector:
    """Detects simple runtime drift signals and emits DRIFT_DETECTED."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def analyze(self, events: Sequence[Event]) -> List[Event]:
        """Analyze an event stream and emit detected drift events."""
        detections: List[Event] = []
        detections.extend(self._detect_confidence_decay(events))
        detections.extend(self._detect_repeated_failures(events))
        detections.extend(self._detect_changing_plans(events))
        detections.extend(self._detect_inconsistent_memory_access(events))
        for event in detections:
            self.event_bus.publish(event)
        return detections

    def _detect_confidence_decay(self, events: Sequence[Event]) -> List[Event]:
        detections = []
        by_agent = self._confidence_by_agent(events)
        for agent_id, values in by_agent.items():
            if len(values) >= 2 and values[-1] < values[0]:
                detections.append(
                    Event(
                        event_type=DRIFT_DETECTED,
                        agent_id=agent_id,
                        payload={"drift_type": "confidence_decay", "start": values[0], "end": values[-1]},
                    )
                )
        return detections

    def _detect_repeated_failures(self, events: Sequence[Event]) -> List[Event]:
        failures = Counter(event.agent_id for event in events if event.event_type == FAILURE_OCCURRED)
        return [
            Event(
                event_type=DRIFT_DETECTED,
                agent_id=agent_id,
                payload={"drift_type": "repeated_failures", "count": count},
            )
            for agent_id, count in failures.items()
            if agent_id is not None and count >= 2
        ]

    def _detect_changing_plans(self, events: Sequence[Event]) -> List[Event]:
        plans = [event.payload.get("plan") for event in events if "plan" in event.payload]
        unique_plans = {plan for plan in plans if plan is not None}
        if len(unique_plans) >= 2:
            return [
                Event(
                    event_type=DRIFT_DETECTED,
                    payload={"drift_type": "changing_plans", "plans": sorted(unique_plans)},
                )
            ]
        return []

    def _detect_inconsistent_memory_access(self, events: Sequence[Event]) -> List[Event]:
        missed_reads = [
            event
            for event in events
            if event.event_type == MEMORY_READ and event.payload.get("found") is False
        ]
        if len(missed_reads) >= 2:
            return [
                Event(
                    event_type=DRIFT_DETECTED,
                    payload={"drift_type": "inconsistent_memory_access", "misses": len(missed_reads)},
                )
            ]
        return []

    @staticmethod
    def _confidence_by_agent(events: Iterable[Event]) -> dict[str, List[float]]:
        values: dict[str, List[float]] = {}
        for event in events:
            if event.event_type == CONFIDENCE_UPDATED and event.agent_id is not None:
                values.setdefault(event.agent_id, []).append(float(event.payload["confidence"]))
        return values

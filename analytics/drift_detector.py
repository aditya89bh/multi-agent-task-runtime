"""Behavioral drift detection heuristics."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import DefaultDict, Iterable, List, Sequence

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


class DriftDetector:
    """Detects runtime drift signals and emits DRIFT_DETECTED."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def analyze(self, events: Sequence[Event]) -> List[Event]:
        """Analyze an event stream and emit detected drift events."""
        detections: List[Event] = []
        detections.extend(self._detect_confidence_decay(events))
        detections.extend(self._detect_confidence_collapse(events))
        detections.extend(self._detect_repeated_failures(events))
        detections.extend(self._detect_persistent_failure_patterns(events))
        detections.extend(self._detect_repeated_retry_loops(events))
        detections.extend(self._detect_changing_plans(events))
        detections.extend(self._detect_inconsistent_memory_access(events))
        detections.extend(self._detect_memory_inconsistency(events))
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

    def _detect_confidence_collapse(self, events: Sequence[Event]) -> List[Event]:
        detections = []
        for agent_id, values in self._confidence_by_agent(events).items():
            if len(values) >= 2 and values[0] - values[-1] >= 0.5:
                detections.append(
                    Event(
                        event_type=DRIFT_DETECTED,
                        agent_id=agent_id,
                        payload={"drift_type": "confidence_collapse", "start": values[0], "end": values[-1]},
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

    def _detect_persistent_failure_patterns(self, events: Sequence[Event]) -> List[Event]:
        failure_reasons = Counter(
            (event.agent_id, event.payload.get("reason") or event.payload.get("exception_type"))
            for event in events
            if event.event_type == FAILURE_OCCURRED
        )
        return [
            Event(
                event_type=DRIFT_DETECTED,
                agent_id=agent_id,
                payload={"drift_type": "persistent_failure_pattern", "reason": reason, "count": count},
            )
            for (agent_id, reason), count in failure_reasons.items()
            if agent_id is not None and reason is not None and count >= 2
        ]

    def _detect_repeated_retry_loops(self, events: Sequence[Event]) -> List[Event]:
        retries = Counter(event.agent_id for event in events if event.event_type == RETRY_STARTED)
        return [
            Event(
                event_type=DRIFT_DETECTED,
                agent_id=agent_id,
                payload={"drift_type": "repeated_retry_loop", "count": count},
            )
            for agent_id, count in retries.items()
            if agent_id is not None and count >= 3
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

    def _detect_memory_inconsistency(self, events: Sequence[Event]) -> List[Event]:
        written_keys = {event.payload.get("key") for event in events if event.event_type == MEMORY_WRITE}
        missed_written_keys = [
            event.payload.get("key")
            for event in events
            if event.event_type == MEMORY_READ
            and event.payload.get("found") is False
            and event.payload.get("key") in written_keys
        ]
        if missed_written_keys:
            return [
                Event(
                    event_type=DRIFT_DETECTED,
                    payload={
                        "drift_type": "memory_inconsistency",
                        "keys": sorted(set(str(key) for key in missed_written_keys)),
                    },
                )
            ]
        return []

    @staticmethod
    def _confidence_by_agent(events: Iterable[Event]) -> dict[str, List[float]]:
        values: DefaultDict[str, List[float]] = defaultdict(list)
        for event in events:
            if event.event_type == CONFIDENCE_UPDATED and event.agent_id is not None:
                values[event.agent_id].append(float(event.payload["confidence"]))
        return dict(values)

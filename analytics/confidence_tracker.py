"""Observable confidence tracking."""

from __future__ import annotations

from collections import defaultdict

from events.event import Event
from events.event_types import CONFIDENCE_UPDATED
from runtime.event_bus import EventBus


class ConfidenceTracker:
    """Tracks confidence history per agent and emits updates."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self._history: defaultdict[str, list[float]] = defaultdict(list)

    def update_confidence(self, agent_id: str, confidence: float, reason: str | None = None) -> None:
        """Record a confidence value and emit CONFIDENCE_UPDATED."""
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        self._history[agent_id].append(confidence)
        self.event_bus.publish(
            Event(
                event_type=CONFIDENCE_UPDATED,
                agent_id=agent_id,
                payload={"confidence": confidence, "reason": reason},
            )
        )

    def history_for(self, agent_id: str) -> list[float]:
        """Return confidence history for one agent."""
        return list(self._history.get(agent_id, []))

    def all_history(self) -> dict[str, list[float]]:
        """Return all confidence histories."""
        return {agent_id: list(values) for agent_id, values in self._history.items()}

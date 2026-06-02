"""Base observable agent lifecycle."""

from __future__ import annotations

from typing import Any

from events.event import Event
from events.event_types import AGENT_FINISHED, AGENT_STARTED
from runtime.event_bus import EventBus


class BaseAgent:
    """Minimal base class that emits lifecycle events."""

    def __init__(self, agent_id: str, event_bus: EventBus) -> None:
        self.agent_id = agent_id
        self.event_bus = event_bus
        self.started = False
        self.finished = False

    def start(self, **context: Any) -> None:
        """Mark the agent as started and emit AGENT_STARTED."""
        self.started = True
        self.event_bus.publish(Event(event_type=AGENT_STARTED, agent_id=self.agent_id, payload={"context": context}))

    def run(self, **context: Any) -> Any:
        """Execute agent behavior.

        Subclasses should override this method. The base implementation returns
        the provided context to keep examples and tests simple.
        """
        return context

    def finish(self, result: Any = None) -> None:
        """Mark the agent as finished and emit AGENT_FINISHED."""
        self.finished = True
        self.event_bus.publish(Event(event_type=AGENT_FINISHED, agent_id=self.agent_id, payload={"result": result}))

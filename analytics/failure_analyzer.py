"""Observable runtime failure tracking."""

from __future__ import annotations

import traceback

from events.event import Event
from events.event_types import FAILURE_OCCURRED
from runtime.event_bus import EventBus


class FailureAnalyzer:
    """Captures exception context and emits failure events."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def capture_exception(
        self,
        exception: BaseException,
        agent_id: str | None = None,
        reason: str | None = None,
    ) -> Event:
        """Capture an exception and emit FAILURE_OCCURRED."""
        event = Event(
            event_type=FAILURE_OCCURRED,
            agent_id=agent_id,
            payload={
                "exception_type": type(exception).__name__,
                "message": str(exception),
                "reason": reason,
                "stack_trace": "".join(traceback.format_exception(type(exception), exception, exception.__traceback__)),
            },
        )
        self.event_bus.publish(event)
        return event

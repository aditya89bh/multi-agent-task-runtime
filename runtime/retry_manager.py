"""Observable retry management."""

from __future__ import annotations

from time import sleep
from typing import Callable, Optional, TypeVar

from events.event import Event
from events.event_types import RETRY_COMPLETED, RETRY_STARTED
from runtime.event_bus import EventBus

T = TypeVar("T")


class RetryManager:
    """Run operations with configurable retries and optional exponential backoff."""

    def __init__(
        self,
        event_bus: EventBus,
        max_retries: int = 3,
        base_delay_seconds: float = 0.0,
        exponential_backoff: bool = True,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        self.event_bus = event_bus
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds
        self.exponential_backoff = exponential_backoff

    def run(self, operation: Callable[[], T], agent_id: Optional[str] = None, operation_name: str = "operation") -> T:
        """Run an operation until it succeeds or retries are exhausted."""
        attempt = 0
        while True:
            try:
                return operation()
            except Exception as error:
                if attempt >= self.max_retries:
                    raise
                attempt += 1
                self.event_bus.publish(
                    Event(
                        event_type=RETRY_STARTED,
                        agent_id=agent_id,
                        payload={
                            "operation_name": operation_name,
                            "attempt": attempt,
                            "error": str(error),
                        },
                    )
                )
                delay = self._delay_for(attempt)
                if delay > 0:
                    sleep(delay)
                self.event_bus.publish(
                    Event(
                        event_type=RETRY_COMPLETED,
                        agent_id=agent_id,
                        payload={"operation_name": operation_name, "attempt": attempt},
                    )
                )

    def _delay_for(self, attempt: int) -> float:
        if not self.exponential_backoff:
            return self.base_delay_seconds
        return self.base_delay_seconds * (2 ** (attempt - 1))

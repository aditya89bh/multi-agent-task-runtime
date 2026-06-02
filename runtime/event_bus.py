"""Synchronous publish/subscribe event bus."""

from __future__ import annotations

from collections.abc import Callable

from events.event import Event

Subscriber = Callable[[Event], None]


class EventBus:
    """A minimal in-process event bus for runtime observability."""

    def __init__(self) -> None:
        self._subscribers: list[Subscriber] = []

    def subscribe(self, subscriber: Subscriber) -> None:
        """Register a subscriber callback."""
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: Subscriber) -> None:
        """Remove a subscriber callback if present."""
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)

    def publish(self, event: Event) -> None:
        """Publish an event to all current subscribers."""
        for subscriber in list(self._subscribers):
            subscriber(event)

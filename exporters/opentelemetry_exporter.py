"""Optional OpenTelemetry-style exporter for runtime events."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from events.event import Event


@dataclass(frozen=True)
class SpanLike:
    """Lightweight trace-like span representation.

    This intentionally avoids requiring opentelemetry-sdk. Applications can
    adapt these dictionaries to a real OpenTelemetry exporter when desired.
    """

    name: str
    timestamp: str
    attributes: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "timestamp": self.timestamp, "attributes": self.attributes}


class OpenTelemetryExporter:
    """Export events as OpenTelemetry-compatible span dictionaries."""

    def export_event(self, event: Event) -> SpanLike:
        attributes: dict[str, Any] = {
            "runtime.event_type": event.event_type,
            "runtime.agent_id": event.agent_id,
        }
        for key, value in event.payload.items():
            attributes[f"runtime.payload.{key}"] = value
        return SpanLike(name=event.event_type, timestamp=event.timestamp, attributes=attributes)

    def export_events(self, events: Iterable[Event]) -> list[dict[str, Any]]:
        return [self.export_event(event).to_dict() for event in events]

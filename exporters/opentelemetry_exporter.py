"""Optional OpenTelemetry-style exporter for runtime events."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from events.event import Event


@dataclass(frozen=True)
class SpanLike:
    """Lightweight trace-like span representation.

    This intentionally avoids requiring opentelemetry-sdk. Applications can
    adapt these dictionaries to a real OpenTelemetry exporter when desired.
    """

    name: str
    timestamp: str
    attributes: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "timestamp": self.timestamp, "attributes": self.attributes}


class OpenTelemetryExporter:
    """Export events as OpenTelemetry-compatible span dictionaries."""

    def export_event(self, event: Event) -> SpanLike:
        attributes: Dict[str, Any] = {
            "runtime.event_type": event.event_type,
            "runtime.agent_id": event.agent_id,
        }
        for key, value in event.payload.items():
            attributes[f"runtime.payload.{key}"] = value
        return SpanLike(name=event.event_type, timestamp=event.timestamp, attributes=attributes)

    def export_events(self, events: Iterable[Event]) -> List[Dict[str, Any]]:
        return [self.export_event(event).to_dict() for event in events]

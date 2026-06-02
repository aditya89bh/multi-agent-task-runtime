"""Core runtime event model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from events.validation import validate_event_fields


@dataclass(frozen=True)
class Event:
    """A single observable fact emitted by the runtime."""

    event_type: str
    agent_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        validate_event_fields(self.event_type, self.agent_id, self.payload, self.timestamp, self.schema_version)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary representation."""
        return asdict(self)

"""Core runtime event model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from events.registry import validate_event_name


@dataclass(frozen=True)
class Event:
    """A single observable fact emitted by the runtime."""

    event_type: str
    agent_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        validate_event_name(self.event_type)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary representation."""
        return asdict(self)

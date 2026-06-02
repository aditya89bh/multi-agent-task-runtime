"""Core runtime event model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from events.registry import validate_event_name


@dataclass(frozen=True)
class Event:
    """A single observable fact emitted by the runtime."""

    event_type: str
    agent_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        validate_event_name(self.event_type)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary representation."""
        return asdict(self)

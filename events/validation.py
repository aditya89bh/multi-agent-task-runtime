"""Strict validation helpers for runtime events."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from events.registry import validate_event_name

_SCHEMA_VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_AGENT_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")


def validate_event_fields(
    event_type: str,
    agent_id: str | None,
    payload: dict[str, Any],
    timestamp: str,
    schema_version: str,
) -> None:
    """Validate event fields and raise clear ValueError/TypeError failures."""
    validate_event_name(event_type)
    if agent_id is not None:
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("agent_id must be a non-empty string when provided")
        if not _AGENT_ID_RE.fullmatch(agent_id):
            raise ValueError("agent_id may contain only letters, numbers, underscore, dash, dot, and colon")
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")
    try:
        json.dumps(payload, sort_keys=True)
    except (TypeError, ValueError) as error:
        raise TypeError("payload must be JSON serializable") from error
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("timestamp must be a non-empty ISO-8601 string")
    normalized = timestamp.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ValueError("timestamp must be ISO-8601 parseable") from error
    if not isinstance(schema_version, str) or not _SCHEMA_VERSION_RE.fullmatch(schema_version):
        raise ValueError("schema_version must use MAJOR.MINOR format")

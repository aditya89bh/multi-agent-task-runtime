"""Built-in and custom event type registration."""

from __future__ import annotations

import re
from typing import Set

from events import event_types

_EVENT_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_BUILT_INS = {
    value
    for name, value in vars(event_types).items()
    if name.isupper() and isinstance(value, str)
}
_CUSTOM: Set[str] = set()


def validate_event_name(name: str) -> str:
    if not _EVENT_NAME_RE.match(name):
        raise ValueError("event names must be lowercase snake_case and start with a letter")
    return name


def register_event_type(name: str) -> str:
    name = validate_event_name(name)
    _CUSTOM.add(name)
    return name


def unregister_event_type(name: str) -> None:
    _CUSTOM.discard(name)


def is_registered_event_type(name: str) -> bool:
    return name in _BUILT_INS or name in _CUSTOM


def registered_event_types() -> Set[str]:
    return set(_BUILT_INS) | set(_CUSTOM)

"""Observable tool registration and execution."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any

from events.event import Event
from events.event_types import TOOL_CALLED, TOOL_RETURNED
from runtime.event_bus import EventBus

Tool = Callable[..., Any]


class ToolExecutor:
    """Executes registered tools and emits tool events."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self._tools: dict[str, Tool] = {}

    def register_tool(self, name: str, tool: Tool) -> None:
        """Register a callable tool by name."""
        self._tools[name] = tool

    def execute(self, name: str, *args: Any, agent_id: str | None = None, **kwargs: Any) -> Any:
        """Execute a registered tool and emit call/return events."""
        if name not in self._tools:
            raise KeyError(f"Tool is not registered: {name}")

        self.event_bus.publish(
            Event(
                event_type=TOOL_CALLED,
                agent_id=agent_id,
                payload={"tool_name": name, "args": list(args), "kwargs": kwargs},
            )
        )
        start = perf_counter()
        result = self._tools[name](*args, **kwargs)
        duration_ms = (perf_counter() - start) * 1000
        self.event_bus.publish(
            Event(
                event_type=TOOL_RETURNED,
                agent_id=agent_id,
                payload={"tool_name": name, "result": result, "duration_ms": duration_ms},
            )
        )
        return result

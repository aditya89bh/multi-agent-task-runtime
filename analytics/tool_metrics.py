"""Tool usage analytics."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, DefaultDict, Dict, Iterable, List

from events import event_types
from events.event import Event


class ToolMetricsCollector:
    """Summarize tool usage, durations, and failures."""

    def summarize(self, events: Iterable[Event]) -> Dict[str, Any]:
        usage: Counter[str] = Counter()
        durations: DefaultDict[str, List[float]] = defaultdict(list)
        failures: Counter[str] = Counter()
        last_called_tool_by_agent: Dict[str, str] = {}
        for event in events:
            if event.event_type == event_types.TOOL_CALLED:
                tool_name = str(event.payload.get("tool_name"))
                usage[tool_name] += 1
                if event.agent_id is not None:
                    last_called_tool_by_agent[event.agent_id] = tool_name
            elif event.event_type == event_types.TOOL_RETURNED:
                tool_name = str(event.payload.get("tool_name"))
                durations[tool_name].append(float(event.payload.get("duration_ms", 0)))
            elif event.event_type == event_types.FAILURE_OCCURRED and event.agent_id in last_called_tool_by_agent:
                failures[last_called_tool_by_agent[event.agent_id]] += 1
        return {
            "tool_usage_count": dict(usage),
            "average_execution_time": {
                tool: sum(values) / len(values) for tool, values in durations.items()
            },
            "failures_by_tool": dict(failures),
        }

"""Failure heatmap analytics."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable

from events.event import Event
from events.event_types import FAILURE_OCCURRED


class FailureHeatmap:
    """Summarize failure density by agent, tool, event type, and reason."""

    def summarize(self, events: Iterable[Event]) -> Dict[str, Any]:
        by_agent: Counter[str] = Counter()
        by_tool: Counter[str] = Counter()
        by_event_type: Counter[str] = Counter()
        reasons: Counter[str] = Counter()
        for event in events:
            if event.event_type != FAILURE_OCCURRED:
                continue
            by_agent[str(event.agent_id or "system")] += 1
            if event.payload.get("tool_name"):
                by_tool[str(event.payload["tool_name"])] += 1
            by_event_type[event.event_type] += 1
            reason = event.payload.get("reason") or event.payload.get("message") or event.payload.get("exception_type")
            if reason:
                reasons[str(reason)] += 1
        return {
            "failures_by_agent": dict(by_agent),
            "failures_by_tool": dict(by_tool),
            "failures_by_event_type": dict(by_event_type),
            "most_repeated_failure_reasons": reasons.most_common(),
        }

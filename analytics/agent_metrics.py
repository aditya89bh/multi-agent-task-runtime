"""Agent-level performance analytics."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, DefaultDict, Dict, Iterable, List

from events import event_types
from events.event import Event


class AgentMetricsCollector:
    """Compute per-agent task, failure, retry, and confidence metrics."""

    def summarize(self, events: Iterable[Event]) -> Dict[str, Dict[str, Any]]:
        metrics: DefaultDict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "tasks_completed": 0,
                "failures": 0,
                "retries": 0,
                "average_confidence": 0.0,
                "success_rate": 0.0,
            }
        )
        confidence: DefaultDict[str, List[float]] = defaultdict(list)
        starts: DefaultDict[str, int] = defaultdict(int)
        for event in events:
            if event.agent_id is None:
                continue
            agent = event.agent_id
            _ = metrics[agent]
            if event.event_type == event_types.AGENT_STARTED:
                starts[agent] += 1
            elif event.event_type == event_types.AGENT_FINISHED:
                metrics[agent]["tasks_completed"] += 1
            elif event.event_type == event_types.FAILURE_OCCURRED:
                metrics[agent]["failures"] += 1
            elif event.event_type == event_types.RETRY_STARTED:
                metrics[agent]["retries"] += 1
            elif event.event_type == event_types.CONFIDENCE_UPDATED:
                confidence[agent].append(float(event.payload["confidence"]))

        for agent, values in metrics.items():
            if confidence[agent]:
                values["average_confidence"] = sum(confidence[agent]) / len(confidence[agent])
            attempts = starts[agent] or values["tasks_completed"] + values["failures"]
            values["success_rate"] = values["tasks_completed"] / attempts if attempts else 0.0
        return dict(metrics)

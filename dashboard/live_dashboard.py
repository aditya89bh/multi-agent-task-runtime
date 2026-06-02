#!/usr/bin/env python3
"""Live terminal dashboard for runtime event streams."""

from __future__ import annotations

import sys
from collections.abc import Iterable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analytics.agent_metrics import AgentMetricsCollector
from analytics.memory_metrics import MemoryMetricsCollector
from analytics.runtime_metrics import RuntimeMetricsCollector
from events.event import Event
from events.event_types import CONFIDENCE_UPDATED, TOOL_CALLED
from runtime.replay_engine import ReplayEngine


class LiveDashboard:
    """Render a compact terminal dashboard from runtime events."""

    def render(self, events: Iterable[Event]) -> str:
        event_list = list(events)
        runtime = RuntimeMetricsCollector().summarize(event_list)
        agents = AgentMetricsCollector().summarize(event_list)
        memory = MemoryMetricsCollector().summarize(event_list)
        confidence = self._latest_confidence(event_list)
        tools = [event.payload.get("tool_name") for event in event_list if event.event_type == TOOL_CALLED]

        lines = [
            "Multi-Agent Task Runtime Dashboard",
            "==================================",
            f"Active agents: {', '.join(sorted(agents)) or 'none'}",
            f"Total events: {runtime['total_events']}",
            f"Memory activity: reads={runtime['memory_reads']} writes={runtime['memory_writes']}",
            f"Tool activity: calls={runtime['tool_calls']} tools={', '.join(str(tool) for tool in tools) or 'none'}",
            f"Failures: {runtime['failures']}",
            f"Retries: {runtime['retries']}",
            "Confidence:",
        ]
        if confidence:
            lines.extend(f"  - {agent}: {value:.2f}" for agent, value in sorted(confidence.items()))
        else:
            lines.append("  - none")
        if memory["most_accessed_keys"]:
            lines.append(f"Most accessed memory keys: {memory['most_accessed_keys']}")
        return "\n".join(lines)

    def print(self, events: Iterable[Event]) -> None:
        """Print dashboard using Rich when available, otherwise plain text."""
        output = self.render(events)
        try:
            from rich.console import Console
            from rich.panel import Panel

            Console().print(Panel(output, title="Runtime Observability"))
        except Exception:
            print(output)

    @staticmethod
    def _latest_confidence(events: Iterable[Event]) -> dict[str, float]:
        latest: dict[str, float] = {}
        for event in events:
            if event.event_type == CONFIDENCE_UPDATED and event.agent_id is not None:
                latest[event.agent_id] = float(event.payload["confidence"])
        return latest


def main() -> None:
    log_path = Path("logs/runtime_events.jsonl")
    if not log_path.exists():
        print("No logs/runtime_events.jsonl found. Run examples/multi_agent_demo.py first.")
        return
    LiveDashboard().print(ReplayEngine().load_jsonl(log_path))


if __name__ == "__main__":
    main()

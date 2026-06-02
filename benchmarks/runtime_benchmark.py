#!/usr/bin/env python3
"""Runtime benchmark suite for large event volumes."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.base_agent import BaseAgent
from analytics.runtime_metrics import RuntimeMetricsCollector
from events.event import Event
from events.event_types import AGENT_FINISHED, AGENT_STARTED, MEMORY_READ, MEMORY_WRITE, TOOL_CALLED, TOOL_RETURNED
from runtime.event_bus import EventBus

RESULTS_PATH = Path("benchmarks/results/latest_results.json")


class BenchmarkAgent(BaseAgent):
    def run(self, **context):
        return {"events": context.get("events_per_agent", 0)}


def run_benchmark(agent_count: int = 10, events_per_agent: int = 100) -> dict[str, object]:
    bus = EventBus()
    events: list[Event] = []
    bus.subscribe(events.append)
    start = perf_counter()
    for index in range(agent_count):
        agent_id = f"agent_{index}"
        bus.publish(Event(event_type=AGENT_STARTED, agent_id=agent_id))
        for event_index in range(events_per_agent):
            bus.publish(Event(event_type=MEMORY_READ, agent_id=agent_id, payload={"key": f"key_{event_index % 10}"}))
            bus.publish(Event(event_type=MEMORY_WRITE, agent_id=agent_id, payload={"key": f"key_{event_index % 10}"}))
            bus.publish(Event(event_type=TOOL_CALLED, agent_id=agent_id, payload={"tool_name": "benchmark_tool"}))
            bus.publish(Event(event_type=TOOL_RETURNED, agent_id=agent_id, payload={"tool_name": "benchmark_tool", "duration_ms": 0.01}))
        bus.publish(Event(event_type=AGENT_FINISHED, agent_id=agent_id))
    duration = perf_counter() - start
    summary = RuntimeMetricsCollector().summarize(events)
    result: dict[str, object] = {
        "agent_count": agent_count,
        "events_per_agent": events_per_agent,
        "total_events": len(events),
        "duration_seconds": duration,
        "events_per_second": len(events) / duration if duration else 0,
        "summary": summary,
    }
    return result


def write_results(result: dict[str, object], output_path: Path = RESULTS_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    result = run_benchmark()
    write_results(result)
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"Benchmark results written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()

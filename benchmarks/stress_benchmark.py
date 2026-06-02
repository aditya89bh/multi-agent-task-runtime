#!/usr/bin/env python3
"""Large-scale runtime stress benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analytics.runtime_metrics import RuntimeMetricsCollector
from events.event import Event
from events.event_types import CONFIDENCE_UPDATED, FAILURE_OCCURRED, MEMORY_READ, MEMORY_WRITE, TOOL_CALLED, TOOL_RETURNED
from runtime.archive import write_jsonl_gz, read_jsonl_gz
from runtime.sqlite_store import SQLiteEventStore

RESULTS_PATH = Path("benchmarks/results/stress_results.json")


def generate_events(event_count: int, agent_count: int) -> list[Event]:
    types = [MEMORY_READ, MEMORY_WRITE, TOOL_CALLED, TOOL_RETURNED, CONFIDENCE_UPDATED, FAILURE_OCCURRED]
    events = []
    for index in range(event_count):
        event_type = types[index % len(types)]
        payload = {"key": f"key_{index % 100}", "tool_name": "stress_tool", "confidence": (index % 100) / 100, "reason": "stress"}
        events.append(Event(event_type=event_type, agent_id=f"agent_{index % agent_count}", payload=payload))
    return events


def run_stress(event_count: int = 100_000, agent_count: int = 25) -> dict:
    events = generate_events(event_count, agent_count)
    db_path = Path("benchmarks/results/stress_events.db")
    if db_path.exists():
        db_path.unlink()
    start = perf_counter()
    store = SQLiteEventStore(db_path)
    store.store_events(events)
    write_seconds = perf_counter() - start

    start = perf_counter()
    loaded = store.get_events()
    read_seconds = perf_counter() - start

    archive = Path("benchmarks/results/stress_events.jsonl.gz")
    write_jsonl_gz(loaded, archive)
    start = perf_counter()
    replayed = read_jsonl_gz(archive)
    replay_seconds = perf_counter() - start

    start = perf_counter()
    summary = RuntimeMetricsCollector().summarize(replayed)
    metrics_seconds = perf_counter() - start

    return {
        "event_count": event_count,
        "agent_count": agent_count,
        "write_throughput_events_per_second": event_count / write_seconds if write_seconds else 0,
        "read_throughput_events_per_second": event_count / read_seconds if read_seconds else 0,
        "replay_time_seconds": replay_seconds,
        "metrics_generation_time_seconds": metrics_seconds,
        "summary": summary,
    }


def write_results(result: dict, path: Path = RESULTS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run runtime stress benchmark")
    parser.add_argument("--small", action="store_true", help="Use a small CI-friendly event count")
    args = parser.parse_args()
    result = run_stress(event_count=1_000 if args.small else 100_000, agent_count=5 if args.small else 25)
    write_results(result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

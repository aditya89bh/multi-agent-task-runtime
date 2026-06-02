#!/usr/bin/env python3
"""Configurable load test for runtime storage and replay."""

from __future__ import annotations

import argparse
import json
import resource
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from events.event import Event
from events.event_types import CONFIDENCE_UPDATED, FAILURE_OCCURRED, MEMORY_READ, MEMORY_WRITE, TOOL_CALLED, TOOL_RETURNED
from runtime.archive import read_jsonl_gz, write_jsonl_gz
from runtime.sqlite_store import SQLiteEventStore

RESULTS_PATH = Path("benchmarks/results/load_test_results.json")


def generate_events(event_count: int, agent_count: int = 10) -> list[Event]:
    event_types = [MEMORY_READ, MEMORY_WRITE, TOOL_CALLED, TOOL_RETURNED, CONFIDENCE_UPDATED, FAILURE_OCCURRED]
    events: list[Event] = []
    for index in range(event_count):
        events.append(
            Event(
                event_type=event_types[index % len(event_types)],
                agent_id=f"agent-{index % agent_count}",
                payload={
                    "index": index,
                    "key": f"key-{index % 100}",
                    "tool_name": "load_tool",
                    "confidence": (index % 100) / 100,
                    "reason": "load",
                },
            )
        )
    return events


def memory_usage_mb() -> float | None:
    try:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except (AttributeError, ValueError):
        return None


def run_load_test(event_count: int = 10_000, agent_count: int = 10) -> dict[str, object]:
    events = generate_events(event_count, agent_count)
    results_dir = Path("benchmarks/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    db_path = results_dir / "load_test_events.db"
    if db_path.exists():
        db_path.unlink()

    store = SQLiteEventStore(db_path)
    start = perf_counter()
    store.store_events(events)
    write_seconds = perf_counter() - start

    start = perf_counter()
    stored = store.retrieve_events()
    read_seconds = perf_counter() - start

    archive = results_dir / "load_test_events.jsonl.gz"
    write_jsonl_gz(stored, archive)
    start = perf_counter()
    replayed = read_jsonl_gz(archive)
    replay_seconds = perf_counter() - start

    return {
        "event_count": event_count,
        "agent_count": agent_count,
        "write_throughput_events_per_second": event_count / write_seconds if write_seconds else 0,
        "read_throughput_events_per_second": event_count / read_seconds if read_seconds else 0,
        "replay_time_seconds": replay_seconds,
        "memory_usage_mb": memory_usage_mb(),
        "replayed_events": len(replayed),
    }


def write_results(result: dict[str, object], path: Path = RESULTS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a configurable runtime load test")
    parser.add_argument("--events", type=int, default=10_000)
    parser.add_argument("--agents", type=int, default=10)
    parser.add_argument("--small", action="store_true", help="Run a small CI-safe load test")
    parser.add_argument("--million", action="store_true", help="Run a 1,000,000 event load test")
    args = parser.parse_args()
    event_count = 1_000 if args.small else 1_000_000 if args.million else args.events
    result = run_load_test(event_count=event_count, agent_count=5 if args.small else args.agents)
    write_results(result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

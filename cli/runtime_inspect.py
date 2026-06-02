"""Inspect runtime event logs."""

from __future__ import annotations

import argparse
import json
from typing import List

from analytics.agent_metrics import AgentMetricsCollector
from analytics.confidence_analysis import ConfidenceAnalyzer
from analytics.memory_metrics import MemoryMetricsCollector
from analytics.runtime_metrics import RuntimeMetricsCollector
from analytics.tool_metrics import ToolMetricsCollector
from events.event import Event
from events.event_types import FAILURE_OCCURRED
from runtime.replay_engine import ReplayEngine
from runtime.sqlite_store import SQLiteEventStore


def inspect_events(events: List[Event]) -> dict:
    tool_summary = ToolMetricsCollector().summarize(events)
    memory_summary = MemoryMetricsCollector().summarize(events)
    return {
        "runtime": RuntimeMetricsCollector().summarize(events),
        "agents": AgentMetricsCollector().summarize(events),
        "failures": [event.to_dict() for event in events if event.event_type == FAILURE_OCCURRED],
        "confidence": ConfidenceAnalyzer().analyze(events),
        "top_tools": sorted(tool_summary["tool_usage_count"].items(), key=lambda item: item[1], reverse=True),
        "top_memory_keys": memory_summary["most_accessed_keys"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="runtime-inspect", description="Inspect runtime JSONL or SQLite event logs")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--jsonl")
    source.add_argument("--sqlite")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    events = SQLiteEventStore(args.sqlite).get_events() if args.sqlite else ReplayEngine().load_jsonl(args.jsonl)
    print(json.dumps(inspect_events(events), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

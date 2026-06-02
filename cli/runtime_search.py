"""Search runtime event logs."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable

from events.event import Event
from runtime.paths import ensure_input_file
from runtime.replay_engine import ReplayEngine
from runtime.sqlite_store import SQLiteEventStore


def search_events(
    events: Iterable[Event], event_type: str | None = None, agent_id: str | None = None, keyword: str | None = None
) -> list[Event]:
    results = []
    for event in events:
        if event_type and event.event_type != event_type:
            continue
        if agent_id and event.agent_id != agent_id:
            continue
        if keyword and keyword.lower() not in json.dumps(event.payload, sort_keys=True).lower():
            continue
        results.append(event)
    return results


def load_events(args: argparse.Namespace) -> list[Event]:
    if args.sqlite:
        return SQLiteEventStore(ensure_input_file(args.sqlite, "SQLite database")).get_events()
    return ReplayEngine().load_jsonl(ensure_input_file(args.jsonl, "JSONL log"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="runtime-search", description="Search runtime JSONL or SQLite event logs")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--jsonl", help="Path to JSONL event log")
    source.add_argument("--sqlite", help="Path to SQLite event store")
    parser.add_argument("--event-type")
    parser.add_argument("--agent-id")
    parser.add_argument("--keyword")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for event in search_events(load_events(args), args.event_type, args.agent_id, args.keyword):
        print(json.dumps(event.to_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

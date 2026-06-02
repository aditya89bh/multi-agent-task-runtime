import json
import subprocess
import sys

from cli.runtime_search import search_events
from events.event import Event
from events.event_types import FAILURE_OCCURRED


def test_search_events_filters_by_type_agent_and_keyword():
    events = [
        Event(event_type=FAILURE_OCCURRED, agent_id="writer", payload={"reason": "timeout"}),
        Event(event_type="custom_event", agent_id="planner", payload={"note": "ok"}),
    ]

    assert search_events(events, event_type=FAILURE_OCCURRED, agent_id="writer", keyword="timeout") == [events[0]]


def test_runtime_search_cli_reads_jsonl(tmp_path):
    path = tmp_path / "events.jsonl"
    event = Event(event_type=FAILURE_OCCURRED, agent_id="writer", payload={"reason": "timeout"})
    path.write_text(json.dumps(event.to_dict()) + "\n", encoding="utf-8")

    result = subprocess.run([sys.executable, "-m", "cli.runtime_search", "--jsonl", str(path), "--keyword", "timeout"], capture_output=True, text=True, check=True)

    assert "failure_occurred" in result.stdout

import json
import subprocess
import sys

from cli.runtime_inspect import inspect_events
from events.event import Event
from events.event_types import CONFIDENCE_UPDATED, FAILURE_OCCURRED, MEMORY_READ, TOOL_CALLED


def test_inspect_events_returns_summary_sections():
    events = [
        Event(event_type=TOOL_CALLED, agent_id="planner", payload={"tool_name": "search"}),
        Event(event_type=MEMORY_READ, agent_id="planner", payload={"key": "plan"}),
        Event(event_type=FAILURE_OCCURRED, agent_id="planner", payload={"reason": "timeout"}),
        Event(event_type=CONFIDENCE_UPDATED, agent_id="planner", payload={"confidence": 0.8}),
    ]

    report = inspect_events(events)

    assert report["runtime"]["total_events"] == 4
    assert report["failures"][0]["event_type"] == FAILURE_OCCURRED
    assert report["top_tools"] == [("search", 1)]
    assert report["top_memory_keys"] == [("plan", 1)]


def test_runtime_inspect_cli_reads_jsonl(tmp_path):
    path = tmp_path / "events.jsonl"
    event = Event(event_type=TOOL_CALLED, payload={"tool_name": "search"})
    path.write_text(json.dumps(event.to_dict()) + "\n", encoding="utf-8")

    result = subprocess.run([sys.executable, "-m", "cli.runtime_inspect", "--jsonl", str(path)], capture_output=True, text=True, check=True)

    assert '"tool_calls": 1' in result.stdout

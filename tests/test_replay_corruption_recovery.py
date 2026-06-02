import json

from events.event import Event
from events.event_types import AGENT_STARTED
from runtime.replay_engine import ReplayEngine


def test_replay_engine_skips_blank_malformed_and_partial_lines(tmp_path):
    valid = Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:00+00:00")
    path = tmp_path / "events.jsonl"
    path.write_text(
        "\n" + json.dumps(valid.to_dict()) + "\n" + "{bad json\n" + json.dumps({"event_type": "Bad Event"}) + "\n" + "[1, 2, 3]\n",
        encoding="utf-8",
    )

    engine = ReplayEngine()
    summary = engine.load_jsonl_with_summary(path)

    assert summary.events == [valid]
    assert summary.skipped_events == 3
    assert summary.skipped_lines == (3, 4, 5)
    assert engine.load_jsonl(path) == [valid]
    assert engine.last_summary.skipped_events == 3

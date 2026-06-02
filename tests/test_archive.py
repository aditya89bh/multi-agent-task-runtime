import json

from events.event import Event
from events.event_types import AGENT_STARTED
from runtime.archive import compress_jsonl, read_jsonl_gz, write_jsonl_gz
from runtime.replay_engine import ReplayEngine


def test_compress_and_read_jsonl_gz_preserves_replay_compatibility(tmp_path):
    event = Event(event_type=AGENT_STARTED, agent_id="planner", timestamp="2026-01-01T10:00:00+00:00")
    source = tmp_path / "events.jsonl"
    source.write_text(json.dumps(event.to_dict()) + "\n", encoding="utf-8")

    archive = compress_jsonl(source)

    assert archive.suffix == ".gz"
    assert read_jsonl_gz(archive) == [event]
    assert list(ReplayEngine().replay(read_jsonl_gz(archive))) == [event]


def test_write_jsonl_gz_writes_events_directly(tmp_path):
    event = Event(event_type=AGENT_STARTED)
    archive = write_jsonl_gz([event], tmp_path / "events.jsonl.gz")
    assert read_jsonl_gz(archive) == [event]

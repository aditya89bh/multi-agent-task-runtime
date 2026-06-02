from events.event import Event
from events.event_types import AGENT_STARTED, CONFIDENCE_UPDATED, MEMORY_READ, TOOL_CALLED
from visualization.replay_timeline import ReplayTimelineRenderer


def test_replay_timeline_renderer_generates_readable_lines():
    events = [
        Event(event_type=TOOL_CALLED, timestamp="2026-01-01T10:00:03+00:00", agent_id="researcher"),
        Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:01+00:00", agent_id="planner"),
        Event(event_type=MEMORY_READ, timestamp="2026-01-01T10:00:02+00:00", agent_id="planner"),
        Event(event_type=CONFIDENCE_UPDATED, timestamp="2026-01-01T10:00:04+00:00", agent_id="planner"),
    ]

    timeline = ReplayTimelineRenderer().render(events)

    assert timeline.splitlines() == [
        "[10:00:01] Planner started",
        "[10:00:02] Memory read",
        "[10:00:03] Tool call",
        "[10:00:04] Confidence updated",
    ]

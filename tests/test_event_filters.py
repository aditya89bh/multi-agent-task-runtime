from events.event import Event
from events.event_types import AGENT_STARTED, MEMORY_READ, TOOL_CALLED
from events.filters import filter_events
from visualization.replay_timeline import ReplayTimelineRenderer


def test_filter_events_by_type_agent_and_time_window():
    events = [
        Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:00+00:00", agent_id="planner"),
        Event(event_type=MEMORY_READ, timestamp="2026-01-01T10:00:01+00:00", agent_id="planner"),
        Event(event_type=TOOL_CALLED, timestamp="2026-01-01T10:00:02+00:00", agent_id="researcher"),
    ]

    assert filter_events(events, event_type=MEMORY_READ) == [events[1]]
    assert filter_events(events, agent_id="planner") == [events[0], events[1]]
    assert filter_events(events, start_time="2026-01-01T10:00:01+00:00") == [events[1], events[2]]
    assert filter_events(events, end_time="2026-01-01T10:00:01+00:00") == [events[0], events[1]]


def test_replay_timeline_renderer_supports_filters():
    events = [
        Event(event_type=AGENT_STARTED, timestamp="2026-01-01T10:00:00+00:00", agent_id="planner"),
        Event(event_type=TOOL_CALLED, timestamp="2026-01-01T10:00:01+00:00", agent_id="researcher"),
    ]

    timeline = ReplayTimelineRenderer().render(events, agent_id="researcher")

    assert timeline == "[10:00:01] Tool call"

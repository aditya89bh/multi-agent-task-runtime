from events.event import Event
from events.event_types import AGENT_STARTED, MEMORY_WRITE
from visualization.timeline_renderer import TimelineRenderer


def test_timeline_renderer_outputs_chronological_lines():
    renderer = TimelineRenderer()
    events = [
        Event(event_type=MEMORY_WRITE, agent_id="planner", payload={"key": "plan"}, timestamp="2026-01-01T00:00:02+00:00"),
        Event(event_type=AGENT_STARTED, agent_id="planner", payload={}, timestamp="2026-01-01T00:00:01+00:00"),
    ]

    timeline = renderer.render(events)

    lines = timeline.splitlines()
    assert "agent_started" in lines[0]
    assert "memory_write" in lines[1]
    assert "key='plan'" in lines[1]

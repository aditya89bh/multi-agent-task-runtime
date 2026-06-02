from dashboard.live_dashboard import LiveDashboard
from events import event_types
from events.event import Event


def test_live_dashboard_renders_runtime_activity():
    events = [
        Event(event_type=event_types.AGENT_STARTED, agent_id="planner"),
        Event(event_type=event_types.CONFIDENCE_UPDATED, agent_id="planner", payload={"confidence": 0.8}),
        Event(event_type=event_types.MEMORY_READ, agent_id="planner", payload={"key": "plan"}),
        Event(event_type=event_types.TOOL_CALLED, agent_id="planner", payload={"tool_name": "search"}),
        Event(event_type=event_types.FAILURE_OCCURRED, agent_id="planner"),
        Event(event_type=event_types.RETRY_STARTED, agent_id="planner"),
    ]

    output = LiveDashboard().render(events)

    assert "Active agents: planner" in output
    assert "Memory activity: reads=1 writes=0" in output
    assert "Tool activity: calls=1 tools=search" in output
    assert "Failures: 1" in output
    assert "Retries: 1" in output
    assert "planner: 0.80" in output

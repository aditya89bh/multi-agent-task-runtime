from analytics.tool_metrics import ToolMetricsCollector
from events import event_types
from events.event import Event


def test_tool_metrics_collector_tracks_usage_duration_and_failures():
    events = [
        Event(event_type=event_types.TOOL_CALLED, agent_id="researcher", payload={"tool_name": "search"}),
        Event(event_type=event_types.TOOL_RETURNED, agent_id="researcher", payload={"tool_name": "search", "duration_ms": 10}),
        Event(event_type=event_types.TOOL_CALLED, agent_id="researcher", payload={"tool_name": "search"}),
        Event(event_type=event_types.FAILURE_OCCURRED, agent_id="researcher"),
    ]

    summary = ToolMetricsCollector().summarize(events)

    assert summary["tool_usage_count"] == {"search": 2}
    assert summary["average_execution_time"] == {"search": 10.0}
    assert summary["failures_by_tool"] == {"search": 1}

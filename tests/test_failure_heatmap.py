from analytics.failure_heatmap import FailureHeatmap
from events.event import Event
from events.event_types import FAILURE_OCCURRED


def test_failure_heatmap_summarizes_failures():
    events = [
        Event(event_type=FAILURE_OCCURRED, agent_id="writer", payload={"tool_name": "summarize", "reason": "timeout"}),
        Event(event_type=FAILURE_OCCURRED, agent_id="writer", payload={"tool_name": "summarize", "reason": "timeout"}),
        Event(event_type=FAILURE_OCCURRED, agent_id="planner", payload={"reason": "bad plan"}),
    ]

    summary = FailureHeatmap().summarize(events)

    assert summary["failures_by_agent"] == {"writer": 2, "planner": 1}
    assert summary["failures_by_tool"] == {"summarize": 2}
    assert summary["failures_by_event_type"] == {FAILURE_OCCURRED: 3}
    assert summary["most_repeated_failure_reasons"][0] == ("timeout", 2)

from analytics.agent_metrics import AgentMetricsCollector
from events import event_types
from events.event import Event


def test_agent_metrics_collector_summarizes_agent_performance():
    events = [
        Event(event_type=event_types.AGENT_STARTED, agent_id="planner"),
        Event(event_type=event_types.CONFIDENCE_UPDATED, agent_id="planner", payload={"confidence": 0.8}),
        Event(event_type=event_types.CONFIDENCE_UPDATED, agent_id="planner", payload={"confidence": 0.6}),
        Event(event_type=event_types.RETRY_STARTED, agent_id="planner"),
        Event(event_type=event_types.AGENT_FINISHED, agent_id="planner"),
        Event(event_type=event_types.AGENT_STARTED, agent_id="writer"),
        Event(event_type=event_types.FAILURE_OCCURRED, agent_id="writer"),
    ]

    summary = AgentMetricsCollector().summarize(events)

    assert summary["planner"] == {
        "tasks_completed": 1,
        "failures": 0,
        "retries": 1,
        "average_confidence": 0.7,
        "success_rate": 1.0,
    }
    assert summary["writer"]["failures"] == 1
    assert summary["writer"]["success_rate"] == 0.0

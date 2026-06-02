from analytics.runtime_metrics import RuntimeMetricsCollector
from events.event import Event
from events import event_types


def test_runtime_metrics_collector_summarizes_counts():
    events = [
        Event(event_type=event_types.TOOL_CALLED),
        Event(event_type=event_types.MEMORY_READ),
        Event(event_type=event_types.MEMORY_WRITE),
        Event(event_type=event_types.FAILURE_OCCURRED),
        Event(event_type=event_types.RETRY_STARTED),
    ]

    assert RuntimeMetricsCollector().summarize(events) == {
        "total_events": 5,
        "tool_calls": 1,
        "memory_reads": 1,
        "memory_writes": 1,
        "failures": 1,
        "retries": 1,
    }

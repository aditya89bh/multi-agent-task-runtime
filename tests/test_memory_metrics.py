from analytics.memory_metrics import MemoryMetricsCollector
from events import event_types
from events.event import Event


def test_memory_metrics_collector_tracks_access_counts_and_frequency():
    events = [
        Event(event_type=event_types.MEMORY_READ, payload={"key": "plan"}),
        Event(event_type=event_types.MEMORY_READ, payload={"key": "plan"}),
        Event(event_type=event_types.MEMORY_WRITE, payload={"key": "draft"}),
    ]

    summary = MemoryMetricsCollector().summarize(events)

    assert summary["read_count"] == 2
    assert summary["write_count"] == 1
    assert summary["most_accessed_keys"] == [("plan", 2), ("draft", 1)]
    assert summary["access_frequency"] == {"plan": 2, "draft": 1}

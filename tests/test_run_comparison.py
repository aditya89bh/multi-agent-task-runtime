from analytics.run_comparison import RunComparison
from events.event import Event
from events.event_types import CONFIDENCE_UPDATED, FAILURE_OCCURRED, MEMORY_READ, TOOL_CALLED


def test_run_comparison_reports_deltas_between_runs():
    baseline = [Event(event_type=TOOL_CALLED), Event(event_type=CONFIDENCE_UPDATED, payload={"confidence": 0.8})]
    candidate = [
        Event(event_type=TOOL_CALLED),
        Event(event_type=TOOL_CALLED),
        Event(event_type=MEMORY_READ),
        Event(event_type=FAILURE_OCCURRED),
        Event(event_type=CONFIDENCE_UPDATED, payload={"confidence": 0.6}),
    ]

    report = RunComparison().compare(baseline, candidate)

    assert report["total_events"]["delta"] == 3.0
    assert report["failures"]["candidate"] == 1.0
    assert report["tool_calls"]["delta"] == 1.0
    assert round(report["average_confidence"]["delta"], 2) == -0.2

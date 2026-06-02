from analytics.failure_analyzer import FailureAnalyzer
from events.event_types import FAILURE_OCCURRED
from runtime.event_bus import EventBus


def test_failure_analyzer_captures_exception_details():
    bus = EventBus()
    events = []
    bus.subscribe(events.append)
    analyzer = FailureAnalyzer(bus)

    try:
        raise RuntimeError("tool failed")
    except RuntimeError as error:
        event = analyzer.capture_exception(error, agent_id="writer", reason="tool execution")

    assert events == [event]
    assert event.event_type == FAILURE_OCCURRED
    assert event.agent_id == "writer"
    assert event.payload["exception_type"] == "RuntimeError"
    assert event.payload["message"] == "tool failed"
    assert event.payload["reason"] == "tool execution"
    assert "RuntimeError: tool failed" in event.payload["stack_trace"]

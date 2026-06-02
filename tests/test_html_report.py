from events.event import Event
from events.event_types import CONFIDENCE_UPDATED, FAILURE_OCCURRED, TOOL_CALLED
from reports.html_report import HTMLReportGenerator


def test_html_report_generator_writes_expected_sections(tmp_path):
    events = [
        Event(event_type=TOOL_CALLED, agent_id="researcher", payload={"tool_name": "search"}),
        Event(event_type=FAILURE_OCCURRED, agent_id="writer", payload={"reason": "timeout"}),
        Event(event_type=CONFIDENCE_UPDATED, agent_id="writer", payload={"confidence": 0.5}),
    ]

    path = HTMLReportGenerator().generate(events, tmp_path / "report.html")
    text = path.read_text(encoding="utf-8")

    assert "Runtime Observability Report" in text
    assert "Event Summary" in text
    assert "Agent Summary" in text
    assert "Tool Summary" in text
    assert "Memory Summary" in text
    assert "Failure Summary" in text
    assert "Confidence Summary" in text

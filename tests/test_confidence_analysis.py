import json

from analytics.confidence_analysis import ConfidenceAnalyzer
from events import event_types
from events.event import Event


def test_confidence_analyzer_generates_history_trends_and_statistics():
    events = [
        Event(event_type=event_types.CONFIDENCE_UPDATED, agent_id="planner", payload={"confidence": 0.8}),
        Event(event_type=event_types.CONFIDENCE_UPDATED, agent_id="planner", payload={"confidence": 0.6}),
    ]

    report = ConfidenceAnalyzer().analyze(events)

    assert report["planner"] == {
        "history": [0.8, 0.6],
        "trend": "decreasing",
        "min": 0.6,
        "max": 0.8,
        "average": 0.7,
    }


def test_confidence_analyzer_writes_json_report(tmp_path):
    output = tmp_path / "confidence_report.json"
    events = [Event(event_type=event_types.CONFIDENCE_UPDATED, agent_id="writer", payload={"confidence": 0.9})]

    report = ConfidenceAnalyzer().write_report(events, output)

    assert json.loads(output.read_text(encoding="utf-8")) == report

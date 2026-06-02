from events.event import Event
from events.event_types import TOOL_CALLED
from exporters.opentelemetry_exporter import OpenTelemetryExporter


def test_opentelemetry_exporter_maps_events_to_span_like_dicts():
    event = Event(event_type=TOOL_CALLED, agent_id="researcher", payload={"tool_name": "search"}, timestamp="2026-01-01T10:00:00+00:00")

    span = OpenTelemetryExporter().export_event(event).to_dict()

    assert span["name"] == TOOL_CALLED
    assert span["timestamp"] == "2026-01-01T10:00:00+00:00"
    assert span["attributes"]["runtime.agent_id"] == "researcher"
    assert span["attributes"]["runtime.payload.tool_name"] == "search"

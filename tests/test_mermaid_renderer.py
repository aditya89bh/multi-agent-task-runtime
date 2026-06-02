from events.event import Event
from events.event_types import FAILURE_OCCURRED, MEMORY_READ, MEMORY_WRITE, TOOL_CALLED
from visualization.mermaid_renderer import MermaidRenderer


def test_mermaid_renderer_generates_sequence_diagram(tmp_path):
    events = [
        Event(event_type=MEMORY_READ, agent_id="planner", payload={"key": "plan"}),
        Event(event_type=MEMORY_WRITE, agent_id="planner", payload={"key": "draft"}),
        Event(event_type=TOOL_CALLED, agent_id="researcher", payload={"tool_name": "search"}),
        Event(event_type=FAILURE_OCCURRED, agent_id="writer", payload={"reason": "timeout"}),
    ]

    renderer = MermaidRenderer()
    diagram = renderer.render(events)
    path = renderer.write(events, tmp_path / "runtime_diagram.mmd")

    assert "sequenceDiagram" in diagram
    assert "planner->>Memory: read plan" in diagram
    assert "researcher->>Tool_search: call" in diagram
    assert "writer-->>Failure: timeout" in diagram
    assert path.read_text(encoding="utf-8") == diagram

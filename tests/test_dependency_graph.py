from analytics.dependency_graph import AgentDependencyGraph
from events.event import Event
from events.event_types import AGENT_STARTED, MEMORY_READ


def test_dependency_graph_infers_agent_relationships_and_mermaid():
    events = [
        Event(event_type=AGENT_STARTED, agent_id="planner", payload={"task": "demo"}),
        Event(event_type=MEMORY_READ, agent_id="researcher", payload={"task": "demo"}),
        Event(event_type=MEMORY_READ, agent_id="writer", payload={"task": "demo"}),
    ]

    graph = AgentDependencyGraph()
    adjacency = graph.build(events)

    assert adjacency == {"planner": ["researcher"], "researcher": ["writer"]}
    assert "planner --> researcher" in graph.to_mermaid(adjacency)

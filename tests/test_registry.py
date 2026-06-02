from agents.base_agent import BaseAgent
from runtime.event_bus import EventBus
from runtime.registry import AgentRegistry


def test_agent_registry_registers_discovers_and_removes_agents():
    registry = AgentRegistry()
    agent = BaseAgent("planner", EventBus())

    registry.register_agent(agent)

    assert registry.discover_agent("planner") == agent
    assert list(registry.all_agents()) == [agent]
    assert registry.remove_agent("planner") == agent
    assert registry.discover_agent("planner") is None

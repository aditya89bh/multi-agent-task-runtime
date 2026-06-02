from agents.base_agent import BaseAgent
from events.event_types import AGENT_FINISHED, AGENT_STARTED
from runtime.coordinator import RuntimeCoordinator
from runtime.event_bus import EventBus


class EchoAgent(BaseAgent):
    def run(self, **context):
        return {"echo": context["task"]}


def test_runtime_coordinator_executes_agent_and_emits_events():
    bus = EventBus()
    events = []
    bus.subscribe(events.append)
    coordinator = RuntimeCoordinator(bus)
    agent = EchoAgent("planner", bus)

    result = coordinator.execute_agent(agent, task="plan")

    assert result == {"echo": "plan"}
    assert agent.started is True
    assert agent.finished is True
    assert coordinator.execution_context["agents"] == ["planner"]
    assert coordinator.execution_context["results"] == {"planner": {"echo": "plan"}}
    assert [event.event_type for event in events] == [AGENT_STARTED, AGENT_FINISHED]


def test_runtime_coordinator_executes_multiple_agents():
    coordinator = RuntimeCoordinator(EventBus())
    agents = [EchoAgent("planner", EventBus()), EchoAgent("writer", EventBus())]

    results = coordinator.execute_agents(agents, task="demo")

    assert results == [{"echo": "demo"}, {"echo": "demo"}]
    assert coordinator.execution_context["agents"] == ["planner", "writer"]

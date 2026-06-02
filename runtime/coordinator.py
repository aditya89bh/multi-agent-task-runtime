"""Runtime coordinator for observable agent execution."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from agents.base_agent import BaseAgent
from events.event import Event
from events.event_types import AGENT_FINISHED, AGENT_STARTED
from runtime.event_bus import EventBus


class RuntimeCoordinator:
    """Executes agents and maintains run context."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.execution_context: Dict[str, Any] = {"agents": [], "results": {}}

    def execute_agent(self, agent: BaseAgent, **context: Any) -> Any:
        """Execute a single agent lifecycle."""
        self.execution_context["agents"].append(agent.agent_id)
        self.event_bus.publish(
            Event(event_type=AGENT_STARTED, agent_id=agent.agent_id, payload={"context": context})
        )
        agent.started = True
        result = agent.run(**context)
        self.execution_context["results"][agent.agent_id] = result
        agent.finished = True
        self.event_bus.publish(
            Event(event_type=AGENT_FINISHED, agent_id=agent.agent_id, payload={"result": result})
        )
        return result

    def execute_agents(self, agents: Iterable[BaseAgent], **context: Any) -> List[Any]:
        """Execute agents sequentially."""
        return [self.execute_agent(agent, **context) for agent in agents]

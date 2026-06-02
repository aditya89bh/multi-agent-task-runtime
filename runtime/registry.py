"""Agent registry for runtime discovery."""

from __future__ import annotations

from typing import Dict, Iterable, Optional

from agents.base_agent import BaseAgent


class AgentRegistry:
    """Register, remove, and discover agents by id."""

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent instance."""
        self._agents[agent.agent_id] = agent

    def remove_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Remove and return an agent if present."""
        return self._agents.pop(agent_id, None)

    def discover_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Find one agent by id."""
        return self._agents.get(agent_id)

    def all_agents(self) -> Iterable[BaseAgent]:
        """Return all registered agents."""
        return tuple(self._agents.values())

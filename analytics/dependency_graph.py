"""Infer agent dependency graphs from event order and task context."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from events.event import Event


class AgentDependencyGraph:
    """Infer relationships between agents that share task context."""

    def build(self, events: Iterable[Event]) -> dict[str, list[str]]:
        by_context: dict[str, list[str]] = defaultdict(list)
        for event in events:
            if event.agent_id is None:
                continue
            context = str(event.payload.get("task") or event.payload.get("context") or event.payload.get("key") or "default")
            if not by_context[context] or by_context[context][-1] != event.agent_id:
                by_context[context].append(event.agent_id)
        adjacency: dict[str, set[str]] = defaultdict(set)
        for agents in by_context.values():
            for left, right in zip(agents, agents[1:], strict=False):
                if left != right:
                    adjacency[left].add(right)
        return {agent: sorted(targets) for agent, targets in adjacency.items()}

    def to_mermaid(self, adjacency: dict[str, list[str]]) -> str:
        lines = ["graph TD"]
        for source, targets in adjacency.items():
            for target in targets:
                lines.append(f"    {source} --> {target}")
        return "\n".join(lines) + "\n"

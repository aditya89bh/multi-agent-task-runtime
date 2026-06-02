"""Generate Mermaid diagrams from runtime events."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Union

from events.event import Event
from events.event_types import FAILURE_OCCURRED, MEMORY_READ, MEMORY_WRITE, TOOL_CALLED

PathLike = Union[str, Path]


class MermaidRenderer:
    """Render agent/tool/memory interactions as Mermaid sequence diagrams."""

    def render(self, events: Iterable[Event]) -> str:
        lines = ["sequenceDiagram"]
        for event in events:
            agent = self._actor(event.agent_id)
            if event.event_type == TOOL_CALLED:
                tool = str(event.payload.get("tool_name", "tool"))
                lines.append(f"    {agent}->>Tool_{tool}: call")
            elif event.event_type == MEMORY_READ:
                lines.append(f"    {agent}->>Memory: read {event.payload.get('key', '')}")
            elif event.event_type == MEMORY_WRITE:
                lines.append(f"    {agent}->>Memory: write {event.payload.get('key', '')}")
            elif event.event_type == FAILURE_OCCURRED:
                lines.append(f"    {agent}-->>Failure: {event.payload.get('reason') or event.payload.get('message', 'failure')}")
        return "\n".join(lines) + "\n"

    def write(self, events: Iterable[Event], output_path: PathLike = "reports/runtime_diagram.mmd") -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(events), encoding="utf-8")
        return path

    @staticmethod
    def _actor(agent_id: str | None) -> str:
        return (agent_id or "system").replace("-", "_").replace(" ", "_")

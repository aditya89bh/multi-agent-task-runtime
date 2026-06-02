#!/usr/bin/env python3
"""End-to-end observable multi-agent runtime demo."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.base_agent import BaseAgent
from analytics.confidence_tracker import ConfidenceTracker
from events.event import Event
from analytics.drift_detector import DriftDetector
from analytics.failure_analyzer import FailureAnalyzer
from memory.memory_store import MemoryStore
from runtime.coordinator import RuntimeCoordinator
from runtime.event_bus import EventBus
from runtime.event_logger import EventLogger
from runtime.retry_manager import RetryManager
from tools.tool_executor import ToolExecutor
from visualization.timeline_renderer import TimelineRenderer


class PlannerAgent(BaseAgent):
    def __init__(self, agent_id, event_bus, memory, confidence):
        super().__init__(agent_id, event_bus)
        self.memory = memory
        self.confidence = confidence

    def run(self, **context):
        plan = "Research topic, draft summary, validate output"
        self.memory.write("plan", plan, agent_id=self.agent_id)
        self.confidence.update_confidence(self.agent_id, 0.82, reason="plan created")
        return {"plan": plan}


class ResearchAgent(BaseAgent):
    def __init__(self, agent_id, event_bus, memory, tools, confidence):
        super().__init__(agent_id, event_bus)
        self.memory = memory
        self.tools = tools
        self.confidence = confidence

    def run(self, **context):
        plan = self.memory.read("plan", agent_id=self.agent_id)
        research = self.tools.execute("search_notes", context["topic"], agent_id=self.agent_id)
        self.memory.write("research", research, agent_id=self.agent_id)
        self.confidence.update_confidence(self.agent_id, 0.74, reason="research gathered")
        return {"plan_seen": plan, "research": research}


class WriterAgent(BaseAgent):
    def __init__(self, agent_id, event_bus, memory, tools, confidence, failures, retries):
        super().__init__(agent_id, event_bus)
        self.memory = memory
        self.tools = tools
        self.confidence = confidence
        self.failures = failures
        self.retries = retries
        self._attempts = 0

    def run(self, **context):
        research = self.memory.read("research", agent_id=self.agent_id)

        def flaky_write():
            self._attempts += 1
            if self._attempts == 1:
                try:
                    raise RuntimeError("temporary writer formatting failure")
                except RuntimeError as error:
                    self.failures.capture_exception(error, agent_id=self.agent_id, reason="draft generation")
                    raise
            return self.tools.execute("summarize", research, agent_id=self.agent_id)

        draft = self.retries.run(flaky_write, agent_id=self.agent_id, operation_name="write_draft")
        self.memory.write("draft", draft, agent_id=self.agent_id)
        self.confidence.update_confidence(self.agent_id, 0.66, reason="recovered after retry")
        return {"draft": draft}


def main() -> None:
    events: list[Event] = []
    bus = EventBus()
    bus.subscribe(events.append)
    logger = EventLogger(bus)
    memory = MemoryStore(bus)
    tools = ToolExecutor(bus)
    confidence = ConfidenceTracker(bus)
    failures = FailureAnalyzer(bus)
    retries = RetryManager(bus, max_retries=2, base_delay_seconds=0)
    coordinator = RuntimeCoordinator(bus)

    tools.register_tool("search_notes", lambda topic: f"Key findings about {topic}: observability beats guessing.")
    tools.register_tool("summarize", lambda research: f"Summary: {research}")

    agents = [
        PlannerAgent("planner", bus, memory, confidence),
        ResearchAgent("researcher", bus, memory, tools, confidence),
        WriterAgent("writer", bus, memory, tools, confidence, failures, retries),
    ]

    coordinator.execute_agents(agents, topic="multi-agent observability")

    # Add a simple drift pass after the run. The writer confidence is lower than
    # planner confidence and the run has a captured failure, so no artificial
    # events are needed for observability.
    DriftDetector(bus).analyze(events)

    timeline = TimelineRenderer().render(events)
    print("Runtime Timeline")
    print("================")
    print(timeline)
    print()
    print("Event log written to logs/runtime_events.jsonl")
    logger.close()


if __name__ == "__main__":
    main()

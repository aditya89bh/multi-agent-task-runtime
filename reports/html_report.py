"""Generate static HTML observability reports."""

from __future__ import annotations

import html
from collections.abc import Iterable
from pathlib import Path

from analytics.agent_metrics import AgentMetricsCollector
from analytics.confidence_analysis import ConfidenceAnalyzer
from analytics.memory_metrics import MemoryMetricsCollector
from analytics.runtime_metrics import RuntimeMetricsCollector
from analytics.tool_metrics import ToolMetricsCollector
from events.event import Event

PathLike = str | Path


class HTMLReportGenerator:
    """Render event analytics into a lightweight HTML report."""

    def generate(self, events: Iterable[Event], output_path: PathLike = "reports/latest_report.html") -> Path:
        event_list = list(events)
        sections = {
            "Event Summary": RuntimeMetricsCollector().summarize(event_list),
            "Agent Summary": AgentMetricsCollector().summarize(event_list),
            "Tool Summary": ToolMetricsCollector().summarize(event_list),
            "Memory Summary": MemoryMetricsCollector().summarize(event_list),
            "Failure Summary": {"failures": [event.payload for event in event_list if event.event_type == "failure_occurred"]},
            "Confidence Summary": ConfidenceAnalyzer().analyze(event_list),
        }
        body = "\n".join(f"<h2>{html.escape(title)}</h2><pre>{html.escape(str(data))}</pre>" for title, data in sections.items())
        document = f"<!doctype html><html><head><title>Runtime Observability Report</title></head><body><h1>Runtime Observability Report</h1>{body}</body></html>"
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document, encoding="utf-8")
        return path

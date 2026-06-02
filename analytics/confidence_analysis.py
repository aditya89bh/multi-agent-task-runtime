"""Confidence trend analysis and JSON reports."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from statistics import mean
from typing import Any

from events import event_types
from events.event import Event

PathLike = str | Path


class ConfidenceAnalyzer:
    """Generate confidence history, trends, and summary statistics."""

    def analyze(self, events: Iterable[Event]) -> dict[str, dict[str, Any]]:
        histories: dict[str, list[float]] = {}
        for event in events:
            if event.event_type != event_types.CONFIDENCE_UPDATED or event.agent_id is None:
                continue
            histories.setdefault(event.agent_id, []).append(float(event.payload["confidence"]))
        return {agent: self._report_for(values) for agent, values in histories.items()}

    def write_report(self, events: Iterable[Event], output_path: PathLike = "confidence_report.json") -> dict[str, dict[str, Any]]:
        """Write confidence analysis to JSON and return the report."""
        report = self.analyze(events)
        path = Path(output_path)
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return report

    @staticmethod
    def _report_for(values: list[float]) -> dict[str, Any]:
        if not values:
            return {"history": [], "trend": "flat", "min": None, "max": None, "average": None}
        if len(values) < 2 or values[-1] == values[0]:
            trend = "flat"
        elif values[-1] > values[0]:
            trend = "increasing"
        else:
            trend = "decreasing"
        return {
            "history": values,
            "trend": trend,
            "min": min(values),
            "max": max(values),
            "average": mean(values),
        }

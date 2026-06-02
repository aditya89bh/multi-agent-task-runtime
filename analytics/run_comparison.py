"""Compare two runtime event logs."""

from __future__ import annotations

from typing import Dict, Iterable

from analytics.runtime_metrics import RuntimeMetricsCollector
from events.event import Event
from events.event_types import CONFIDENCE_UPDATED


class RunComparison:
    """Compare summary statistics between two runs."""

    def compare(self, baseline: Iterable[Event], candidate: Iterable[Event]) -> Dict[str, Dict[str, float]]:
        left = list(baseline)
        right = list(candidate)
        left_summary = self._summary(left)
        right_summary = self._summary(right)
        return {
            key: {"baseline": left_summary[key], "candidate": right_summary[key], "delta": right_summary[key] - left_summary[key]}
            for key in left_summary
        }

    def _summary(self, events: list[Event]) -> Dict[str, float]:
        metrics = RuntimeMetricsCollector().summarize(events)
        confidence = [float(event.payload["confidence"]) for event in events if event.event_type == CONFIDENCE_UPDATED]
        return {
            "total_events": float(metrics["total_events"]),
            "failures": float(metrics["failures"]),
            "retries": float(metrics["retries"]),
            "tool_calls": float(metrics["tool_calls"]),
            "memory_reads": float(metrics["memory_reads"]),
            "memory_writes": float(metrics["memory_writes"]),
            "average_confidence": sum(confidence) / len(confidence) if confidence else 0.0,
        }

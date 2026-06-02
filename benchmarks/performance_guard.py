"""Compare benchmark results against loose regression baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASELINE_PATH = Path("benchmarks/performance_baseline.json")


def load_json(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("performance data must be a JSON object")
    return loaded


def compare_performance(result: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    """Return pass/fail details while ignoring minor benchmark variance."""
    failures: list[dict[str, Any]] = []
    for suite, suite_baseline in baseline.items():
        if suite not in result or not isinstance(suite_baseline, dict):
            continue
        suite_result = result[suite]
        if not isinstance(suite_result, dict):
            continue
        threshold = float(suite_baseline.get("regression_threshold", 0.5))
        for metric, expected_value in suite_baseline.items():
            if metric == "regression_threshold" or metric not in suite_result:
                continue
            actual = float(suite_result[metric])
            expected = float(expected_value)
            minimum_allowed = expected * (1 - threshold)
            if actual < minimum_allowed:
                failures.append({"suite": suite, "metric": metric, "actual": actual, "minimum_allowed": minimum_allowed})
    return {"passed": not failures, "failures": failures}


def main() -> int:
    result_path = Path("benchmarks/results/performance_results.json")
    comparison = compare_performance(load_json(result_path), load_json(BASELINE_PATH))
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0 if comparison["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

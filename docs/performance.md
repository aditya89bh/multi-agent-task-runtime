# Performance Baseline

`benchmarks/performance_baseline.json` stores intentionally loose baseline values for production-readiness checks.

The guard is designed to catch large regressions, not normal benchmark noise from shared CI machines.

## Interpreting results

- A pass means measured throughput stayed above the configured minimum after tolerance.
- A failure means one or more metrics fell below `baseline * (1 - regression_threshold)`.
- Update the baseline only after an intentional performance-changing commit and a clean local benchmark run.

## Usage

```bash
python benchmarks/performance_guard.py
```

Expected input:

```text
benchmarks/results/performance_results.json
```

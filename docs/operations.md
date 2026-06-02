# Operational Debugging Guide

This guide describes practical workflows for debugging and analyzing multi-agent runtime behavior.

## Replay Workflow

1. Run a demo or application that writes JSONL logs:

   ```bash
   python examples/multi_agent_demo.py
   ```

2. Confirm the log exists:

   ```bash
   ls logs/runtime_events.jsonl
   ```

3. Load and replay events with `ReplayEngine`:

   ```python
   from runtime.replay_engine import ReplayEngine

   engine = ReplayEngine()
   events = engine.load_jsonl("logs/runtime_events.jsonl")
   for event in engine.replay(events):
       print(event)
   ```

4. Reconstruct a timeline:

   ```python
   print(engine.reconstruct_timeline(events))
   ```

## Debugging Workflow

When an agent output looks wrong, inspect the event stream in this order:

1. `AGENT_STARTED` — did the agent receive the expected context?
2. `MEMORY_READ` — did the agent read the expected memory keys?
3. `TOOL_CALLED` — did it call the expected tools with the expected inputs?
4. `TOOL_RETURNED` — did tools return expected outputs and durations?
5. `CONFIDENCE_UPDATED` — did confidence rise or fall during execution?
6. `FAILURE_OCCURRED` — did exceptions occur?
7. `RETRY_STARTED` / `RETRY_COMPLETED` — did retries recover or loop?
8. `AGENT_FINISHED` — what final result was produced?

## Querying Events

SQLite storage supports event queries:

```python
from runtime.sqlite_store import SQLiteEventStore

store = SQLiteEventStore("runtime.db")
failures = store.get_events(event_type="failure_occurred")
planner_events = store.get_events(agent_id="planner")
time_window = store.get_events(
    start_time="2026-01-01T10:00:00+00:00",
    end_time="2026-01-01T10:05:00+00:00",
)
```

For in-memory event lists, use reusable filters:

```python
from events.filters import filter_events

planner_failures = filter_events(events, event_type="failure_occurred", agent_id="planner")
```

## Drift Analysis

Use `DriftDetector` to identify behavioral changes:

```python
from analytics.drift_detector import DriftDetector
from runtime.event_bus import EventBus

bus = EventBus()
detections = DriftDetector(bus).analyze(events)
```

Current heuristics detect:

- confidence decay
- confidence collapse
- repeated failures
- persistent failure patterns
- repeated retry loops
- changing plans
- inconsistent memory access
- memory inconsistency

## Metrics Workflow

Runtime-wide metrics:

```python
from analytics.runtime_metrics import RuntimeMetricsCollector

summary = RuntimeMetricsCollector().summarize(events)
```

Agent metrics:

```python
from analytics.agent_metrics import AgentMetricsCollector

agent_summary = AgentMetricsCollector().summarize(events)
```

Memory metrics:

```python
from analytics.memory_metrics import MemoryMetricsCollector

memory_summary = MemoryMetricsCollector().summarize(events)
```

Tool metrics:

```python
from analytics.tool_metrics import ToolMetricsCollector

tool_summary = ToolMetricsCollector().summarize(events)
```

Confidence report:

```python
from analytics.confidence_analysis import ConfidenceAnalyzer

ConfidenceAnalyzer().write_report(events, "confidence_report.json")
```

## Dashboard Workflow

After generating logs:

```bash
python dashboard/live_dashboard.py
```

The dashboard shows:

- active agents
- confidence
- tool activity
- memory activity
- failures
- retries

It uses Rich when available and falls back to plain terminal output.

## Benchmark Usage

Run:

```bash
python benchmarks/runtime_benchmark.py
```

Output is written to:

```text
benchmarks/results/latest_results.json
```

Benchmark output includes:

- number of agents
- generated event volume
- duration
- events per second
- runtime metric summary

Use benchmarks to compare event-processing changes over time.

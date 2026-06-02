# Results

This document captures expected output from the current runtime demo.

## Validation

```bash
pytest
```

Expected result:

```text
22 passed
```

## Demo Command

```bash
python examples/multi_agent_demo.py
```

## Demo Output Excerpt

```text
Runtime Timeline
================
... | planner | agent_started | context={'topic': 'multi-agent observability'}
... | planner | memory_write | key='plan', value='Research topic, draft summary, validate output'
... | planner | confidence_updated | confidence=0.82, reason='plan created'
... | researcher | memory_read | found=True, key='plan', value='Research topic, draft summary, validate output'
... | researcher | tool_called | args=['multi-agent observability'], kwargs={}, tool_name='search_notes'
... | researcher | tool_returned | duration_ms=..., result='Key findings about multi-agent observability: observability beats guessing.', tool_name='search_notes'
... | writer | failure_occurred | exception_type='RuntimeError', message='temporary writer formatting failure', reason='draft generation'
... | writer | retry_started | attempt=1, error='temporary writer formatting failure', operation_name='write_draft'
... | writer | retry_completed | attempt=1, operation_name='write_draft'
... | writer | memory_write | key='draft', value='Summary: Key findings about multi-agent observability: observability beats guessing.'
... | writer | confidence_updated | confidence=0.66, reason='recovered after retry'
```

## Event Samples

JSONL event sample from `logs/runtime_events.jsonl`:

```json
{"agent_id": "planner", "event_type": "agent_started", "payload": {"context": {"topic": "multi-agent observability"}}, "timestamp": "..."}
{"agent_id": "planner", "event_type": "memory_write", "payload": {"key": "plan", "value": "Research topic, draft summary, validate output"}, "timestamp": "..."}
{"agent_id": "researcher", "event_type": "tool_called", "payload": {"args": ["multi-agent observability"], "kwargs": {}, "tool_name": "search_notes"}, "timestamp": "..."}
{"agent_id": "writer", "event_type": "failure_occurred", "payload": {"exception_type": "RuntimeError", "message": "temporary writer formatting failure", "reason": "draft generation", "stack_trace": "..."}, "timestamp": "..."}
{"agent_id": "writer", "event_type": "retry_started", "payload": {"attempt": 1, "error": "temporary writer formatting failure", "operation_name": "write_draft"}, "timestamp": "..."}
```

## Timeline Example

The timeline renderer turns an event stream into chronological lines:

```text
timestamp | agent_id | event_type | payload
```

This makes agent behavior inspectable without needing a dashboard yet.

## Current Coverage

The repository currently tests:

- event model serialization
- event bus subscribe/unsubscribe/publish
- JSONL event persistence
- observable memory reads/writes
- observable tool calls/returns
- agent lifecycle events
- confidence updates
- failure capture
- retry management
- runtime coordination
- agent registry
- drift detection
- timeline rendering

## Extended Validation

Additional validation commands:

```bash
python benchmarks/runtime_benchmark.py
python dashboard/live_dashboard.py
```

Expected generated artifacts:

```text
logs/runtime_events.jsonl
benchmarks/results/latest_results.json
```

## Analytics Added

The framework now includes collectors for:

- runtime-wide event totals
- per-agent performance
- memory access frequency
- tool usage and duration
- confidence history and trend reports
- drift detection signals

## Replay and Storage

Events can be persisted to SQLite, queried by event type, agent, or time range, and replayed into chronological timelines.

## Visual Assets

Generated examples are available in `assets/screenshots/`:

```text
assets/screenshots/live_dashboard.txt
assets/screenshots/replay_timeline.txt
assets/screenshots/benchmark_output.txt
assets/screenshots/latest_report.html
assets/screenshots/runtime_diagram.mmd
```

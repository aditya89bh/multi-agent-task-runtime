# Multi-Agent Task Runtime

[![Version](https://img.shields.io/badge/version-v0.1.0-blue)](https://github.com/aditya89bh/multi-agent-task-runtime/releases/tag/v0.1.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-82%20passing-brightgreen)](#quality)
[![Coverage](https://img.shields.io/badge/coverage-95.61%25-brightgreen)](#quality)


Understand what your agents are actually doing.

## Project Overview

Multi-Agent Task Runtime is an observability-first execution framework for agent systems. It provides visibility into:

- Agent task execution
- Agent-to-agent communication
- Memory reads and writes
- Tool invocations
- Confidence evolution
- Failures and retries
- Planning decisions
- Behavioral drift
- Runtime metrics


## Installation

Clone the repository and install it locally:

```bash
git clone https://github.com/aditya89bh/multi-agent-task-runtime.git
cd multi-agent-task-runtime
python -m pip install -e .
```

For development checks:

```bash
python -m pip install pytest pytest-cov mypy ruff build
```

## Quick Start

Run the observable multi-agent demo:

```bash
python examples/multi_agent_demo.py
```

Inspect the generated event log:

```bash
runtime-inspect --jsonl logs/runtime_events.jsonl
runtime-search --jsonl logs/runtime_events.jsonl --event-type failure_occurred
```

Generate benchmark output:

```bash
python benchmarks/runtime_benchmark.py
```

## Motivation

Most agent frameworks show final outputs.
This project focuses on making internal runtime behavior observable and debuggable.

The design rule is simple:

> Everything that happens in the system should generate an event.

This repository intentionally does **not** add LLM integrations, Streamlit, or another heavy agent framework yet. The priority is runtime observability.

## Architecture

```text
User Request
 |
 v
Runtime Coordinator
 |
 +------------------+
 |                  |
 v                  v
Agent A            Agent B
 |                  |
 v                  v
Memory Layer       Tool Layer
 |                  |
 +--------+---------+
          |
          v
    Event Stream
          |
          v
Observability Dashboard / Timeline
```

Core modules:

- `events/` — event model and canonical event types
- `runtime/` — event bus, event logger, coordinator, retry manager, registry
- `agents/` — observable base agent lifecycle
- `memory/` — observable memory store
- `tools/` — observable tool executor
- `analytics/` — confidence tracking, failure tracking, drift detection
- `visualization/` — timeline rendering
- `examples/` — runnable multi-agent demo
- `tests/` — unit coverage for runtime behavior

## Event Flow

Every major runtime action emits an event:

```text
Agent starts        -> AGENT_STARTED
Memory write        -> MEMORY_WRITE
Memory read         -> MEMORY_READ
Tool called         -> TOOL_CALLED
Tool returned       -> TOOL_RETURNED
Confidence changes  -> CONFIDENCE_UPDATED
Failure captured    -> FAILURE_OCCURRED
Retry starts        -> RETRY_STARTED
Retry completes     -> RETRY_COMPLETED
Drift detected      -> DRIFT_DETECTED
Agent finishes      -> AGENT_FINISHED
```

Events flow through `EventBus` and can be consumed by:

- in-memory collectors
- `EventLogger` JSONL persistence
- timeline renderers
- future dashboards
- future metrics exporters

## Runtime Concepts

### Task Runtime

Coordinates execution while preserving an event stream of what happened.

### Agent Registry

Registers and discovers agents by ID.

### Event Stream

The central observability primitive. Runtime components publish structured `Event` objects.

### Memory Tracing

`MemoryStore` emits read/write events with key, value, and hit/miss metadata.

### Tool Tracing

`ToolExecutor` emits tool call and return events, including duration.

### Confidence Tracking

`ConfidenceTracker` records confidence history per agent and emits updates.

### Failure Analysis

`FailureAnalyzer` captures exception type, message, reason, and stack trace.

### Retry Management

`RetryManager` emits retry start/completion events and supports exponential backoff.

### Drift Detection

`DriftDetector` detects early signals such as confidence decay, repeated failures, changing plans, and inconsistent memory access.

## Example Output

Run:

```bash
python examples/multi_agent_demo.py
```

Example timeline excerpt:

```text
Runtime Timeline
================
... | planner | agent_started | context={'topic': 'multi-agent observability'}
... | planner | memory_write | key='plan', value='Research topic, draft summary, validate output'
... | researcher | tool_called | args=['multi-agent observability'], kwargs={}, tool_name='search_notes'
... | writer | failure_occurred | exception_type='RuntimeError', message='temporary writer formatting failure'
... | writer | retry_started | attempt=1, error='temporary writer formatting failure', operation_name='write_draft'
... | writer | retry_completed | attempt=1, operation_name='write_draft'
... | writer | agent_finished | result={'draft': 'Summary: ...'}
```

The demo also writes JSONL events to:

```text
logs/runtime_events.jsonl
```

See `RESULTS.md` for sample outputs.

## Repository Structure

```text
multi-agent-task-runtime/
├── agents/
├── analytics/
├── docs/
├── events/
├── examples/
├── memory/
├── runtime/
├── tests/
├── tools/
└── visualization/
```

## Future Roadmap

### Phase 1

- Runtime event bus
- Agent lifecycle tracking
- Tool call tracking
- Memory event tracking

### Phase 2

- Confidence monitoring
- Failure monitoring
- Retry visualization
- Timeline playback

### Phase 3

- Drift detection
- Agent performance analytics
- Multi-run comparison
- Dashboard UI

### Phase 4

- OpenAI integration
- Anthropic integration
- Local model integration
- Production deployment examples

## Developer-Grade Observability Features

The runtime now includes:

- SQLite event storage via `SQLiteEventStore`
- event query filters by type, agent, and time window
- JSONL and SQLite replay through `ReplayEngine`
- concise replay timelines through `ReplayTimelineRenderer`
- runtime, agent, memory, tool, and confidence analytics
- improved drift detection heuristics
- terminal dashboard via `dashboard/live_dashboard.py`
- benchmark suite via `benchmarks/runtime_benchmark.py`
- GitHub Actions CI, coverage, CodeQL, dependency audit, and release workflows

## Operational Commands

```bash
pytest
python examples/multi_agent_demo.py
python dashboard/live_dashboard.py
python benchmarks/runtime_benchmark.py
```

See `docs/operations.md` for replay, querying, drift analysis, dashboard, and benchmark workflows.

## Dashboard Screenshot

Terminal dashboard sample output is stored at [`assets/screenshots/live_dashboard.txt`](assets/screenshots/live_dashboard.txt).

```text
Runtime Observability Dashboard
================================
... event totals, failures, confidence, memory, and tool metrics ...
```

## Screenshots and Generated Examples

Generated text assets live in `assets/screenshots/`:

- `live_dashboard.txt` — terminal dashboard output
- `replay_timeline.txt` — replay timeline output from the demo
- `benchmark_output.txt` — runtime benchmark output
- `latest_report.html` — generated HTML observability report
- `runtime_diagram.mmd` — Mermaid runtime sequence diagram

## Example Commands

```bash
python examples/multi_agent_demo.py
python dashboard/live_dashboard.py
python benchmarks/runtime_benchmark.py
python benchmarks/stress_benchmark.py --small
runtime-search --jsonl logs/runtime_events.jsonl --event-type failure_occurred
runtime-inspect --jsonl logs/runtime_events.jsonl
```

## Quality

- 82 automated tests
- 95.61% test coverage
- `mypy .` validation
- `ruff check .` and `ruff format --check .` validation
- Package build validation with `python -m build`
- Docker packaging
- Security hardening notes in `docs/security.md`

## Production-Readiness Status

Approximate status: moving toward production readiness for local/runtime observability.

This project does:

- capture structured runtime events
- persist and replay event logs
- query JSONL and SQLite traces
- generate analytics and reports
- provide terminal inspection tools
- support plugins and custom events
- benchmark event throughput

This project does not yet do:

- distributed orchestration
- hosted dashboards
- authentication or multi-tenant access control
- vendor-specific LLM tracing
- managed telemetry ingestion

## Docker

Build the image:

```bash
docker build -t multi-agent-task-runtime .
```

Run the demo:

```bash
docker run --rm multi-agent-task-runtime
```

Run tests inside the image:

```bash
docker run --rm multi-agent-task-runtime pytest
```

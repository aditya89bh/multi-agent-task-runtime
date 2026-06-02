# Architecture

Multi-Agent Task Runtime is an observability-first runtime for multi-agent systems.

The central rule is:

```text
Everything that happens in the system generates an event.
```

The project does not try to be another agent framework. It provides the runtime layer needed to understand agent execution.

## Goals

- Make task execution observable
- Trace memory reads and writes
- Trace tool calls and outcomes
- Track confidence changes across a run
- Capture failures and retries
- Detect behavioral drift across tasks and runs
- Provide a dashboard-friendly event stream

## Non-Goals

This project is not currently intended to provide:

- LLM provider integrations
- Streamlit or dashboard UI
- distributed task execution
- model serving
- long-term vector memory
- workflow orchestration

Those can be added later after the runtime event model is stable.

## Core Components

### Event Model

`events/event.py` defines the core `Event` dataclass:

- `event_type`
- `timestamp`
- `agent_id`
- `payload`

`events/event_types.py` defines canonical event names such as `AGENT_STARTED`, `MEMORY_READ`, `TOOL_CALLED`, and `DRIFT_DETECTED`.

### Event Bus

`runtime/event_bus.py` implements synchronous publish/subscribe event routing.

The event bus supports:

- `subscribe()`
- `unsubscribe()`
- `publish()`

Multiple subscribers can consume the same event stream.

### Event Logger

`runtime/event_logger.py` subscribes to the event bus and writes every event to JSONL:

```text
logs/runtime_events.jsonl
```

This gives the runtime a durable trace without requiring an observability backend.

### Memory Store

`memory/memory_store.py` implements an observable key-value memory store.

Every operation emits an event:

- `write()` -> `MEMORY_WRITE`
- `read()` -> `MEMORY_READ`

### Tool Executor

`tools/tool_executor.py` registers and executes Python callables.

Every tool run emits:

- `TOOL_CALLED`
- `TOOL_RETURNED`

Returned events include execution duration.

### Base Agent

`agents/base_agent.py` provides a minimal observable lifecycle:

- `start()` -> `AGENT_STARTED`
- `run()` -> subclass behavior
- `finish()` -> `AGENT_FINISHED`

### Runtime Coordinator

`runtime/coordinator.py` executes agents sequentially and maintains execution context.

It emits lifecycle events around agent execution so coordinated runs are observable.

### Agent Registry

`runtime/registry.py` tracks agents by ID and supports:

- register agent
- remove agent
- discover agent

### Confidence Tracker

`analytics/confidence_tracker.py` records confidence history per agent and emits `CONFIDENCE_UPDATED`.

### Failure Analyzer

`analytics/failure_analyzer.py` captures:

- exception type
- message
- failure reason
- stack trace

It emits `FAILURE_OCCURRED`.

### Retry Manager

`runtime/retry_manager.py` provides configurable retries and optional exponential backoff.

It emits:

- `RETRY_STARTED`
- `RETRY_COMPLETED`

### Drift Detector

`analytics/drift_detector.py` detects early behavioral drift signals:

- confidence decay
- repeated failures
- changing plans
- inconsistent memory access

It emits `DRIFT_DETECTED`.

### Timeline Renderer

`visualization/timeline_renderer.py` converts the event stream into a chronological human-readable timeline.

## Event Flow

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
          +--> JSONL Event Logger
          |
          +--> Timeline Renderer
          |
          v
Observability Dashboard (future)
```

## Demo Flow

`examples/multi_agent_demo.py` wires together:

- `PlannerAgent`
- `ResearchAgent`
- `WriterAgent`
- memory reads/writes
- tool calls
- confidence updates
- failure capture
- retry events
- timeline rendering
- JSONL logging

Run:

```bash
python examples/multi_agent_demo.py
```

## Design Principles

Prefer:

- explicit events
- small modules
- simple interfaces
- observable execution
- standard library first

Avoid:

- hidden magic
- premature framework abstractions
- dashboard work before event semantics are stable
- LLM integrations before runtime behavior is testable

## Persistence and Replay Layer

`runtime/sqlite_store.py` provides `SQLiteEventStore`, which persists all event fields and supports queries by event type, agent ID, and time range.

`runtime/replay_engine.py` loads JSONL logs or SQLite logs, replays events sequentially, and reconstructs timelines.

`visualization/replay_timeline.py` provides concise replay-oriented output such as:

```text
[10:00:01] Planner started
[10:00:02] Memory read
[10:00:03] Tool call
[10:00:04] Confidence updated
```

## Analytics Layer

The analytics layer now includes:

- runtime metrics
- agent performance metrics
- memory metrics
- tool metrics
- confidence trend analysis
- drift detection

These modules consume event streams and produce summaries without changing runtime execution.

## Operations and Tooling

The repository includes:

- terminal dashboard
- runtime benchmark suite
- operational debugging guide
- CI workflow
- coverage workflow
- CodeQL workflow
- dependency audit workflow
- release workflow

## Event Lifecycle

1. Runtime component creates an `Event` with `event_type`, `agent_id`, `payload`, `timestamp`, and `schema_version`.
2. `EventBus.publish()` sends the event to subscribers.
3. Subscribers may include loggers, plugins, dashboards, metrics collectors, or custom application hooks.
4. Events can be persisted to JSONL, compressed JSONL archives, or SQLite.
5. Replay and analytics tools consume persisted events without re-running agents.

## Storage Backends

- JSONL: append-only developer-friendly logs.
- `.jsonl.gz`: compressed event archives for long-running traces.
- SQLite: queryable local event database with filters for event type, agent ID, and time windows.

## Replay Architecture

`ReplayEngine` loads JSONL or SQLite logs and yields chronological events. Replay output can feed:

- `TimelineRenderer`
- `ReplayTimelineRenderer`
- analytics collectors
- dashboards
- HTML reports
- Mermaid diagrams

## Analytics Architecture

Analytics modules are read-only consumers of event streams. They do not modify runtime behavior.

Available analytics include:

- runtime metrics
- agent metrics
- memory metrics
- tool metrics
- confidence trends
- drift detection
- failure heatmaps
- dependency graphs
- comparative run analysis

## CLI Workflows

Search events:

```bash
runtime-search --jsonl logs/runtime_events.jsonl --event-type failure_occurred
runtime-search --sqlite runtime.db --agent-id planner
```

Inspect runs:

```bash
runtime-inspect --jsonl logs/runtime_events.jsonl
runtime-inspect --sqlite runtime.db
```

## Production Readiness Notes

The project is moving toward production readiness while remaining intentionally lightweight.

Current strengths:

- event schema versioning
- queryable SQLite backend
- compressed archives
- replay engine
- plugin hooks
- CLI inspection/search
- CI, coverage, CodeQL, dependency audit, release workflow
- stress benchmarks

Still intentionally out of scope:

- LLM vendor integrations
- hosted observability service
- distributed tracing backend ownership
- remote agent orchestration
- authentication/authorization

The recommended production path is to keep this runtime as the local instrumentation layer and export events to external telemetry systems when needed.

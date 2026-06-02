# Multi-Agent Task Runtime

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

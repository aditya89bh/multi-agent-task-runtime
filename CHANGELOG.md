# Changelog

All notable changes to `multi-agent-task-runtime` will be documented in this file.

The project follows semantic versioning: `MAJOR.MINOR.PATCH`.

## v0.1.0 - Initial production-hardening baseline

### Runtime

- Structured runtime event model with event type, agent ID, payload, timestamp, and schema version.
- Observable event bus, JSONL logger, SQLite event store, replay engine, plugin hooks, and custom event registration.
- Retry, coordination, registry, and lifecycle instrumentation for multi-agent examples.

### Observability

- Timeline renderers, replay timelines, live terminal dashboard, Mermaid runtime diagrams, and HTML observability reports.
- Lightweight OpenTelemetry-style exporter for trace-like event spans.

### Replay and Storage

- JSONL event logs, SQLite storage/querying, and compressed `.jsonl.gz` event archives.
- Replay-compatible loading for persisted event streams.

### Analytics

- Runtime, agent, memory, tool, confidence, drift, failure, failure heatmap, dependency graph, and comparative run analytics.

### CLI

- `runtime-search` for JSONL/SQLite event search.
- `runtime-inspect` for JSONL/SQLite run summaries.

### Benchmarks

- Runtime benchmark suite and large-scale stress benchmark with CI-safe mode.

### Release Readiness

- CI workflows for tests, coverage artifacts, CodeQL, dependency audit, and releases.
- Architecture, operations, results, and production-readiness documentation.

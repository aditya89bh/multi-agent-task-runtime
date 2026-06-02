# Security Notes

This project is a local developer/runtime observability library. It is not a hosted service and does not implement authentication, authorization, tenancy, or network exposure controls.

## Current hardening

- Event validation rejects malformed event types, timestamps, agent IDs, payloads, and schema versions.
- SQLite queries use parameter binding for user-supplied filters.
- SQLite initialization uses a schema migration table and forward-compatible migration hooks.
- JSONL replay skips malformed or partially written events and exposes skipped-line counts.
- Archive helpers validate input files, reject output directories, and prevent source/target overwrite collisions.
- CLI log/database arguments must point to existing files.
- HTML report output escapes rendered content and rejects directory output paths.
- Event bus, JSONL logger, and SQLite store have thread-safety protections.

## Operator responsibilities

- Do not expose generated logs or reports publicly if payloads contain sensitive data.
- Treat event payloads as application data; avoid writing secrets unless explicitly required.
- Run CLI tools only against trusted local paths.
- Use external platform controls for authentication, authorization, retention, and audit logging.

## Out of scope for v0.1.0

- Remote ingestion endpoints.
- Multi-tenant isolation.
- Encryption-at-rest management.
- User/session access control.
- Sandboxing arbitrary plugins.

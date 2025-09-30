# ADR-0014-observability-logging-and-progress.md

## Title

Observability: structured logging & progress

## Status

Proposed

## Context

MCP clients surface log and progress to users; this is vital for long IO.

## Decision

* Use `ctx.debug/info/warning/error` with structured, terse messages.
* Report **milestones** via `ctx.report_progress(progress, total)` (start/50%/100% minimum).
* Include request IDs and URIs in logs (no secrets).

## Consequences

* Pro: Clear UX; easier troubleshooting.
* Con: Small runtime cost to track progress.

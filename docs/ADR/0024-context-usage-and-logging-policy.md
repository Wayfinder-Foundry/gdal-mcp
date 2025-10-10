---
status: accepted
date: 2025-10-10
decision-makers: [jgodau, cascade-ai]
tags: [context, logging, fastmcp, architecture]
---

# ADR-0024: Context Usage and Logging Policy

## Context

FastMCP injects a `Context` object into tools, resources, and prompts. It offers
capabilities for logging, progress reporting, resource access, and request
metadata. Without guardrails, `Context` can become a "god object" accumulating
business logic, global state, and verbose logging scattered across layers,
leading to noisy outputs and brittle code.

As the GDAL MCP server grows, we need predictable, low-noise logging and a clear
boundary between orchestration (MCP entry points) and core logic (shared
modules). This ADR formalizes the allowed uses of `Context`, the layers where it
may appear, and patterns that keep logging meaningful.

## Decision

Adopt the following policy for `Context` usage and logging:

### 1. Layer Responsibilities
- **MCP entry points** (`src/tools/`, `src/resources/`, `src/prompts/`):
  - Own all user-facing logging (`ctx.info/debug/warning/error`).
  - Own progress reporting (`ctx.report_progress`).
  - Access request metadata (`ctx.request_id`, `ctx.client_id`) for telemetry.
  - Pass `ctx` downstream only when subroutines genuinely need to log or
    report progress.
- **Shared modules** (`src/shared/…`):
  - Remain pure by default; accept `ctx: Context | None = None` but do not log
    unless explicitly instructed by callers.
  - Provide targeted helpers when deeper logging is essential.

### 2. Allowed Uses of `Context`
- Logging through `ctx.info/debug/warning/error`.
- Progress reporting via `ctx.report_progress`.
- Reading resources with `ctx.read_resource`.
- Accessing request metadata (`request_id`, `client_id`).
- Per-request scratch state using `ctx.set_state` / `ctx.get_state`.
- Optional LLM sampling (`ctx.sample`) when necessary.

### 3. Prohibited Uses
- Persisting data across requests (no global state).
- Embedding business logic or branching within `Context` helpers.
- Transporting large payloads or raw datasets via context state/logs.
- Managing configuration values.
- Performing blocking IO inside context helpers (do it in the caller instead).

### 4. Logging Guidelines
- Log at the boundary: start/end messages, key milestones, recoverable errors.
- Avoid duplicate log entries between callers and callees.
- Keep shared utilities silent unless the caller passes `ctx` with intent to log.
- Use consistent prefixes (e.g., `[raster_info]`) for fast filtering.
- Prefer progress updates over chatty info logs for long loops.

### 5. Exposure Pattern
- `Context` is optional in shared helpers (`ctx: Context | None = None`).
- Entry points decide whether to forward `ctx` downstream.
- New helpers that require logging should live in `src/shared/context_logging.py`
  (future work) to centralize formatting and throttling.

## Consequences

- **Positive**: Predictable logs, cleaner separation between orchestration and
  business logic, easier testing of shared modules, and reduced risk of context
  becoming a god object.
- **Negative**: Requires discipline during code reviews; developers must avoid
  reintroducing logging deep in the stack without justification.
- **Neutral**: Some helpers may receive `ctx` parameters they do not use; this is
  acceptable to keep signatures consistent.

## Implementation Notes

- Update documentation in `docs/fastmcp/CONTEXT.md` summarizing allowed and
  forbidden patterns.
- Add checklist item to code reviews: "Context usage limited to allowed layer?"
- Consider lightweight tooling to flag `ctx.` usages outside approved modules.

## Status

Accepted — 2025-10-10

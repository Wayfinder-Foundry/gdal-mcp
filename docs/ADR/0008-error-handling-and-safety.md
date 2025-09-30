# ADR-0008-error-handling-and-safety.md

## Title

Error handling, masking, and tool safety annotations

## Status

Proposed

## Context

We need user-safe errors and clear risk signaling in MCP UIs.

## Decision

* Initialize FastMCP with `mask_error_details=True`.
* Raise `ToolError("human message")` for expected failures; let unexpected exceptions be masked.
* Use annotations: `readOnlyHint` for info/VRT tools; `destructiveHint` only when writing; `idempotentHint` where applicable.

## Consequences

* Pro: Safer UX; predictable error semantics; clearer consent surfaces.
* Con: Must be disciplined about distinguishing expected vs unexpected errors.

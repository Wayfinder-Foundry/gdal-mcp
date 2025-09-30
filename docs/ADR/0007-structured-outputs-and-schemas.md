# ADR-0007-structured-outputs-and-schemas.md

## Title

Return structured outputs with schemas by default

## Status

Proposed

## Context

MCP/FastMCP can auto-emit JSON schemas from type hints, enabling reliable chaining and UI validation.

## Decision

* Tools return **dataclasses / Pydantic models** for structured outputs.
* Primitive returns allowed but prefer explicit models for clarity.
* Include concise human-readable text alongside structured content when helpful.

## Consequences

* Pro: Strong contracts; easier downstream use; better client UX.
* Con: Slight overhead defining models.

---
task_id: "2004"
title: "Add epistemic middleware enforcement and policy hooks"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-19"
updated: "2025-10-19"
tags:
  - epistemology
  - middleware
  - enforcement
depends_on:
  - "2001"
  - "2002"
  - "2003"
---

## Summary
Implement the middleware gate that enforces justification requirements, integrates with risk classification, and returns receipts per sections 7-8 of `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

## Rationale
To convert documentation into action, tool handlers must consult middleware that blocks or warns when justification is missing or stale. This ensures governance policies are enforced consistently.

## Deliverables
- **[middleware]** `mcp/epistemic/middleware.py` with `require_justification()` hook, stale detection, and policy branching.
- **[config]** Extend `mcp/config.py` (or equivalent) with `CRITICAL_TOOLS` and helper flags.
- **[tests]** `tests/test_epistemic_middleware.py` covering proceed, warn, block, and cache-hit scenarios.
- **[docs]** Update implementation plan checklist for sections 7-8.

## Acceptance Criteria
- **[integration]** Middleware composes with risk classification, hashing, store, and receipts without circular imports.
- **[policy]** Warnings triggered when hash mismatch occurs; blocking respects `CRITICAL_TOOLS` list.
- **[observability]** Returned payloads include receipt metadata for downstream logging/UI.

## Notes
- Coordinate with task 2005 for tool integration to avoid duplication.
- Ensure `.epistemic/` directory is respected when storing justifications in tests.

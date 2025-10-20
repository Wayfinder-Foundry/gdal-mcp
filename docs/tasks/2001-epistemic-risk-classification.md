---
task_id: "2001"
title: "Implement epistemic risk classification module"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-19"
updated: "2025-10-19"
tags:
  - epistemology
  - middleware
  - risk
depends_on:
  - "0026"
---

## Summary
Build `mcp/risk/` with risk-class enumeration, tool classification logic, and stable input hashing per `docs/design/epistemology/IMPLEMENTATION_PLAN.md` sections 1-2.

## Rationale
Risk detection is the entry point for epistemic enforcement. Without deterministic classification and hashing, preflight prompts and receipts cannot be activated.

## Deliverables
- **[module]** `mcp/risk/classes.py` defining `RiskClass` and `classify()` with unit docstrings.
- **[hashing]** `mcp/risk/hashing.py` implementing normalized payload hashing keyed by relevant arguments.
- **[tests]** `tests/test_epistemic_risk.py` covering classification branches and hash stability.
- **[docs]** Update `docs/design/epistemology/IMPLEMENTATION_PLAN.md` checklist to reflect module completion.

## Acceptance Criteria
- **[deterministic]** Hash function returns stable values for identical payloads regardless of argument ordering.
- **[coverage]** Tests exercise CRS, resampling, hydrology, aggregation, and none cases.
- **[integration]** Module imports cleanly in future middleware code without circular dependencies.

## Notes
- Follow naming in the plan (`RiskClass`, `classify`, `input_hash`).
- Coordinate with task 2002 (epistemic schema/middleware) to share fixtures.

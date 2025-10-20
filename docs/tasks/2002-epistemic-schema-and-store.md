---
task_id: "2002"
title: "Implement epistemic schema, store, and receipts"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-19"
updated: "2025-10-19"
tags:
  - epistemology
  - storage
  - observability
depends_on:
  - "2001"
---

## Summary
Create the `mcp/epistemic/` package with Pydantic models, disk-backed storage, and receipt helpers as outlined in sections 3-5 of `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

## Rationale
Justification artifacts must be schema-validated, persisted, and observable. The schema, store, and receipt utilities provide the backbone for preflight prompts and middleware to operate safely.

## Deliverables
- **[schema]** `mcp/epistemic/schema.py` defining `EpistemicJustification` and related models with validators.
- **[store]** `mcp/epistemic/store.py` implementing `EpistemicStore` interface and `DiskStore` persistence.
- **[receipts]** `mcp/epistemic/receipts.py` generating structured receipt dictionaries.
- **[tests]** `tests/test_epistemic_store.py` verifying schema validation, disk round-trips, and receipt shape.

## Acceptance Criteria
- **[validation]** Schema enforces domain suffix `_justification` and optional fields behave per plan.
- **[persistence]** Disk store writes to `.epistemic/justifications/<risk>/<hash>.json` with metadata timestamp.
- **[observability]** Receipts include risk class, input hash, decision state, and justification reference.

## Notes
- Share helpers or fixtures with task 2001 for risk class imports.
- Ensure `.epistemic/` is gitignored or added to documentation as non-committed output.

---
task_id: "1009"
title: "Build operation validation checklist prompt"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - validation
depends_on:
  - "1001"
  - "1002"
  - "1004"
---

## Summary
Define `validate_operation_result()` in `src/prompts/validation.py` providing operation-specific post-processing checklists for reprojection, conversion, and analysis outputs.

## Rationale
Validation guardrails are central to user trust. A dedicated prompt aligns with `GLOBAL_INSTRUCTIONS` in `src/app.py` and ensures agents confirm correctness before declaring success.

## Deliverables
- **[prompt]** Validation prompt with branching guidance by operation type.
- **[tests]** Unit coverage ensuring critical checks (metadata, extent, nodata, statistics) are present.
- **[docs]** Documentation describing how and when to invoke validation prompts.

## Acceptance Criteria
- **[operation-mapping]** Prompt tailors checklist items to operation categories (reprojection, conversion, analysis).
- **[quality]** Emphasizes visual inspection, metadata review, and file existence.
- **[tests-pass]** Prompt suite updated with validation assertions.
- **[docs-updated]** Prompt documentation includes validation guidance section.

## Notes
- Coordinate with 1006 to ensure tests share helper assertions with other prompts.
- Validation language should complement receipts emitted under `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

---
task_id: "1006"
title: "Implement prompt unit testing harness"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - testing
  - prompts
depends_on:
  - "1001"
  - "1002"
  - "1003"
  - "1004"
  - "1005"
---

## Summary
Create `test/prompt_suite/test_prompts.py` validating content structure for all new prompts and establishing assertion helpers for future prompt coverage.

## Rationale
Prompt reliability requires automated regression. A dedicated harness lets us quantify guidance changes and supports CI pipelines as new prompts ship.

## Deliverables
- **[tests]** New pytest module covering each prompt’s critical guidance.
- **[helpers]** Utility functions for keyword/assertion reuse.
- **[docs]** Update testing documentation with instructions to run prompt suite.

## Acceptance Criteria
- **[coverage]** Each prompt task (1001-1005) has unit assertions verifying core instructions.
- **[automation]** Added to CI command in `pyproject.toml` or existing workflow steps.
- **[documentation]** README or CONTRIBUTING includes guidance on running prompt tests.
- **[tests-pass]** Entire test suite succeeds under `uv run pytest`.

## Notes
- Consider snapshot or transcript-based testing for future integration layers.
- Iterate alongside justification enforcement from `docs/design/epistemology/IMPLEMENTATION_PLAN.md` so prompts and guardrails remain in sync.

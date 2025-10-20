---
task_id: "1003"
title: "Develop data quality assessment prompt"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - quality
depends_on:
  - "1001"
---

## Summary
Create a `assess_data_quality()` prompt in `src/prompts/quality.py` that guides agents through verifying CRS, resolution, coverage, nodata handling, and compression artifacts before analysis.

## Rationale
Data quality verification is mandatory for reliable analytics. Prompt-driven assessments reduce downstream failures and align with the guardrails introduced in `src/app.py` global instructions.

## Deliverables
- **[prompt]** Function returning structured quality checklist guidance.
- **[tests]** Assertions ensuring all critical checks are mentioned.
- **[docs]** Documentation update describing the quality assessment workflow.

## Acceptance Criteria
- **[checklist]** Prompt enumerates CRS, resolution, nodata, coverage, and artifacts validation.
- **[recommendations]** Offers remediation suggestions for common quality failures.
- **[integration]** Tests exercise prompt from `test/prompt_suite/test_prompts.py`.
- **[docs-updated]** Prompt documentation reflects quality guidance.

## Notes
- Mention relevant resources such as `metadata://{file}/raster` and `reference://compression/guide` where applicable.
- Align checklist language with justification artifacts outlined in `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

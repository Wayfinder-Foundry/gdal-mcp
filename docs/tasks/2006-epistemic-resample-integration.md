---
task_id: "2006"
title: "Integrate epistemic enforcement with raster resampling tool"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-19"
updated: "2025-10-19"
tags:
  - epistemology
  - tools
  - raster
depends_on:
  - "2005"
---

## Summary
Extend the middleware integration to the raster resampling tool (e.g., `src/tools/raster/resample.py`), ensuring resampling choices trigger justification checks and receipts per section 10 step 3 of `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

## Rationale
Resampling introduces signal distortion risk. After validating reprojection, applying enforcement to resampling generalizes the pattern and surfaces new edge cases (e.g., up/down-sampling arguments).

## Deliverables
- **[integration]** Middleware calls around resampling execution, including risk classification and justification retrieval.
- **[receipts]** Logging or return payloads capturing decisions and residual uncertainty notes.
- **[tests]** Integration tests covering categorical and continuous datasets, ensuring justification changes per risk scenario.
- **[docs]** Update methodology links and usage examples to reference the new enforcement behavior.

## Acceptance Criteria
- **[policy]** Resampling refuses to run for high-risk contexts without justification; warns when stale.
- **[observability]** Receipts capture method choices and references to relevant methodology docs.
- **[regression]** Existing resampling tests continue to pass or are updated to include justification fixtures.

## Notes
- Coordinate with task 2007 to cover hydrology and aggregation tools next.
- Consider adding fixtures for categorical vs continuous data to test harness.

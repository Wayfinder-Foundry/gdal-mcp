---
task_id: "1004"
title: "Author format conversion strategy prompt"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - conversion
depends_on:
  - "1001"
---

## Summary
Implement `conversion_strategy()` in `src/prompts/conversion.py` to guide agents on selecting target formats, compression, tiling, and overview settings tailored to usage scenarios.

## Rationale
Format conversions are common yet nuanced. A dedicated prompt reduces guesswork and encodes best practices outlined in ADR-0023 references and `README.md` feature descriptions.

## Deliverables
- **[prompt]** New conversion guidance prompt with parameterization support.
- **[tests]** Automated checks confirming key guidance terms (format, compression, tiling).
- **[docs]** Prompt catalog entry describing format selection recommendations.

## Acceptance Criteria
- **[format-coverage]** Prompt addresses archival, analysis, and web delivery use cases.
- **[compression]** Mentions lossless vs lossy trade-offs referencing `reference://compression/guide`.
- **[overview]** Advises on tiling/overview usage for large rasters.
- **[tests-pass]** Unit tests pass under `uv run pytest`.

## Notes
- Align guidance with existing `raster_convert` options and future COG best practices.
- Reference `docs/design/epistemology/IMPLEMENTATION_PLAN.md` to ensure conversion choices dovetail with resampling and aggregation governance.

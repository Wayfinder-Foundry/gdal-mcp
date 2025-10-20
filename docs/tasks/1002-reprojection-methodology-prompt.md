---
task_id: "1002"
title: "Create reprojection decision methodology prompt"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - reprojection
depends_on:
  - "1001"
---

## Summary
Introduce `reprojection_methodology()` in `src/prompts/reprojection.py` to guide CRS selection, resampling decisions, and distortion awareness based on analysis goals and data characteristics.

## Rationale
Explicit prompt guidance ensures agents justify CRS changes and resampling methods, satisfying ADR-0011 (explicit resampling) and reducing misuse of `raster_reproject()`.

## Deliverables
- **[prompt]** New prompt function with contextual recommendations and resource references.
- **[tests]** Coverage ensuring guidance includes CRS and resampling decision factors.
- **[docs]** Prompt documentation entry highlighting usage scenarios.

## Acceptance Criteria
- **[crs-guidance]** Prompt differentiates between projected vs geographic CRS and mentions distortion implications.
- **[resampling]** Lists resampling guidance referencing `reference://resampling/guide`.
- **[validation]** Encourages post-reprojection quality checks (extent, resolution, metadata).
- **[tests-pass]** Unit tests succeed in `test/prompt_suite/test_prompts.py`.

## Notes
- Link to `reference://crs/common` once resource taxonomy Phase 2B files ship.
- Ensure prompt output can feed into justification workflows per `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

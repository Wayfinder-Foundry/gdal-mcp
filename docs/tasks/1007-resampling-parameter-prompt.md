---
task_id: "1007"
title: "Design resampling method selection prompt"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - parameters
depends_on:
  - "1002"
---

## Summary
Introduce `choose_resampling_method()` in `src/prompts/parameters.py` providing a decision framework based on data type, scale change, and analysis purpose.

## Rationale
Agents must justify resampling choices before calling `raster_reproject`. Encoding decision heuristics prevents misuse and reflects ADR-0011 requirements.

## Deliverables
- **[prompt]** Resampling decision prompt with branching logic and references.
- **[tests]** Assertions covering categorical vs continuous, upsampling vs downsampling guidance.
- **[docs]** Updated prompt documentation describing usage patterns.

## Acceptance Criteria
- **[decision-tree]** Prompt addresses data type, scale change, and output intent.
- **[references]** Mentions `reference://resampling/guide` for deeper context.
- **[validation]** Encourages verifying results post-resampling.
- **[tests-pass]** Prompt suite tests updated and passing.

## Notes
- Coordinate with 1002 to avoid duplicating reprojection guidance.
- Ensure decision logic harmonizes with resampling governance in `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

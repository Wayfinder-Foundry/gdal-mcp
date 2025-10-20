---
task_id: "1001"
title: "Implement terrain analysis methodology prompt"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - methodology
depends_on: []
---

## Summary
Design and implement a terrain analysis methodology prompt under `src/prompts/terrain.py` that guides agents through DEM quality checks, algorithm selection, preprocessing, execution planning, and validation per `docs/design/PROMPTING.md` guidance.

## Rationale
Terrain workflows are foundational for hydrology, risk, and planning analyses. Encoding expert methodology in prompts advances the Phase 2B objective captured in `PROMPT_IMPLEMENTATION_TASKS.md`.

## Deliverables
- **[prompt]** `terrain_analysis_methodology()` function with docstring and type hints.
- **[tests]** Unit test verifying key guidance terms and references.
- **[docs]** Entry in prompt library documentation describing usage.

## Acceptance Criteria
- **[guidance]** Prompt instructs agents to verify CRS, resolution, voids, and preprocessing steps.
- **[decision-tree]** Provides algorithm recommendations (e.g., Horn vs Evans-Young) with context.
- **[validation]** Includes explicit quality-check steps prior to reporting results.
- **[tests-pass]** New tests pass via `uv run pytest test/prompt_suite/test_prompts.py`.

## Notes
- Reference `metadata://{file}/raster` and `reference://terrain/parameters` resources once available.
- Coordinate guidance with `docs/design/epistemology/IMPLEMENTATION_PLAN.md` to ensure justifications align with CRS/resampling/hydrology policies.

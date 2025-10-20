---
task_id: "1005"
title: "Craft multi-criteria suitability analysis prompt"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - analysis
depends_on:
  - "1001"
---

## Summary
Add `suitability_analysis_methodology()` to `src/prompts/analysis.py` capturing data alignment, normalization, weighting, combination, and validation guidance for multi-criteria suitability workflows.

## Rationale
Complex suitability analyses are prime candidates for agentic planning. Prompt guidance enables consistent decision-making, fulfilling PROMPT_IMPLEMENTATION_TASKS.md Week 1 goals.

## Deliverables
- **[prompt]** Implementation with parameterized criteria and weights input.
- **[tests]** Unit tests validating presence of alignment, normalization, weighting, and validation instructions.
- **[docs]** Prompt library entry covering suitability use cases.

## Acceptance Criteria
- **[alignment]** Prompt instructs ensuring CRS/resolution/extent consistency across criteria.
- **[normalization]** Recommends normalization strategies and direction handling.
- **[validation]** Calls for sensitivity analysis and result verification.
- **[tests-pass]** Tests pass under `uv run pytest` suite.

## Notes
- Reference `reference://formats/raster` and `metadata://{file}/raster` resources when available.
- Ensure normalization/weighting guidance can surface justification data per `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

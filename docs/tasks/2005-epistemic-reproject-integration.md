---
task_id: "2005"
title: "Integrate epistemic enforcement with raster reprojection tool"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-19"
updated: "2025-10-19"
tags:
  - epistemology
  - tools
  - raster
depends_on:
  - "2004"
---

## Summary
Wrap the raster reprojection tool (e.g., `src/tools/raster/reproject.py`) with the new epistemic middleware, invoke the preflight prompt when required, and emit receipts as outlined in section 10 step 2 of `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

## Rationale
Starting with a single high-impact tool verifies end-to-end behavior before rolling out to other operations. Reprojection touches CRS/datum risk directly.

## Deliverables
- **[integration]** Middleware call added to the reprojection entry point with appropriate risk classification and just-in-time justification handling.
- **[receipts]** Tool returns or logs receipts, making decisions visible to users/agents.
- **[tests]** Integration tests simulating proceed, warn, and block flows using fixtures from tasks 2001-2004.
- **[docs]** Update tool docstrings and README/CHANGELOG to note epistemic enforcement.

## Acceptance Criteria
- **[runtime]** Reprojection refuses to run without justification when risk policy demands it.
- **[observability]** Receipts are surfaced through existing logging/context mechanisms.
- **[regression]** Existing functional tests continue to pass with middleware enabled.

## Notes
- Coordinate with task 2006 to reuse patterns for other tools.
- Capture sample receipts for documentation once behavior is stable.

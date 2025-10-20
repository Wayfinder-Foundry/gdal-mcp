---
task_id: "2007"
title: "Integrate epistemic enforcement with hydrology tooling"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-19"
updated: "2025-10-19"
tags:
  - epistemology
  - tools
  - hydrology
depends_on:
  - "2006"
---

## Summary
Apply the middleware and receipt framework to hydrology operations (flow direction, accumulation, sink filling) per section 10 step 3 of `docs/design/epistemology/IMPLEMENTATION_PLAN.md` and the methodology in `docs/design/epistemology/HYDROLOGY.md`.

## Rationale
Hydrology workflows are highly sensitive to epistemic risk. Ensuring these tools require justifications prevents silent topology failures and builds on lessons from reprojection/resampling integrations.

## Deliverables
- **[integration]** Middleware hooks across hydrology-related tool entry points with risk classification and justification enforcement.
- **[receipts]** Output that highlights hydrology-specific tradeoffs (preserve, restore, enforce) captured in justifications.
- **[tests]** Integration tests covering headwater, basin-scale, and artifact scenarios with proceed/warn/block behaviors.
- **[docs]** Update hydrology methodology doc with examples of receipts or enforcement messaging.

## Acceptance Criteria
- **[policy]** Hydrology tools require appropriate justifications before altering terrain surfaces.
- **[observability]** Receipts surface uncertainty sources and conditions for revisit drawn from justifications.
- **[regression]** Existing hydrology tests updated to accommodate middleware; new fixtures cover risk cases.

## Notes
- Coordinate with task 2008 for aggregation enforcement to maintain consistent patterns.
- Consider capturing sample justifications for documentation galleries.

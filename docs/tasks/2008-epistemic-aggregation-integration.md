---
task_id: "2008"
title: "Integrate epistemic enforcement with aggregation tooling"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-19"
updated: "2025-10-19"
tags:
  - epistemology
  - tools
  - aggregation
depends_on:
  - "2007"
---

## Summary
Extend enforcement to aggregation/zonal statistics tools, ensuring summary operations consult the aggregation methodology (`docs/design/epistemology/AGGREGATION.md`) and follow policy steps described in `docs/design/epistemology/IMPLEMENTATION_PLAN.md` section 10.

## Rationale
Aggregation choices can silently change interpretation. Enforcing justifications closes the loop across all risk classes and ensures receipts communicate interpretive tradeoffs.

## Deliverables
- **[integration]** Middleware hooks in aggregation/zonal tooling referencing risk classification and justification payloads.
- **[receipts]** Outputs capturing which distribution property was privileged (central tendency, dominant behavior, peak conditions).
- **[tests]** Scenarios covering different aggregation intents (mean, median, percentile) with proceed/warn/block outcomes.
- **[docs]** Update aggregation methodology doc with enforcement notes and sample receipts.

## Acceptance Criteria
- **[policy]** Aggregation operations require justifications aligned with their interpretive goal.
- **[observability]** Receipts highlight tradeoffs and conditions for revisit drawn from justifications.
- **[regression]** Existing aggregation tests updated to include justification fixtures and enforcement paths.

## Notes
- Consider cross-linking with prompt tasks that generate aggregation plans (e.g., 1005) to reuse justification language.
- Final step before expanding risk classes to additional domains if needed.

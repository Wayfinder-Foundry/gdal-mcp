---
status: proposed
date: 2025-10-19
decision-makers: [jgodau]
tags: [epistemology, governance, prompts, fastmcp]
---

# ADR-0026: Epistemic Governance for Geospatial Methodology

## Context

Phase 2B planning introduced an epistemology program (`docs/design/epistemology/`) that
defines how the MCP reasons about high-risk geospatial operations. The prompt roadmap now
depends on:

- A reusable justification schema (`JUSTIFICATION_SCHEMA.md`) for documenting scientific
  reasoning.
- Domain methodology guides for CRS, resampling, hydrology, and aggregation decisions.
- An implementation plan describing preflight prompts, middleware gates, receipts, and
  storage for justification artifacts (`IMPLEMENTATION_PLAN.md`).
- Task cards and prompts that must align with these guardrails (`docs/tasks/1001-1011-*.md`,
  `docs/tasks/1020-transactional-workflow-adr.md`).

We need a formal decision to anchor these philosophies, clarify their permanence, and guide
future contributors as tooling evolves beyond documentation.

## Decision

1. **Adopt epistemic justification as a first-class requirement** for high-impact raster and
   vector operations. All tooling and prompts touching CRS/datum, resampling, hydrology, or
   aggregation must surface or consume an `epistemic_justification` object.
2. **Standardize risk detection** on the four classes enumerated in
   `docs/design/epistemology/RISK_CLASSES.md`, using the hashing and routing strategy captured
   in `IMPLEMENTATION_PLAN.md` when code implementation proceeds.
3. **Treat methodology documents as canonical references** for prompt authors, ADR writers,
   and future agents. Any new domain guidance extends the epistemology directory using the
   shared schema rather than ad-hoc prose.
4. **Log every escalated operation with machine-readable receipts** once enforcement lands,
   enabling observability, education, and potential rollback/approval workflows.
5. **Align prompt and ADR planning artifacts** with the epistemology suite. Existing task
   cards (`1001-1011`, `1020`) already reference the plan; new work items must do the same to
   ensure governance continuity.

## Consequences

- **Positive**: Encourages reproducible scientific reasoning, improves user trust, and
  prevents silent failure modes (projection drift, over-smoothing, hydrology artifacts,
  misinterpreted aggregation).
- **Positive**: Creates a clear integration path for future enforcement modules (risk
  classifiers, middleware, receipts, persistence) without blocking current documentation work.
- **Positive**: Codifies how prompts and tooling interact, reducing ambiguity for new
  contributors.
- **Negative**: Adds documentation overhead and requires ongoing discipline when expanding the
  risk taxonomy or methodology set.
- **Neutral**: Implementation effort is staged; until middleware and prompts are updated, the
  epistemology suite functions as guidance rather than enforcement.

## Status

Proposed — documentation complete; engineering tasks to implement enforcement will follow the
steps in `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

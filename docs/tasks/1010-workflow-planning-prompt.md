---
task_id: "1010"
title: "Implement workflow planning prompt"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - workflow
depends_on:
  - "1001"
  - "1002"
  - "1003"
  - "1004"
  - "1005"
---

## Summary
Add `plan_geospatial_workflow()` to `src/prompts/workflow.py` that decomposes user goals into ordered steps, highlights data dependencies, and flags validation checkpoints before execution.

## Rationale
Planning prompts support the proposed transaction-based approval loop and Phase 3 workflow intelligence objectives. They give users visibility before long-running pipelines execute.

## Deliverables
- **[prompt]** Workflow planning prompt with rationale output and approval guidance.
- **[tests]** Assertions ensuring plan includes steps, dependencies, and validation notes.
- **[docs]** Documentation entry describing the planning/approval flow.

## Acceptance Criteria
- **[stepwise]** Prompt outputs numbered steps with explanations and prerequisite data.
- **[approval]** Explicitly asks users to confirm the plan before execution.
- **[tests-pass]** Prompt suite expanded and passing.
- **[docs-updated]** Documentation references transaction-style review concept.

## Notes
- Coordinate with pending ADR 1020 on transactional workflow approval.

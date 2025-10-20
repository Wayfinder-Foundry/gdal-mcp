---
task_id: "1020"
title: "Draft ADR for transactional workflow approval"
status: "todo"
priority: "high"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - adr
  - workflow
depends_on:
  - "1010"
---

## Summary
Document a proposal ADR describing transaction-style approval for multi-step workflows, where the MCP presents planned pipelines with rationale and waits for user confirmation before execution.

## Rationale
Users need agency over long-running pipelines. An ADR captures design trade-offs and aligns prompt and middleware changes with the collaborative philosophy noted in `PROMPT_IMPLEMENTATION_TASKS.md` and the global instructions in `src/app.py`.

## Deliverables
- **[adr-draft]** `docs/ADR/00XX-transactional-workflow-approval.md` capturing context, decision, and consequences.
- **[references]** Links to relevant prompts (1010) and tooling policies.
- **[open-questions]** Section outlining rollback semantics, partial execution handling, and UI signals.

## Acceptance Criteria
- **[structure]** ADR follows existing format with status=pending and clear rationale.
- **[alignment]** Decision statement ties to user trust and collaborative iteration goals.
- **[next-steps]** Identifies experiments/prototypes needed before acceptance.

## Notes
- Coordinate ADR numbering with maintainer before finalizing filename.

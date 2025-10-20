---
task_id: "1011"
title: "Update prompt documentation catalog"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - documentation
  - prompts
depends_on:
  - "1001"
  - "1002"
  - "1003"
  - "1004"
  - "1005"
  - "1007"
  - "1008"
  - "1009"
  - "1010"
---

## Summary
Revise `docs/fastmcp/PROMPTS.md` (or new `docs/fastmcp/PROMPT_LIBRARY.md`) to catalog all prompts, document usage patterns, and include examples referencing the new prompt modules.

## Rationale
Clear documentation ensures discoverability for both developers and AI agents. Updating the catalog maintains alignment with the expanded prompt suite.

## Deliverables
- **[doc-update]** Prompt documentation covering new modules and grouping by category.
- **[examples]** Usage snippets referencing resources and validation flow.
- **[index]** Links from README or ROADMAP to the updated prompt catalog.

## Acceptance Criteria
- **[coverage]** Every prompt from tasks 1001-1010 documented with purpose, parameters, and example usage.
- **[navigation]** README or roadmap links highlight the prompt catalog location.
- **[consistency]** Terminology aligns with guardrails and global instructions in `src/app.py`.

## Notes
- Consider split documentation for methodology vs parameter vs validation prompts if the catalog grows large.

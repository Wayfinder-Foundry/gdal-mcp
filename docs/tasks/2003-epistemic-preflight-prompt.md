---
task_id: "2003"
title: "Implement epistemic preflight prompt and model interface"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-19"
updated: "2025-10-19"
tags:
  - epistemology
  - prompts
  - middleware
depends_on:
  - "2001"
  - "2002"
---

## Summary
Develop the helper that builds the epistemic preflight prompt, invoke the LLM client to obtain `epistemic_justification` payloads, and parse responses as described in section 6 of `docs/design/epistemology/IMPLEMENTATION_PLAN.md`.

## Rationale
The preflight prompt is the bridge between risk detection and justification generation. It ensures escalations produce schema-compliant objects before tool execution.

## Deliverables
- **[helper]** `mcp/epistemic/preflight.py` containing `EP_PREPROMPT` template and `build_preflight_prompt()`.
- **[client integration]** Utility or adapter for calling the LLM (can be synchronous placeholder) returning JSON for tests.
- **[tests]** `tests/test_epistemic_preflight.py` verifying prompt formatting, JSON parsing, and error handling on malformed responses.
- **[docs]** Update `docs/design/epistemology/IMPLEMENTATION_PLAN.md` checklist for section 6.

## Acceptance Criteria
- **[formatting]** Prompt includes tool name, arguments, and risk class guidance verbatim from the plan.
- **[parsing]** Response handler validates `needs_escalation`, `risk_class`, and `justification` fields before returning.
- **[test-mocks]** Tests simulate both escalation and pass-through cases without hitting real networks.

## Notes
- Coordinate with future middleware task (2004) to reuse the response parser.
- Keep the prompt template easy to update as methodology grows.

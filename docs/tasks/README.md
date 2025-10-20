# Task Card Schema

Each task card lives under `docs/tasks/` as `####-slug.md`.

```yaml
---
task_id: "####"
title: "Concise, action-oriented heading"
status: "todo" # allowed: todo, in_progress, blocked, done
priority: "medium" # allowed: low, medium, high, critical
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - category-one
  - category-two
depends_on: [] # list of task_ids
---
```

## Body Sections

- `## Summary`
  - Brief description of the task’s intent.
- `## Rationale`
  - Why the task matters (link to docs/ADRs if relevant).
- `## Deliverables`
  - Bullet list of concrete outputs.
- `## Acceptance Criteria`
  - Bullet list of measurable checks required for completion.
- `## Notes`
  - Optional references, blocking issues, or follow-ups.

Stick to Markdown bullet lists using `- **[label]** description`.
Update `status` and timestamps as progress changes.

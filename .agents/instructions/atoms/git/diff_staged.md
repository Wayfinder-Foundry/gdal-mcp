
---
description: Show diff of staged changes (read-only).
---

```yaml
name: git_diff_staged_atom
description: |
  Staged diff. Use to confirm index contents prior to commit.

inputs:
  repo_path: { type: string, required: false, default: "{{ context.project.root_path }}" }
  context_lines: { type: number, required: false, default: 3 }

steps:
  - id: diff
    action: git_op
    tool: git_diff_staged
    params:
      repo_path: "{{ inputs.repo_path }}"
      context_lines: "{{ inputs.context_lines }}"

outputs:
  success:
    status: ok
    repo_path: "{{ inputs.repo_path }}"
    diff_text: "{{ steps.diff.output or '' }}"
```

---
description: Show diff of unstaged changes (read-only).
---

```yaml
name: git_diff_unstaged_atom
description: |
  Unstaged diff. Use for quick local-change inspection before staging.

inputs:
  repo_path: { type: string, required: false, default: "{{ context.project.root_path }}" }
  context_lines: { type: number, required: false, default: 3 }

steps:
  - id: diff
    action: git_op
    tool: git_diff_unstaged
    params:
      repo_path: "{{ inputs.repo_path }}"
      context_lines: "{{ inputs.context_lines }}"

outputs:
  success:
    status: ok
    repo_path: "{{ inputs.repo_path }}"
    diff_text: "{{ steps.diff.output or '' }}"
```
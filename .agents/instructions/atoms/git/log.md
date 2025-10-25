---
description: Show recent commits (read-only).
---

```yaml
name: git_log_atom
description: |
  Recent commit log window with hash, author, date, message.

inputs:
  repo_path:   { type: string, required: false, default: "{{ context.project.root_path }}" }
  max_count:   { type: number, required: false, default: 10 }

steps:
  - id: log
    action: git_op
    tool: git_log
    params:
      repo_path: "{{ inputs.repo_path }}"
      max_count: "{{ inputs.max_count }}"

outputs:
  success:
    status: ok
    repo_path: "{{ inputs.repo_path }}"
    commits: "{{ steps.log.output or [] }}"
```
---
description: Unstage all staged changes (guarded by auto_confirm).
---

```yaml
name: git_reset_atom
description: |
  Unstage any files currently in the index. Guarded by auto_confirm.

inputs:
  repo_path: { type: string, required: false, default: "{{ context.project.root_path }}" }
  auto_confirm: { type: boolean, required: false, default: false }

steps:
  - id: preview
    action: system
    output: |
      [GIT_RESET_PREVIEW]
      repo: {{ inputs.repo_path }}

  - id: confirm
    when: "{{ not inputs.auto_confirm }}"
    action: user
    description: "Unstage all staged changes?"

  - id: reset
    when: "{{ inputs.auto_confirm or confirm.approved }}"
    action: git_op
    tool: git_reset
    params:
      repo_path: "{{ inputs.repo_path }}"

outputs:
  success:
    status: ok
    message: "Index reset (unstaged)."
```
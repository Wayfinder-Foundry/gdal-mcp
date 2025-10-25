---
description: Stage specific files (guarded by auto_confirm).
---

```yaml
name: git_stage_atom
description: |
  Stage a provided list of files into the index. No wildcards. Guarded by auto_confirm.

inputs:
  repo_path: { type: string, required: false, default: "{{ context.project.root_path }}" }
  files:     { type: array,  required: true,  description: "Explicit file paths relative to repo root" }
  auto_confirm: { type: boolean, required: false, default: false }

steps:
  - id: preview
    action: system
    output: |
      [GIT_STAGE_PREVIEW]
      repo: {{ inputs.repo_path }}
      files: {{ inputs.files | join(', ') }}

  - id: confirm
    when: "{{ not inputs.auto_confirm }}"
    action: user
    description: "Stage these files?"

  - id: stage
    when: "{{ inputs.auto_confirm or confirm.approved }}"
    action: git_op
    tool: git_add
    params:
      repo_path: "{{ inputs.repo_path }}"
      files: "{{ inputs.files }}"

outputs:
  success:
    status: ok
    staged: "{{ inputs.files }}"
```
---
description: Create a commit (explicitly guarded; off by default).
---

```yaml
name: git_commit_atom
description: |
  Create a commit with a provided message.
  Strict guardrails: requires allow_dangerous=true and auto_confirm.

inputs:
  repo_path:     { type: string, required: false, default: "{{ context.project.root_path }}" }
  message:       { type: string, required: true }
  allow_dangerous: { type: boolean, required: false, default: false }
  auto_confirm:  { type: boolean, required: false, default: false }

steps:
  - id: policy_check
    action: assert
    with:
      condition: "{{ inputs.allow_dangerous == true }}"
      message: "Commit blocked by policy (require allow_dangerous=true)."

  - id: staged_preview
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/diff_staged.md
    with:
      repo_path: "{{ inputs.repo_path }}"
      context_lines: 1

  - id: preview
    action: system
    output: |
      [GIT_COMMIT_PREVIEW]
      repo: {{ inputs.repo_path }}
      message: {{ inputs.message }}
      staged_diff_preview:
      {{ steps.staged_preview.diff_text or '(no staged changes)' }}

  - id: confirm
    when: "{{ not inputs.auto_confirm }}"
    action: user
    description: "Create commit with the above message and currently staged changes?"

  - id: commit
    when: "{{ inputs.auto_confirm or confirm.approved }}"
    action: git_op
    tool: git_commit
    params:
      repo_path: "{{ inputs.repo_path }}"
      message: "{{ inputs.message }}"

outputs:
  success:
    status: ok
    repo_path: "{{ inputs.repo_path }}"
    commit: "{{ steps.commit.output or null }}"
```
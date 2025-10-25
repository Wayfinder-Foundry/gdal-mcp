---
description: Read-only “grounding” snapshot (status + diffs + recent commits).
---

```yaml
name: git_sweep_atom
description: |
  Lightweight, read-only snapshot to ground an agent's run:
  - status
  - unstaged diff (short)
  - staged diff (short)
  - recent commits (short)

inputs:
  repo_path:     { type: string, required: false, default: "{{ context.project.root_path }}" }
  max_commits:   { type: number, required: false, default: 8 }
  context_lines: { type: number, required: false, default: 2 }

steps:
  - id: status
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/status.md
    with:
      repo_path: "{{ inputs.repo_path }}"

  - id: unstaged
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/diff_unstaged.md
    with:
      repo_path: "{{ inputs.repo_path }}"
      context_lines: "{{ inputs.context_lines }}"

  - id: staged
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/diff_staged.md
    with:
      repo_path: "{{ inputs.repo_path }}"
      context_lines: "{{ inputs.context_lines }}"

  - id: log
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/log.md
    with:
      repo_path: "{{ inputs.repo_path }}"
      max_count: "{{ inputs.max_commits }}"

  - id: summarize
    action: system
    output_transform:
      snapshot:
        repo_path: "{{ inputs.repo_path }}"
        has_changes: "{{ steps.status.summary.has_changes }}"
        recent_commits: "{{ steps.log.commits or [] }}"
        unstaged_preview: "{{ (steps.unstaged.diff_text or '')[:2000] }}"
        staged_preview:   "{{ (steps.staged.diff_text   or '')[:2000] }}"

outputs:
  success:
    status: ok
    snapshot: "{{ steps.summarize.snapshot }}"
```
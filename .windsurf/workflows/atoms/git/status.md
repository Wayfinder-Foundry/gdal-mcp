---
description: Show working tree status (read-only).
---
```yaml
name: git_status_atom
description: |
  Read-only status of working directory (modified, added, deleted, untracked).
  Returns raw text plus a simple presence summary.

inputs:
  repo_path:
    type: string
    required: false
    default: "{{ context.project.root_path }}"

steps:
  - id: status
    action: git_op
    tool: git_status
    params:
      repo_path: "{{ inputs.repo_path }}"

  - id: summarize
    action: system
    output_transform:
      summary:
        has_changes: "{{ steps.status.output and (steps.status.output | length > 0) }}"
        # Provide raw text; parsing is tool/version dependent. Keep it simple & portable.
        status_text: "{{ steps.status.output or '' }}"

outputs:
  success:
    status: ok
    repo_path: "{{ inputs.repo_path }}"
    summary: "{{ steps.summarize.summary }}"
```
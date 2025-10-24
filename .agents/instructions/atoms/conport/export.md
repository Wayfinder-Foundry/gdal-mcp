---
description: Export ConPort state to Markdown for backup or sharing.
---

```yaml
name: export_conport_atom
description: |
  Export ConPort state to Markdown for backup or sharing.
  - Uses `export_conport_to_markdown` with the current workspace_id
  - Supports explicit `output_path` or defaults to <workspace>/context_portal/export.md
  - Always confirms the destination path to the user

inputs:
  output_path:
    type: string
    required: false
    description: "Where to save the export (default: <workspace>/context_portal/export.md)"

steps:
  - id: resolve_paths
    action: system
    output_transform:
      portal_dir: "{{ context.workspace_id }}/context_portal"
      default_export: "{{ context.workspace_id }}/context_portal/export.md"

  - id: run_export
    action: conport_op
    tool: export_conport_to_markdown
    params:
      workspace_id: "{{ context.workspace_id }}"
      output_path: "{{ inputs.output_path or steps.resolve_paths.default_export }}"

  - id: confirm
    action: system
    output: >-
      [CONPORT_EXPORT] ConPort state exported to
      {{ inputs.output_path or steps.resolve_paths.default_export }}

outputs:
  success:
    status: ok
    message: "{{ steps.confirm.output }}"
    path: "{{ inputs.output_path or steps.resolve_paths.default_export }}"
```
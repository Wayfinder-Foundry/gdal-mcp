---
description: Identify styles and patterns and log as Custom StyleImprint
---

```yaml
---
description: Identify repository style/patterns and log as ConPort Custom Data (StyleImprint → repo-wide). Hooked with pre/post.
---

name: imprint
description: |
  Extract a style/pattern “imprint” for the repository and persist it as ConPort Custom Data.
  Wrap with preflight/postflight for consistent grounding and logging.

inputs:
  pre_opts:  { type: object, required: false, default: {} }
  post_opts:
    type: object
    required: false
    default: { capture_git_snapshot: true, log_run_record: true, export_on_change: false }

steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"

  # ---------- Extract style imprint ----------
  - id: extract
    action: coding_op
    tool: extract_style_imprint
    params:
      repo_root: "{{ context.project.root_path }}"

  # ---------- Log as Custom Data (StyleImprint / repo-wide) ----------
  - id: log_imprint
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/log.md
    with:
      custom:
        category: "StyleImprint"
        key: "repo-wide"
        value: "{{ steps.extract.imprint | tojson }}"
      auto_confirm: true

  # ---------- Prepare progress payload for postflight ----------
  - id: progress_payload
    action: system
    output_transform:
      progress:
        - description: >-
            Style imprint updated (category=StyleImprint, key=repo-wide).
            {{ steps.log_imprint.custom_key and 'upserted key=' ~ steps.log_imprint.custom_key or '' }}
          status: "DONE"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.progress_payload.progress }}"
      active_patch:
        current_focus: "Style imprint"
        workflow: "imprint"
        last_run: "{{ now_iso() }}"
      {{ inputs.post_opts | tojson }}

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: "Style imprint logged."
    custom_key: "{{ steps.log_imprint.custom_key or 'repo-wide' }}"
```
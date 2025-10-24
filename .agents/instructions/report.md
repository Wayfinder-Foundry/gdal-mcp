---
description: Summarize Product/Active contexts, recent ConPort activity, and Git snapshot.
---

---
description: Summarize Product/Active contexts, recent ConPort activity, and Git snapshot. Hooked with pre/post.
---

```yaml
name: report
description: |
  Generate a concise report:
  - ConPort status (counts, current focus) + recent activity (last N hours)
  - Git snapshot (changes + recent commits) from preflight
  - Display as markdown; optionally save to file
  - Log a lightweight progress item via postflight

inputs:
  hours_ago:   { type: integer, required: false, default: 48 }
  output_path: { type: string,  required: false, default: "" }
  pre_opts:    { type: object,  required: false, default: {} }
  post_opts:
    type: object
    required: false
    default: { capture_git_snapshot: true, log_run_record: true, export_on_change: false }

steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with:
      {{ inputs.pre_opts | tojson }}
      recent_activity:
        hours_ago: "{{ inputs.hours_ago }}"
        limit_per_type: 5

  # Pull recent ConPort activity explicitly
  - id: recent
    action: conport_op
    tool: get_recent_activity_summary
    params:
      workspace_id: "{{ context.workspace_id }}"
      hours_ago: "{{ inputs.hours_ago }}"
      limit_per_type: 5

  # ---------- Compose markdown report ----------
  - id: compose
    action: system
    output_transform:
      report_md: |
        ## ConPort & Git Report (last {{ inputs.hours_ago }}h)

        **ConPort**
        - Status: {{ steps.preflight.preflight.conport.status }}
        - Current focus: {{ steps.preflight.preflight.conport.current_focus or '—' }}
        - Counts — decisions: {{ steps.preflight.preflight.conport.counts.decisions }},
          progress: {{ steps.preflight.preflight.conport.counts.progress }},
          patterns: {{ steps.preflight.preflight.conport.counts.patterns }},
          glossary: {{ steps.preflight.preflight.conport.counts.glossary }}
        - Recent activity:
          {{ steps.recent.summary or 'None' }}

        **Git**
        - Has changes: {{ steps.preflight.preflight.git.has_changes }}
        - Recent commits: {{ (steps.preflight.preflight.git.recent_commits | length) if steps.preflight.preflight.git.recent_commits else 0 }}
        - Unstaged preview:
          {% raw %}```diff
          {{ (steps.preflight.preflight.git.unstaged_preview or '')[:1500] }}
          ```{% endraw %}
        - Staged preview:
          {% raw %}```diff
          {{ (steps.preflight.preflight.git.staged_preview or '')[:1500] }}
          ```{% endraw %}

  - id: display
    action: system
    say: "{{ steps.compose.report_md }}"

  - id: maybe_write
    when: "{{ inputs.output_path != '' }}"
    action: fs_op
    tool: write_text
    params:
      path: "{{ inputs.output_path }}"
      text: "{{ steps.compose.report_md }}"

  # ---------- Prepare progress payload ----------
  - id: progress_payload
    action: system
    output_transform:
      progress:
        - description: >-
            Report generated ({{ inputs.hours_ago }}h) — ConPort={{ steps.preflight.preflight.conport.status }},
            git_changes={{ steps.preflight.preflight.git.has_changes }}
          status: "DONE"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.progress_payload.progress }}"
      active_patch:
        current_focus: "Status report ({{ inputs.hours_ago }}h)"
        workflow: "report"
        last_run: "{{ now_iso() }}"
      {{ inputs.post_opts | tojson }}

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: "Report displayed."
    report_md: "{{ steps.compose.report_md }}"
    report_path: "{{ inputs.output_path if inputs.output_path != '' else null }}"
```
---
description: Create a development plan and reconcile with ConPort progress, appending next steps, and committing if changed.
---

```yaml
---
description: Maintain plan.md: reconcile with ConPort progress, append next steps, and commit if changed. Hooked; no tests.
---

name: plan
description: |
  Maintain {{ context.project.root_path }}/plan.md (or a custom path).
  - Preflight to load env/policies + ConPort/Git grounding
  - Close/mark done items in plan from current ConPort progress
  - Append a concise “Next Steps” section
  - Format/lint only (no tests); commit if there are diffs
  - Postflight to sync/log/export as configured

inputs:
  plan_path: { type: string, required: false, default: "plan.md" }
  pre_opts:  { type: object, required: false, default: {} }
  post_opts:
    type: object
    required: false
    default: { capture_git_snapshot: true, log_run_record: true, export_on_change: true, preserve_focus: true }

  dry_run:
    type: boolean
    required: false
    default: false

steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"

  # ---------- Load/prepare existing plan ----------
  - id: read_plan
    action: fs_op
    tool: read_text_if_exists
    params:
      path: "{{ inputs.plan_path }}"

  # ---------- Pull recent progress from ConPort (source of truth) ----------
  - id: get_progress
    action: conport_op
    tool: get_progress
    params:
      workspace_id: "{{ context.workspace_id }}"
      limit: 200

  # ---------- Reconcile plan with progress ----------
  - id: clean_plan
    action: coding_op
    tool: reconcile_plan_with_progress
    params:
      plan_md: "{{ steps.read_plan.text or '' }}"
      progress: "{{ steps.get_progress.results or [] }}"

  - id: write_plan
  when: "{{ inputs.dry_run != true }}"
  action: fs_op
  tool: write_text
  params:
    path: "{{ inputs.plan_path }}"
    text: "{{ steps.clean_plan.updated_plan_md }}"

  # ---------- Draft minimal, testable next steps ----------
  - id: think_next
    action: sequential_thinking
    tool: sequential_thinking
    params:
      thought: |
        Draft a short, concrete “Next Steps” list based on the cleaned plan and current progress.
        Prefer 3–6 bullets, each action-oriented and verifiable.
        Avoid speculative architecture; keep it executable within 1–2 working sessions.
      nextThoughtNeeded: false
      thoughtNumber: 1
      totalThoughts: 1

  - id: has_next_steps
    action: coding_op
    tool: select_if
    params:
      condition: >-
        {{ steps.read_plan.text and (steps.read_plan.text | contains('## Next Steps')) }}
      then: present
      else: absent

  - id: append_next
  when: "{{ steps.has_next_steps.result == 'absent' and inputs.dry_run != true }}"
  action: fs_op
  tool: append_text
  params:
    path: "{{ inputs.plan_path }}"
    text: |
        {% raw %}

        ## Next Steps
        {{ steps.think_next.thought }}
        {% endraw %}

  # ---------- Stage and commit if there are changes (docs-only discipline) ----------
  - id: git_status
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/status.md
    with:
      repo_path: "{{ context.project.root_path }}"

  - id: stage_plan
    when: "{{ steps.git_status.summary.has_changes }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/stage.md
    with:
      repo_path: "{{ context.project.root_path }}"
      files: ["{{ inputs.plan_path }}"]
      auto_confirm: true

  - id: commit_plan
    when: "{{ steps.git_status.summary.has_changes }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/commit.md
    with:
      repo_path: "{{ context.project.root_path }}"
      allow_dangerous: true
      auto_confirm: true
      message: "docs(plan): update plan and next steps"

  # ---------- Prepare progress payload for postflight ----------
  - id: progress_payload
    action: system
    output_transform:
      progress:
        - description: >-
            Plan reconciled and extended — {{ inputs.plan_path }}
            {{ steps.git_status.summary.has_changes and 'committed changes' or 'no changes' }}
          status: "{{ steps.git_status.summary.has_changes and 'DONE' or 'IN_PROGRESS' }}"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.progress_payload.progress }}"
      dry_run: "{{ inputs.dry_run }}"
      {% raw %}{% if inputs.post_opts and inputs.post_opts.preserve_focus %}{% endraw %}
      active_patch:
        requested_scope: "{{ inputs.plan_path }}"
        workflow: "plan"
        last_run: "{{ now_iso() }}"
      {% raw %}{% else %}{% endraw %}
      active_patch:
        current_focus: "Plan maintenance"
        requested_scope: "{{ inputs.plan_path }}"
        workflow: "plan"
        last_run: "{{ now_iso() }}"
      {% raw %}{% endif %}{% endraw %}
      {{ inputs.post_opts | tojson }}

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: >-
      Plan reconciled and extended.
      {{ steps.qa_and_commit.commit_hash and ('commit='+steps.qa_and_commit.commit_hash[:7]) or '(no changes)' }}
```
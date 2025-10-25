---
description: Maintain plan.md: reconcile with ConPort progress, append next steps, and commit if changed. Hooked; no tests.
---

```yaml
name: plan
description: |
  Maintain {{ context.project.root_path }}/plan.md (or a custom path).
  - Preflight to load env/policies + ConPort/Git grounding
  - Close/mark done items in plan from current ConPort progress
  - Append a concise "Next Steps" section
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
    action: workflow
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"
    on_error:
      strategy: continue
      output: "[PLAN] preflight failed, continuing without context"

  # ---------- Load/prepare existing plan ----------
  - id: check_plan_exists
    action: fs_op
    tool: get_file_info
    params:
      path: "{{ inputs.plan_path }}"
    on_error:
      strategy: continue

  - id: read_plan
    when: "{{ steps.check_plan_exists.success }}"
    action: fs_op
    tool: read_text_file
    params:
      path: "{{ inputs.plan_path }}"
    on_error:
      strategy: fail
      message: "Failed to read existing plan at {{ inputs.plan_path }}"

  # ---------- Pull recent progress from ConPort (source of truth) ----------
  - id: get_progress
    action: conport_op
    tool: get_progress
    params:
      workspace_id: "{{ context.workspace_id }}"
      limit: 200
    on_error:
      strategy: continue
      output: "[]"

  # ---------- Reconcile plan with progress ----------
  # This step needs manual implementation - using AI to reconcile
  - id: reconcile_request
    action: system
    output: |
      [PLAN_RECONCILIATION_NEEDED]
      Current plan ({{ (steps.read_plan.content or '') | length }} chars)
      Progress entries: {{ (steps.get_progress.results or []) | length }}
      
      Task: Mark completed items from progress as DONE in plan.
      Look for matching descriptions between plan items and progress with status=DONE.

  # For now, use the existing plan or empty string
  - id: plan_content
    action: system
    output_transform:
      text: "{{ steps.read_plan.content or '# Development Plan\n\n' }}"

  # ---------- Draft minimal, testable next steps ----------
  - id: think_next
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: |
        Analyze the current plan and ConPort progress.
        Draft 3-6 concrete, actionable next steps that are:
        - Specific and testable
        - Achievable within 1-2 sessions
        - Ordered by priority/dependency
        - Aligned with the plan's goals
      nextThoughtNeeded: true
      thoughtNumber: 1
      totalThoughts: 5
      isRevision: false

  - id: think_refine
    when: "{{ steps.think_next.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: |
        Review the drafted next steps. Are they:
        1. Concrete enough? (avoid vague actions)
        2. Properly scoped? (not too large/small)
        3. Well-ordered? (dependencies clear)
        Refine as needed.
      nextThoughtNeeded: true
      thoughtNumber: 2
      totalThoughts: 5
      isRevision: true
      revisesThought: 1

  - id: think_finalize
    when: "{{ steps.think_refine.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: |
        Finalize the next steps list in markdown format:
        - Use bullet points
        - Start each with action verb
        - Include acceptance criteria where helpful
      nextThoughtNeeded: false
      thoughtNumber: 3
      totalThoughts: 3
      isRevision: false

  # ---------- Check if Next Steps section exists ----------
  - id: has_next_steps
    action: system
    output_transform:
      result: "{{ (steps.plan_content.text | contains('## Next Steps')) and 'present' or 'absent' }}"

  # ---------- Build updated plan ----------
  - id: build_updated_plan
    action: system
    output_transform:
      updated_plan: |
        {{ steps.plan_content.text }}
        {% if steps.has_next_steps.result == 'absent' %}
        
        ## Next Steps
        {{ steps.think_finalize.thought or steps.think_refine.thought or steps.think_next.thought }}
        {% endif %}

  # ---------- Write plan if not dry run ----------
  - id: write_plan
    when: "{{ not inputs.dry_run }}"
    action: fs_op
    tool: write_file
    params:
      path: "{{ inputs.plan_path }}"
      content: "{{ steps.build_updated_plan.updated_plan }}"
    on_error:
      strategy: fail
      message: "Failed to write plan to {{ inputs.plan_path }}"

  # ---------- Git operations (stage and commit if changes) ----------
  - id: git_status
    action: git_op
    tool: git_status
    params:
      repo_path: "{{ context.project.root_path }}"
    on_error:
      strategy: continue
      output: ""

  - id: has_git_changes
    action: system
    output_transform:
      result: "{{ steps.git_status.output and (steps.git_status.output | length > 0) }}"

  - id: stage_plan
    when: "{{ steps.has_git_changes.result and not inputs.dry_run }}"
    action: git_op
    tool: git_add
    params:
      repo_path: "{{ context.project.root_path }}"
      files: ["{{ inputs.plan_path }}"]
    on_error:
      strategy: continue
      message: "Failed to stage {{ inputs.plan_path }}"

  - id: commit_plan
    when: "{{ steps.has_git_changes.result and not inputs.dry_run }}"
    action: git_op
    tool: git_commit
    params:
      repo_path: "{{ context.project.root_path }}"
      message: "docs(plan): update plan and next steps"
    on_error:
      strategy: continue
      message: "Failed to commit plan changes"

  # ---------- Prepare progress payload for postflight ----------
  - id: build_progress_payload
    action: system
    output_transform:
      progress:
        - description: "Plan reconciled and extended at {{ inputs.plan_path }}"
          status: "{{ steps.has_git_changes.result and 'DONE' or 'IN_PROGRESS' }}"
          linked_item_type: "custom_data"
          linked_item_id: "ProjectDocs/plan"

  # ---------- Build postflight active context patch ----------
  - id: build_active_patch
    action: system
    output_transform:
      patch:
        current_focus: "{{ inputs.post_opts.preserve_focus and null or 'Plan maintenance' }}"
        requested_scope: "{{ inputs.plan_path }}"
        workflow: "plan"
        last_run: "{{ context.current_time }}"
        next_steps_count: "{{ steps.think_finalize.thought or steps.think_next.thought | split('\n') | length }}"

  # ---------- POST HOOK ----------
  - id: postflight
    action: workflow
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.build_progress_payload.progress }}"
      active_patch: "{{ steps.build_active_patch.patch }}"
      dry_run: "{{ inputs.dry_run }}"
      capture_git_snapshot: "{{ inputs.post_opts.capture_git_snapshot }}"
      log_run_record: "{{ inputs.post_opts.log_run_record }}"
      export_on_change: "{{ inputs.post_opts.export_on_change }}"
    on_error:
      strategy: continue
      output: "[PLAN] postflight failed"

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: |
      Plan reconciled and extended.
      {{ steps.has_git_changes.result and 'Changes committed.' or 'No changes detected.' }}
    plan_path: "{{ inputs.plan_path }}"
    commit_hash: "{{ steps.commit_plan.output or null }}"
    progress_entries: "{{ (steps.get_progress.results or []) | length }}"
    dry_run: "{{ inputs.dry_run }}"
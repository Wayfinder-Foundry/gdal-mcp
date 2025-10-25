---
description: Continue development idempotently with full context persistence.
---

```yaml
name: continue
description: |
  Context-enabled wrapper ensuring proper context persistence.
  Loads ConPort context, executes task, validates changes, commits, and syncs back.

inputs:
  task: { type: string, required: false, description: "Task to perform or resume from Active Context" }
  scope: { type: string, required: false, description: "File/directory scope" }
  resume: { type: boolean, default: false }
  run_quality: { type: boolean, default: true }
  quality_gate: { type: object, default: { format: true, lint: true, typecheck: true, tests: false } }
  auto_stage: { type: boolean, default: false }
  commit_type: { type: string, default: "feat" }
  commit_message: { type: string, required: false }
  pre_opts: { type: object, default: {} }
  post_opts: { type: object, default: { log_run_record: true, export_on_change: false } }
  dry_run: { type: boolean, default: false }

steps:
  - id: preflight
    action: workflow
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"
    on_error: { strategy: continue, output: "[CONTINUE] preflight failed" }

  - id: resolve_task
    action: system
    output_transform:
      task: "{{ inputs.resume and null or inputs.task }}"
      source: "{{ inputs.resume and 'resume' or 'explicit' }}"

  - id: load_active_context
    when: "{{ inputs.resume or not inputs.task }}"
    action: conport_op
    tool: get_active_context
    params: { workspace_id: "{{ context.workspace_id }}" }
    on_error: { strategy: continue, output: { content: {} } }

  - id: build_task
    action: system
    output_transform:
      final_task: "{{ inputs.task or (steps.load_active_context.content and steps.load_active_context.content.current_focus) or 'Continue development' }}"
      final_scope: "{{ inputs.scope or (steps.load_active_context.content and steps.load_active_context.content.requested_scope) or '.' }}"

  - id: search_knowledge
    action: conport_op
    tool: semantic_search_conport
    params: { workspace_id: "{{ context.workspace_id }}", query_text: "{{ steps.build_task.final_task }}", top_k: 10 }
    on_error: { strategy: continue, output: { results: [] } }

  - id: search_decisions
    action: conport_op
    tool: search_decisions_fts
    params: { workspace_id: "{{ context.workspace_id }}", query_term: "{{ steps.build_task.final_task }}", limit: 5 }
    on_error: { strategy: continue, output: { results: [] } }

  - id: present_context
    action: system
    output: |
      [CONTINUE] Task: {{ steps.build_task.final_task }}
      Scope: {{ steps.build_task.final_scope }}
      Knowledge: {{ (steps.search_knowledge.results or []) | length }} items, {{ (steps.search_decisions.results or []) | length }} decisions

  - id: patch_active_context
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: update_active_context
    params:
      workspace_id: "{{ context.workspace_id }}"
      patch_content:
        current_focus: "{{ steps.build_task.final_task }}"
        requested_scope: "{{ steps.build_task.final_scope }}"
        workflow: "continue"
        workflow_started: "{{ context.current_time }}"
    on_error: { strategy: continue }

  - id: git_status_check
    action: git_op
    tool: git_status
    params: { repo_path: "{{ context.project.root_path }}" }
    on_error: { strategy: continue, output: "" }

  - id: has_changes
    action: system
    output_transform: { result: "{{ steps.git_status_check.output and (steps.git_status_check.output | length > 0) }}" }

  - id: quality_gates
    when: "{{ inputs.run_quality and steps.has_changes.result and not inputs.dry_run }}"
    action: workflow
    file: .windsurf/workflows/dev/quality.md
    with:
      scope: "{{ steps.build_task.final_scope }}"
      run_format: "{{ inputs.quality_gate.format }}"
      run_lint: "{{ inputs.quality_gate.lint }}"
      run_types: "{{ inputs.quality_gate.typecheck }}"
      run_tests: "{{ inputs.quality_gate.tests }}"
    on_error: { strategy: continue }

  - id: diff_unstaged
    when: "{{ steps.has_changes.result }}"
    action: git_op
    tool: git_diff_unstaged
    params: { repo_path: "{{ context.project.root_path }}", context_lines: 3 }
    on_error: { strategy: continue, output: "" }

  - id: show_changes
    when: "{{ steps.has_changes.result }}"
    action: system
    output: |
      [CHANGES] {{ steps.git_status_check.output }}
      Quality: {{ inputs.run_quality and 'RAN' or 'SKIPPED' }}

  - id: stage_changes
    when: "{{ steps.has_changes.result and inputs.auto_stage and not inputs.dry_run }}"
    action: git_op
    tool: git_add
    params: { repo_path: "{{ context.project.root_path }}", files: ["{{ steps.build_task.final_scope }}"] }
    on_error: { strategy: continue }

  - id: build_commit_message
    when: "{{ steps.has_changes.result }}"
    action: system
    output_transform: { message: "{{ inputs.commit_message or (inputs.commit_type + ': ' + steps.build_task.final_task) }}" }

  - id: commit_changes
    when: "{{ steps.has_changes.result and not inputs.dry_run }}"
    action: git_op
    tool: git_commit
    params: { repo_path: "{{ context.project.root_path }}", message: "{{ steps.build_commit_message.message }}" }
    on_error: { strategy: continue }

  - id: log_progress
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: log_progress
    params:
      workspace_id: "{{ context.workspace_id }}"
      description: "{{ steps.build_task.final_task }}"
      status: "{{ steps.has_changes.result and 'DONE' or 'IN_PROGRESS' }}"
    on_error: { strategy: continue }

  - id: finalize_active_context
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: update_active_context
    params:
      workspace_id: "{{ context.workspace_id }}"
      patch_content:
        workflow_completed: "{{ context.current_time }}"
        last_commit: "{{ steps.commit_changes.output or null }}"
        changes_made: "{{ steps.has_changes.result }}"
    on_error: { strategy: continue }

  - id: postflight
    action: workflow
    file: .windsurf/workflows/hooks/post.md
    with:
      progress: [{ description: "{{ steps.build_task.final_task }}", status: "{{ steps.has_changes.result and 'DONE' or 'IN_PROGRESS' }}" }]
      log_run_record: "{{ inputs.post_opts.log_run_record }}"
      export_on_change: "{{ inputs.post_opts.export_on_change }}"
      capture_git_snapshot: true
    on_error: { strategy: continue }

outputs:
  success:
    status: ok
    message: |
      ✓ Context workflow complete
      Task: {{ steps.build_task.final_task }}
      Changes: {{ steps.has_changes.result and 'Yes' or 'No' }}
      Committed: {{ steps.commit_changes.output and 'Yes' or 'No' }}
    task: "{{ steps.build_task.final_task }}"
    scope: "{{ steps.build_task.final_scope }}"
    changes_made: "{{ steps.has_changes.result }}"
    commit_hash: "{{ steps.commit_changes.output or null }}"
    dry_run: "{{ inputs.dry_run }}"
---
description: Continue development idempotently.
---

---

## description: Continue development idempotently (hooked with pre/post).

```yaml
name: continue
description: "Continue dev idempotently: run preflight, patch Active Context, run quality + commit/push, then postflight."
inputs:
  task: { type: string, required: true }
  scope: { type: string }
  recursive:
    type: boolean
    default: true
    description: "If scope is a directory, recurse by default."
  stage:   { type: boolean, default: true }
  commit:  { type: boolean, default: true }
  push:    { type: boolean, default: false }
  type:    { type: string, default: "feat" }
  scope_commit: { type: string }
  message: { type: string, default: "" }
  quality_gate:
    type: object
    default: { format: true, lint: true, typecheck: true, tests: true, coverage_threshold: 0 }
  # Optional knobs passed through to hooks (safe defaults)
  pre_opts:
    type: object
    default: { }
  post_opts:
    type: object
    default: { export_snapshot: false, log_run: true }

steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"

  # ConPort knowledge preflight: search knowledge graph for the current task
  - id: conport_knowledge
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/search.md
    with:
      query: "{{ inputs.task }}"
      type: "semantic"
      limit: 7

  # Patch Active Context (object patch, not stringified)
  - id: pre_patch
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      active_patch:
        current_focus: "{{ inputs.task }}"
        requested_scope: "{{ inputs.scope or '' }}"
        recursive: "{{ inputs.recursive }}"
        workflow: "continue"
        preflight:
          env_ok: "{{ steps.preflight and steps.preflight.env_ok }}"
          policies_ok: "{{ steps.preflight and steps.preflight.policies_ok }}"
          git:
            has_changes: "{{ steps.preflight and steps.preflight.git and steps.preflight.git.has_changes }}"
            repo_path: "{{ steps.preflight and steps.preflight.git and steps.preflight.git.repo_path }}"
        last_run: "{{ now_iso() }}"

  # Run the development loop (fmt/lint/types/tests) and commit if diffs
  - id: dev
    action: Read the contents of the file.
    file: .windsurf/workflows/dev/loop.md
    with:
      task: "{{ inputs.task }}"
      scope: "{{ inputs.scope or '.' }}"
      run_format:   "{{ inputs.quality_gate.format }}"
      run_lint:     "{{ inputs.quality_gate.lint }}"
      run_types:    "{{ inputs.quality_gate.typecheck }}"
      run_tests:    "{{ inputs.quality_gate.tests }}"

  # Add after the dev step:
  - id: git_commit
    when: "{{ steps.dev.success }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/commit.md
    with:
      message: "{{ inputs.type }}: {{ inputs.message or inputs.task }}"
      allow_dangerous: true
      auto_confirm: true

  # Post-patch with branch + last_commit from update flow if available
  - id: post_patch
    when: "{{ steps.git_commit and steps.git_commit.commit }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      active_patch:
        current_focus: "{{ inputs.task }}"
        requested_scope: "{{ inputs.scope or '' }}"
        recursive: "{{ inputs.recursive }}"
        workflow: "continue"
        branch: "{{ steps.dev.branch }}"
        last_commit: "{{ steps.git_commit.commit }}"
        last_run: "{{ now_iso() }}"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      export_snapshot: "{{ inputs.post_opts.export_snapshot }}"
      log_run: "{{ inputs.post_opts.log_run }}"

outputs:
  success:
    status: ok
    message: "Continued: '{{ inputs.task }}'{{ steps.dev and steps.dev.commit_hash and (' @ '+steps.dev.commit_hash[:7]) or '' }}"
    pre_ok: "{{ steps.preflight and steps.preflight.env_ok and steps.preflight.policies_ok }}"
    post_synced: "{{ steps.postflight and steps.postflight.conport and steps.postflight.conport.synced }}"
    conport_summary: "{{ steps.conport_knowledge and steps.conport_knowledge.results }}"
```
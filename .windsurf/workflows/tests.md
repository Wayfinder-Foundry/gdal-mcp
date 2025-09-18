---
description: Generate tests for scope, run pytest, commit if green.
---

```yaml
---
description: Generate tests for scope, run pytest, and commit only if green. Hooked with pre/post.
---

name: tests
description: |
  Generate tests for the given scope, run pytest (Poetry if available, else system),
  and commit changes only when tests pass. Wrap with preflight/postflight.

inputs:
  task:  { type: string, required: true }
  scope: { type: string, required: true }
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

  # ---------- Generate tests for the scope ----------
  - id: gen_tests
    action: coding_op
    tool: generate_tests_for_scope
    params:
      scope: "{{ inputs.scope }}"
      repo_root: "{{ context.project.root_path }}"

  # ---------- Choose pytest command (Poetry preferred, fallback to system) ----------
  - id: choose_pytest_cmd
    action: system
    output_transform:
      tests_target: >-
        {{
          inputs.scope and inputs.scope
          or (context.project.tests_path or "tests")
        }}
      cmd: >-
        {{
          (context.poetry and context.poetry.executable)
          and (context.poetry.executable ~ " run pytest -q " ~
               (inputs.scope and inputs.scope or (context.project.tests_path or "tests")))
          or ("pytest -q " ~ (inputs.scope and inputs.scope or (context.project.tests_path or "tests")))
        }}

  # ---------- Run pytest ----------
  - id: run_pytest
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ steps.choose_pytest_cmd.cmd }}"
      cwd: "{{ context.project.root_path }}"
    on_error:
      capture: true

  # ---------- If green: format/lint/typecheck (no test re-run) and commit ----------
  - id: commit_if_green
    when: "{{ run_pytest.exit_code == 0 }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      scope: "{{ inputs.scope }}"
      quality_gate:
        format: true
        lint: true
        typecheck: true
        tests: false           # tests already ran; avoid double running
        coverage_threshold: 0
      commit_type: "test"
      commit_scope: "auto"
      commit_subject: "{{ inputs.task }}"
      do_stage: true
      do_commit: true
      do_push: false

  # ---------- Prepare progress payload for postflight ----------
  - id: progress_payload
    action: system
    output_transform:
      progress:
        - description: >-
            Tests '{{ inputs.task }}' — scope={{ inputs.scope }}
            {{ run_pytest.exit_code == 0
               and (steps.commit_if_green.commit_hash and 'passed, committed ' ~ steps.commit_if_green.commit_hash[:7] or 'passed, no diffs')
               or  'failed' }}
          status: "{{ run_pytest.exit_code == 0 and 'DONE' or 'IN_PROGRESS' }}"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.progress_payload.progress }}"
      active_patch:
        current_focus: "{{ inputs.task }}"
        requested_scope: "{{ inputs.scope }}"
        workflow: "tests"
        last_run: "{{ now_iso() }}"
      {{ inputs.post_opts | tojson }}

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: >-
      Tests {{ run_pytest.exit_code == 0 and 'passed' or 'failed' }}.
      {{ (steps.commit_if_green and steps.commit_if_green.commit_hash) and ('commit=' ~ steps.commit_if_green.commit_hash[:7]) or '' }}
    pytest_rc: "{{ run_pytest.exit_code }}"
```
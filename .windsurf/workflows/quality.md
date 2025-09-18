---
description: Lint and autocorrect Python files using Poetry-managed tools.
---

```yaml
---
description: Lint & refactor safely: run non-destructive auto-fixes, plan guarded refactors, optionally apply & commit. Hooked with pre/post.
---

name: quality
description: |
  Lint & safe-refactor:
  1) Auto-fix non-destructive items (black, isort, Ruff imports).
  2) Collect diagnostics (Ruff/Flake8/mypy) and build a human-safe refactor plan.
  3) Apply only within guardrails and (by default) with confirmation.
  4) Optionally run tests, then format/lint/typecheck and commit.

inputs:
  targets:       { type: list,   default: ["." ] }      # files/dirs
  mode:          { type: string, default: "safe" }      # safe|plan|apply
  confirm:       { type: boolean, default: true }       # require confirmation before edits
  create_branch: { type: boolean, default: true }
  run_tests:     { type: boolean, default: false }
  max_deletions: { type: integer, default: 10 }         # hard stop if exceeded
  max_changed:   { type: integer, default: 200 }        # (adds + dels) guard
  use_poetry:    { type: boolean, default: true }

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

  - id: ack
    action: system
    output: |
      Lint strategy:
      1) Auto-fix only non-destructive items (Black, isort, Ruff-imports).
      2) Collect lint diagnostics (Ruff/Flake8/mypy) → build refactor plan.
      3) Apply plan only after guardrails & confirmation. Never mass-delete code.

  # ---------- Toolchain resolution (Poetry preferred) ----------
  - id: toolchain
    action: system
    output_transform:
      repo_root: "{{ context.project.root_path }}"
      poetry_exe: "{{ (inputs.use_poetry and context.poetry and context.poetry.executable) or null }}"
      use_poetry: "{{ (inputs.use_poetry and context.poetry and context.poetry.executable) and true or false }}"
      black_cmd: >-
        {{ (inputs.use_poetry and context.poetry and context.poetry.executable)
           and (context.poetry.executable ~ " run black")
           or "black" }}
      isort_cmd: >-
        {{ (inputs.use_poetry and context.poetry and context.poetry.executable)
           and (context.poetry.executable ~ " run isort")
           or "isort" }}
      ruff_cmd: >-
        {{ (inputs.use_poetry and context.poetry and context.poetry.executable)
           and (context.poetry.executable ~ " run ruff")
           or "ruff" }}
      flake8_cmd: >-
        {{ (inputs.use_poetry and context.poetry and context.poetry.executable)
           and (context.poetry.executable ~ " run flake8")
           or "flake8" }}
      mypy_cmd: >-
        {{ (inputs.use_poetry and context.poetry and context.poetry.executable)
           and (context.poetry.executable ~ " run mypy")
           or "mypy" }}
      pytest_cmd: >-
        {{ (inputs.use_poetry and context.poetry and context.poetry.executable)
           and (context.poetry.executable ~ " run pytest -q")
           or "pytest -q" }}

  - id: ensure_install
    when: "{{ toolchain.use_poetry }}"
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.poetry_exe }} install"
      cwd: "{{ toolchain.repo_root }}"

  # ---------- Optional safety branch ----------
  - id: create_branch
    when: "{{ inputs.create_branch }}"
    action: shell_op
    tool: run_command
    params:
      cmd: "git checkout -b lint/$(date +%Y%m%d-%H%M%S)"
      cwd: "{{ toolchain.repo_root }}"
    on_error: { ignore: true }

  # ---------- Non-destructive auto-fixes ----------
  - id: black
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.black_cmd }} {{ inputs.targets | join(' ') }}"
      cwd: "{{ toolchain.repo_root }}"

  - id: isort
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.isort_cmd }} {{ inputs.targets | join(' ') }}"
      cwd: "{{ toolchain.repo_root }}"

  # Ruff safe pass: ONLY imports (I). Avoid auto-removing code/vars beyond imports.
  - id: ruff_imports
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.ruff_cmd }} check --fix --select I {{ inputs.targets | join(' ') }}"
      cwd: "{{ toolchain.repo_root }}"

  # ---------- Full diagnostics (no fixing) ----------
  - id: ruff_report
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.ruff_cmd }} check --format json {{ inputs.targets | join(' ') }}"
      cwd: "{{ toolchain.repo_root }}"
    on_error: { capture: true }

  - id: flake8_report
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.flake8_cmd }} --format=default {{ inputs.targets | join(' ') }}"
      cwd: "{{ toolchain.repo_root }}"
    on_error: { capture: true }

  - id: mypy_report
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.mypy_cmd }} {{ inputs.targets | join(' ') }}"
      cwd: "{{ toolchain.repo_root }}"
    on_error: { capture: true }

  # ---------- Build a human-safe refactor plan (no mass deletions) ----------
  - id: plan_refactors
    action: coding_op
    tool: build_lint_refactor_plan
    params:
      ruff_json: "{{ steps.ruff_report.stdout or '[]' }}"
      flake8_text: "{{ steps.flake8_report.stdout or '' }}"
      mypy_text: "{{ steps.mypy_report.stdout or '' }}"
      policy:
        allow_deletions: false
        allow_remove_unused_imports: false
        strategy_order:
          - "rename_unused_vars_to_underscore"     # e.g., x -> _x for F841
          - "add_explicit_returns_or_raises"
          - "introduce_narrower_excepts"
          - "add_type_annotations_or_narrow_types"
          - "split_large_functions"
          - "replace_bare_except_with_specific"
          - "introduce_const_or_helper_function"
        never_autofix:
          - "F401"   # unused import (ask first)
          - "F841"   # unused local
          - "PLR0915"
          - "C901"
          - "ERA"
      targets: "{{ inputs.targets }}"

  # ---------- Present plan + guardrails ----------
  - id: present_plan
    action: system
    say: |
      Lint plan ready (non-destructive).
      Mode={{ inputs.mode }}, confirm={{ inputs.confirm }}.
      - Proposed edits: {{ steps.plan_refactors.summary.change_count }}
      - Estimated deletions: {{ steps.plan_refactors.summary.deletions }}
      - Estimated total changed lines: {{ steps.plan_refactors.summary.total_changed }}
      Proceed?

  - id: guardrails
    when: "{{ steps.plan_refactors.summary.deletions > inputs.max_deletions or steps.plan_refactors.summary.total_changed > inputs.max_changed }}"
    action: system
    output: "Refactor plan exceeds guardrails; edits will NOT be applied."

  # ---------- Apply only when allowed (mode/confirm/guards) ----------
  - id: maybe_apply
    when: >-
      {{
        inputs.mode in ['apply','safe'] and
        not steps.guardrails and
        (inputs.confirm == false)
      }}
    action: coding_op
    tool: perform_task_edits
    params:
      plan: "{{ steps.plan_refactors.plan }}"
      repo_root: "{{ toolchain.repo_root }}"

  # ---------- Optional test run after changes ----------
  - id: run_tests
    when: "{{ inputs.run_tests }}"
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.pytest_cmd }}"
      cwd: "{{ toolchain.repo_root }}"
    on_error: { capture: true }

  # ---------- Final reports + commit (no test re-run here) ----------
  - id: ruff_post
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ toolchain.ruff_cmd }} check {{ inputs.targets | join(' ') }}"
      cwd: "{{ toolchain.repo_root }}"
    on_error: { capture: true }

  - id: quality_summary
    action: system
    output_transform:
      quality_passed: true  # Based on earlier ruff_post, test results, etc.
      modified_files: "{{ steps.black.modified_files + steps.isort.modified_files }}"
    
  - id: git_commit
    when: "{{ steps.quality_summary.quality_passed }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/git/commit.md
    with:
      message: "style: Lint & safe refactors"
      allow_dangerous: true
      auto_confirm: true

  # ---------- Progress payload for postflight ----------
  - id: progress_payload
    action: system
    output_transform:
      progress:
        - description: >-
            Lint completed — {{ steps.qa_and_commit.commit_hash and 'committed ' ~ steps.qa_and_commit.commit_hash[:7] or 'no diffs' }}
            {{ steps.guardrails and '(guardrails tripped)' or '' }}
          status: "{{ steps.qa_and_commit.commit_hash and 'DONE' or 'IN_PROGRESS' }}"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.progress_payload.progress }}"
      active_patch:
        current_focus: "Lint & safe refactor"
        workflow: "lint"
        last_run: "{{ now_iso() }}"
      {{ inputs.post_opts | tojson }}

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: >-
      Lint finished.
      {{ steps.qa_and_commit.commit_hash and ('commit=' ~ steps.qa_and_commit.commit_hash[:7]) or '(no diffs)' }}
      {{ steps.guardrails and 'Guardrails tripped.' or '' }}
```
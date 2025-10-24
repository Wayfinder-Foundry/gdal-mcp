---
description: Catch-all development workflow.
---

id: dev
version: 1
enabled: true
priority: high
trigger:
  phrases_any:
    - "dev"
    - "start dev workflow"
    - "implement feature"
    - "refactor module"
    - "fix bug"
options:
  dry_run: false
  max_fix_passes: 3
  create_branch: true
  branch_prefix: "feat/"
  context7_on_unknowns: true
  commit_push: false
  python_exec: "python3"
  mypy_targets: ["."]
  ruff_targets: ["."]
  # heuristics
  plan_if_ambiguous: true
  ambiguity_keywords:
    - "improve"
    - "refactor"
    - "optimize"
    - "add feature"
    - "enhance"
    - "not sure"
    - "investigate"
state:
  # persistent crumbs the workflow updates as it runs; store in memory or a .workflow/ folder
  branch: null
  plan_summary_path: ".workflow/dev_plan.yaml"
  serena_edit_plan_path: ".workflow/serena_edit_plan.yaml"
  last_git_diff_summary: null
  ruff_passes: 0
  mypy_passes: 0

steps:

  # 0) Preflight: repo hygiene
  - name: preflight.git
    tool: git-mcp
    run:
      - status
      - current_branch
      - last_commit
      - detect_default_branch  # if supported
    on_result:
      - set: state.branch = "{{result.current_branch}}"
      - if: "{{result.working_tree_dirty and not options.dry_run}}"
        then: "Ask user to stash/commit or rerun with dry_run: true and exit"
      - if: "{{options.create_branch and (result.on_default_branch or state.branch in ['main','master'])}}"
        then:
          - create_branch "{{options.branch_prefix}}auto-{{date:%Y%m%d-%H%M}}"
          - set: state.branch = "{{last_result.new_branch}}"

  # 0b) Stamp the start in ConPort (non-blocking)
  - name: preflight.conport
    tool: conport
    continue_on_error: true
    run:
      - remember
        text: >
          DEV workflow start at {{now}}. Branch={{state.branch}}. DryRun={{options.dry_run}}.
          Goal: {{user_goal or 'unspecified'}}.

  # 1) Sequential-Thinking: conditional plan/decision stabilization
  - name: plan.sequential
    tool: sequential-thinking
    run_if:
      - "{{options.plan_if_ambiguous}}"
      - "user request is vague OR multiple approaches likely OR prior run flagged uncertainty"
    run:
      - reflect
        prompt: |
          You are creating a lightweight plan for a code change.
          Summarize:
          - problem statement & success criteria
          - candidate approaches (2–3), pros/cons, pick one (with reason)
          - likely files/modules/symbols to touch
          - risks & blast radius
          - whether we need library/API verification (Context7)
          - a concrete step list (N steps)
      - save_plan path="{{state.plan_summary_path}}"
    on_result:
      - route:
          if: "plan indicates 'no code change needed'"
          then: "Summarize and stop (optionally write ConPort note)"
          else: "continue"

  # 2) Serena grounding (always for non-trivial work)
  - name: serena.ground
    tool: serena
    run:
      - index_project_if_needed
      - get_symbols_overview limit=200
      - infer_targets_from:
          - "{{state.plan_summary_path}}"
          - "recent git changes"
          - "user goal"
      - structural_summary max_files=100
    on_result:
      - produce_plan:
          path: "{{state.serena_edit_plan_path}}"
          content: |
            # minimal, reviewable plan Serena can apply
            targets: {{inferred_targets}}
            insertions: []
            refactors: []
            notes: "Grounded by structural_summary and plan_summary"

  # 3) Context7 (conditional certainty on APIs)
  - name: context7.verify
    when: "{{options.context7_on_unknowns}}"
    tool: context7
    run_if:
      - "plan or serena grounding references unknown/ambiguous APIs"
      - "previous mypy/ruff errors imply attribute/method mismatch"
    run:
      - lookup library="{{inferred_library}}" query="{{unknown_symbol_or_signature}}"
      - summarize usage="concise" attach_to="{{state.serena_edit_plan_path}}"

  # 4) Serena: refine edit plan with precise placements
  - name: serena.plan_edits
    tool: serena
    run:
      - propose_insertions_from_goals
          plan="{{state.plan_summary_path}}"
          into="{{state.serena_edit_plan_path}}"
      - safe_refactor_plan update="{{state.serena_edit_plan_path}}"

  # 5) Apply edits (respect dry-run)
  - name: serena.apply
    tool: serena
    run:
      - apply_edit_plan file="{{state.serena_edit_plan_path}}" dry_run="{{options.dry_run}}"
    on_result:
      - if: "{{options.dry_run}}"
        then: "Show unified diff and STOP before QA"
      - else: "continue"

  # 6) Ruff fix loop (format + lint)
  - name: qa.ruff
    loop:
      count: "{{options.max_fix_passes}}"
      steps:
        - tool: shell
          run:
            - "{{options.python_exec}} -m ruff check {{options.ruff_targets}} --fix || true"
            - "{{options.python_exec}} -m ruff format {{options.ruff_targets}} || true"
        - set: state.ruff_passes = "{{state.ruff_passes + 1}}"
        - tool: git-mcp
          run:
            - diff --stat
          on_result:
            - set: state.last_git_diff_summary = "{{result.diff_stat}}"
            - break_if: "no changes OR ruff produced no further diagnostics"

  # 7) Mypy fix loop (types) with Serena targeting
  - name: qa.mypy
    loop:
      count: "{{options.max_fix_passes}}"
      steps:
        - tool: shell
          run:
            - "{{options.python_exec}} -m mypy {{options.mypy_targets}} || true"
        - set: state.mypy_passes = "{{state.mypy_passes + 1}}"
        - tool: serena
          run_if:
            - "last_shell_stdout contains 'error:'"
          run:
            - pinpoint_symbol_from_mypy mypy_output="{{last_shell_stdout}}"
            - open_symbol_context
            - propose_fix_from_types
            - apply_edits
        - tool: git-mcp
          run:
            - diff --stat
          on_result:
            - break_if: "mypy clean OR no further Serena deltas"

  # 8) Optional tests (if repo looks test-enabled)
  - name: qa.tests
    when: "path_exists('tests/') or path_exists('pytest.ini') or file_contains('pyproject.toml','[tool.pytest]')"
    tool: shell
    run:
      - "{{options.python_exec}} -m pytest -q || true"
    on_result:
      - tool: serena
        run_if:
          - "last_shell_stdout contains 'FAILED'"
        run:
          - map_failures_to_symbols pytest_output="{{last_shell_stdout}}"
          - propose_localized_fixes
          - apply_edits

  # 9) Commit (and optional push)
  - name: vcs.commit
    tool: git-mcp
    run:
      - add_all
      - commit
        message: >
          {{auto_summary_from_diffs prefix='dev: '
            include_changed_files=true
            include_issue_or_task_ref=true
            include_plan_excerpt=state.plan_summary_path}}
      - push when="{{options.commit_push}}"

  # 10) Postflight snapshot (non-blocking)
  - name: postflight.conport
    tool: conport
    continue_on_error: true
    run:
      - remember
        text: >
          DEV workflow end at {{now}} on {{state.branch}}.
          Ruff passes={{state.ruff_passes}}, mypy passes={{state.mypy_passes}}.
          Last diff summary: {{state.last_git_diff_summary}}.
          Plan: {{state.plan_summary_path}}; Edits: {{state.serena_edit_plan_path}}.

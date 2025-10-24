---
description:  Guided refactor using project styleguides. Plan edits under constraints, apply safely, and log via postflight.
---

---
description: Guided refactor using project styleguides. Plan edits under constraints, apply safely, and log via postflight.
---

```yaml
name: refactor
description: |
  Refactor targeted files using project styleguides:
  - Load env/policies via preflight
  - Read rule docs to ground the agent
  - Propose a constrained refactor plan (respecting allow_moves / change limits)
  - Apply via quality gate (fmt/lint/typecheck/tests) and commit
  - Sync Decision + Progress via postflight

inputs:
  task:        { type: string, required: true }              # e.g., "Refactor tabular GUI for clarity"
  targets:     { type: array,  items: { type: string }, required: true }
  rationale:   { type: string, default: "" }
  dry_run:     { type: boolean, default: false }
  push:        { type: boolean, default: false }
  allow_moves: { type: boolean, default: false }
  max_changes_per_file: { type: integer, default: 50 }
  enforce_rules:
    type: array
    items: { type: string }
    default: []

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

  # ---------- Styleguide rule docs (grounding) ----------
  - id: rules_aliasing
    action: Read the contents of the file.
    file: .windsurf/rules/aliasing.md
  - id: rules_complex_expr
    action: Read the contents of the file.
    file: .windsurf/rules/complex-expressions.md
  - id: rules_constants
    action: Read the contents of the file.
    file: .windsurf/rules/constants.md
  - id: rules_dicts
    action: Read the contents of the file.
    file: .windsurf/rules/dictionaries.md
  - id: rules_exports
    action: Read the contents of the file.
    file: .windsurf/rules/exports.md
  - id: rules_func_len
    action: Read the contents of the file.
    file: .windsurf/rules/function-length.md
  - id: rules_funcs_nested
    action: Read the contents of the file.
    file: .windsurf/rules/functions-nested.md
  - id: rules_inline_expr
    action: Read the contents of the file.
    file: .windsurf/rules/inline-expressions.md
  - id: rules_math_expr
    action: Read the contents of the file.
    file: .windsurf/rules/math-expressions.md
  - id: rules_module_scope
    action: Read the contents of the file.
    file: .windsurf/rules/module_scope.md
  - id: rules_namespacing
    action: Read the contents of the file.
    file: .windsurf/rules/namespacing.md
  - id: rules_naming
    action: Read the contents of the file.
    file: .windsurf/rules/naming-conventions.md
  - id: rules_shadowing
    action: Read the contents of the file.
    file: .windsurf/rules/shadowing.md
  - id: rules_single_resp
    action: Read the contents of the file.
    file: .windsurf/rules/single-responsibility.md
  - id: rules_solid
    action: Read the contents of the file.
    file: .windsurf/rules/SOLID.md
  - id: rules_types
    action: Read the contents of the file.
    file: .windsurf/rules/type-annotations.md
  - id: rules_any
    action: Read the contents of the file.
    file: .windsurf/rules/type-any.md

  # ---------- Analyze targets & propose plan ----------
  - id: read_targets
    action: coding_op
    tool: read_files
    params:
      paths: "{{ inputs.targets }}"
      allow_large: true

  - id: plan
    action: coding_op
    tool: propose_refactor_plan
    params:
      repo_root: "{{ context.project.root_path }}"
      targets: "{{ inputs.targets }}"
      current_code_blobs: "{{ steps.read_targets.contents }}"
      rationale_seed: "{{ inputs.rationale }}"
      constraints:
        enforce_only: "{{ inputs.enforce_rules or [] }}"
        hard_limits:
          max_changes_per_file: "{{ inputs.max_changes_per_file }}"
          allow_moves: "{{ inputs.allow_moves }}"
        objectives:
          - "Preserve external behavior unless task explicitly requires API/IO change"
          - "Alias repeated chains"
          - "Extract complex/inline/math expressions"
          - "Eliminate magic literals via constants/enums"
          - "Shorten long functions (~20 LOC target)"
          - "Enforce SRP/module scoping; splits only if allow_moves=true"
          - "Avoid shadowing"
          - "Prefer clear naming conventions"
          - "Type annotations comprehensive; avoid Any"
          - "Organize exports via __all__"

  # If moves were proposed but not allowed, re-plan without moves
  - id: plan_no_moves
    when: "{{ (steps.plan.requires_moves or false) and (not inputs.allow_moves) }}"
    action: coding_op
    tool: propose_refactor_plan
    params:
      repo_root: "{{ context.project.root_path }}"
      targets: "{{ inputs.targets }}"
      current_code_blobs: "{{ steps.read_targets.contents }}"
      rationale_seed: "{{ inputs.rationale }}"
      constraints:
        enforce_only: "{{ inputs.enforce_rules or [] }}"
        hard_limits:
          max_changes_per_file: "{{ inputs.max_changes_per_file }}"
          allow_moves: false
        objectives: "{{ steps.plan.constraints.objectives }}"

  - id: select_plan
    action: system
    output_transform:
      plan: "{{ steps.plan_no_moves or steps.plan }}"

  # ---------- Apply edits via update atom ----------
  - id: apply_and_validate
    when: "{{ not inputs.dry_run }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      scope: "{{ inputs.targets | join(' ') }}"
      quality_gate:
        format: true
        lint: true
        typecheck: true
        tests: true
        coverage_threshold: 0
      commit_type: "refactor"
      commit_scope: "guided"
      commit_subject: "{{ inputs.task }}"
      do_stage: true
      do_commit: true
      do_push: "{{ inputs.push }}"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      active_patch:
        current_focus: "{{ inputs.task }}"
        workflow: "refactor"
        requested_scope: "{{ inputs.targets }}"
        last_commit: "{{ steps.apply_and_validate.commit_hash or null }}"
        branch: "{{ steps.apply_and_validate.branch or null }}"
        last_run: "{{ now_iso() }}"
      decisions:
        - "Guided refactor: {{ inputs.task }} ({{ inputs.targets | length }} file(s)))"
      progress:
        - "Refactor completed and validated"
      product_patch: {}
      <<: "{{ inputs.post_opts }}"

outputs:
  success:
    status: ok
    message: >-
      Guided refactor complete for {{ inputs.targets | length }} file(s).
      {{ steps.apply_and_validate and steps.apply_and_validate.commit_hash and ('Commit ' ~ steps.apply_and_validate.commit_hash[:7]) or '' }}
```
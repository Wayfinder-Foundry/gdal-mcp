---
# Description: Core development loop: take a prompted task + scope, run quality gates. No VCS or ConPort here.
---

```yaml
name: dev_loop
description: |
  Apply the development loop for the given task/scope:
  - Run configurable quality gates (format, lint, typecheck, tests)
  - Emit a concise summary for downstream hooks/workflows
  - No staging/commit/push here; that’s handled elsewhere

inputs:
  task:  { type: string, required: true }
  scope: { type: string, default: "." }

  # Gate toggles (forwarded to dev_quality)
  run_format: { type: boolean, default: true }
  run_lint:   { type: boolean, default: true }
  run_types:  { type: boolean, default: true }
  run_tests:  { type: boolean, default: true }

  # Optional command overrides; empty means "let dev_quality resolve"
  fmt_cmds:   { type: array,  default: ["/home/jgodau/.local/bin/poetry run black"] }
  lint_cmds:  { type: array,  default: ["/home/jgodau/.local/bin/poetry run ruff"] }
  types_cmds: { type: array,  default: ["/home/jgodau/.local/bin/poetry run mypy"] }
  style_cmds: { type: array,  default: ["/home/jgodau/.local/bin/poetry run flake8"] }
  tests_cmd:  { type: string, default: "/home/jgodau/.local/bin/poetry run pytest" }

steps:
  - id: note_task
    action: system
    output: "Dev loop started for task: {{ inputs.task }} (scope={{ inputs.scope }})"

  - id: quality
    action: Read the contents of the file.
    file: .windsurf/workflows/dev/quality.md
    with:
      scope:       "{{ inputs.scope }}"
      run_format:  "{{ inputs.run_format }}"
      run_lint:    "{{ inputs.run_lint }}"
      run_types:   "{{ inputs.run_types }}"
      run_styles:   "{{ inputs.run_types }}"
      run_tests:   "{{ inputs.run_tests }}"
      fmt_cmds:    "{{ inputs.fmt_cmds | default([]) }}"
      lint_cmds:   "{{ inputs.lint_cmds | default([]) }}"
      types_cmds:  "{{ inputs.types_cmds | default([]) }}"
      tests_cmd:   "{{ inputs.tests_cmd | default('') }}"

  - id: summarize
    action: system
    output_transform:
      summary:
        task: "{{ inputs.task }}"
        scope: "{{ inputs.scope }}"
        ran:
          format: "{{ inputs.run_format }}"
          style: "{{ inputs.run_styles }}"
          lint:   "{{ inputs.run_lint }}"
          types:  "{{ inputs.run_types }}"
          tests:  "{{ inputs.run_tests }}"
      message: >-
        Dev loop complete for '{{ inputs.task }}' on {{ inputs.scope }} —
        gates: [format={{ inputs.run_format }}, lint={{ inputs.run_lint }},
        types={{ inputs.run_types }}, tests={{ inputs.run_tests }}]

outputs:
  success:
    status: ok
    message: "{{ steps.summarize.message }}"
    loop_summary: "{{ steps.summarize.summary }}"
```
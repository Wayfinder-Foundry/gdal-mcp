---
description:  Create an executable debug script appropriate for the environment, run it, capture diagnostics, optionally auto-fix, then retry once.
---

---
description: Create & run a language-native debug script (agent-inferred), capture diagnostics, attempt a reasonable fix, and retry once. No tests.
---

```yaml
name: debug
description: |
  Create an executable debug script appropriate for the environment (agent-inferred),
  run it, capture diagnostics, optionally auto-fix (fmt/lint/typecheck only), then retry once.
  Wrap with preflight/postflight. Do NOT run tests here.

inputs:
  task:        { type: string,  required: true }            # human description of what we’re debugging
  scope:       { type: string,  required: false, default: "" }  # file/dir hint for the agent
  attempts:    { type: integer, required: false, default: 1 }   # max retries after auto-fix (0/1)
  run_args:    { type: array,   required: false, default: [] }  # args for the debug script
  pre_opts:    { type: object,  required: false, default: {} }
  post_opts:
    type: object
    required: false
    default: { capture_git_snapshot: true, log_run_record: true, export_on_change: false }

# --------------------------------- Steps -------------------------------------
steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"

  # ---------- Resolve debug filename & working dir ----------
  - id: resolve_context
    action: system
    output_transform:
      repo_root: "{{ context.project.root_path }}"
      # Prefer an explicit scope-derived base, else ConPort focus, else 'session'
      base:
        {% raw %}{{ (inputs.scope and (inputs.scope.split('/')[-1].split('.')[0])) or
            (steps.preflight.preflight.conport.current_focus and
             steps.preflight.preflight.conport.current_focus | replace(' ', '_')[:24]) or
            'session' }}{% endraw %}
      # Let the agent decide extension by language; we pass a suggested stem only
      debug_stem: "debug_{{ base }}"

  # ---------- Ask the agent to synthesize an appropriate debug script ----------
  - id: plan_and_render_script
    action: coding_op
    tool: synthesize_text
    params:
      prompt: |
        You are creating a minimal, runnable debug script for this repository.
        Goals:
        - Be idiomatic for the native environment (Python/Node/TS/Go/Java/C#/Rust/Bash/etc.).
        - Prefer the project's existing toolchain (poetry, uv, pip, npm, pnpm, yarn, ts-node, go, cargo, gradle, dotnet, etc.).
        - The script should reproduce the runtime of the given scope (file or dir) or an app entrypoint if scope is empty.
        - Print clear diagnostics (exit code, duration, any key warnings).
        - Do NOT run tests here.
        - Keep it short and self-contained.

        Repository root: {{ steps.resolve_context.repo_root }}
        Suggested filename stem (no extension): {{ steps.resolve_context.debug_stem }}
        Task: {{ inputs.task }}
        Scope: {{ inputs.scope or '(none provided)' }}
        Args (JSON): {{ inputs.run_args | tojson }}

        Output format (strict JSON):
        {
          "filename": "<full filename including chosen extension>",
          "content": "<file contents>",
          "exec_cmd": "<command to run the script from repo root>",
          "fix_instructions": [
            "short, concrete suggestions for minimal auto-fixes (fmt/lint/typecheck) without tests"
          ]
        }

  - id: write_script
    action: fs_op
    tool: write_file
    params:
      path: "{{ steps.plan_and_render_script.output.filename }}"
      content: "{{ steps.plan_and_render_script.output.content }}"
      make_parents: true

  - id: chmod_exec
    action: shell_op
    tool: run_command
    params:
      cmd: "chmod +x {{ steps.plan_and_render_script.output.filename }}"
      cwd: "{{ steps.resolve_context.repo_root }}"
    on_error: { ignore: true }

  # ---------- First run ----------
  - id: run_debug
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ steps.plan_and_render_script.output.exec_cmd }}"
      cwd: "{{ steps.resolve_context.repo_root }}"
    on_error:
      capture: true

  # ---------- Optional auto-fix pass (fmt/lint/typecheck only) ----------
  - id: should_fix
    action: coding_op
    tool: select_if
    params:
      condition: "{{ (run_debug.exit_code and run_debug.exit_code != 0) and (inputs.attempts | int > 0) }}"
      then: proceed
      else: skip

  - id: apply_reasonable_fixes
    when: "{{ steps.should_fix.result == 'proceed' }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      scope: "{{ inputs.scope or '' }}"
      quality_gate:
        format: true
        lint: true
        typecheck: true
        tests: false
        coverage_threshold: 0
      commit_type: "chore"
      commit_scope: "debug"
      commit_subject: "{{ inputs.task }} (auto-fix)"
      do_stage: true
      do_commit: true
      do_push: false

  - id: run_debug_retry
    when: "{{ steps.should_fix.result == 'proceed' }}"
    action: shell_op
    tool: run_command
    params:
      cmd: "{{ steps.plan_and_render_script.output.exec_cmd }}"
      cwd: "{{ steps.resolve_context.repo_root }}"
    on_error:
      capture: true

  # ---------- Prepare ConPort progress payload for postflight ----------
  - id: summarize_progress
    action: system
    output_transform:
      progress:
        - description: >-
            Debug '{{ inputs.task }}' — script: {{ steps.plan_and_render_script.output.filename }}
            initial_exit={{ run_debug.exit_code | default(0) }}
            retry_exit={{ (steps.run_debug_retry and steps.run_debug_retry.exit_code) | default(null) }}
          status: >-
            {{
              ((steps.run_debug_retry and steps.run_debug_retry.exit_code == 0) or (run_debug.exit_code == 0))
              and 'DONE' or 'IN_PROGRESS'
            }}

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.summarize_progress.progress }}"
      active_patch:
        current_focus: "{{ inputs.task }}"
        last_run: "{{ now_iso() }}"
      {{ inputs.post_opts | tojson }}

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: >-
      Debug completed for '{{ inputs.task }}' —
      script={{ steps.plan_and_render_script.output.filename }},
      rc={{ (steps.run_debug_retry and steps.run_debug_retry.exit_code) or run_debug.exit_code }}
    script_path: "{{ steps.plan_and_render_script.output.filename }}"
    first_rc: "{{ run_debug.exit_code | default(0) }}"
    second_rc: "{{ (steps.run_debug_retry and steps.run_debug_retry.exit_code) | default(null) }}"
```
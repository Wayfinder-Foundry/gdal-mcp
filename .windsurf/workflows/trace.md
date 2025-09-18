---
description: Generate import and dependency trace for a scope, save artifacts, log to ConPort for RAG.
---

```yaml
name: trace
description: "Generate import/dependency trace for a scope; save artifacts; log to ConPort for RAG."

inputs:
  scope:   { type: string, required: true }  # file or directory (directory implies recursive)
  depth:   { type: integer, default: 2 }
  format:  { type: string,  default: "svg" } # svg|png|json (json always saved for data)
  out_dir: { type: string,  default: "docs/trace" }
  push:    { type: boolean, default: false }

steps:
  # 0) Env + load
  - id: env
    action: Read the contents of the file.
    file: .windsurf/workflows/config/env.md

  - id: load
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/load.md

  # 1) Pre-patch Active Context
  - id: pre_patch
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      active_patch:
        current_focus: "Trace: {{ inputs.scope }}"
        requested_scope: "{{ inputs.scope }}"
        workflow: "trace"
        last_run: "{{ now_iso() }}"

  # 2) Build the graph (code-only; no side effects)
  - id: build_graph
    action: coding_op
    tool: generate_import_graph
    params:
      scope: "{{ inputs.scope }}"
      max_depth: "{{ inputs.depth }}"
      repo_root: "{{ context.project.root_path }}"
      # expected: { nodes[], edges[], stats{modules,files}, dot, json }

  # 3) Write artifacts (JSON always; image if requested)
  - id: ensure_out_dir
    action: fs_op
    tool: make_dirs
    params: { path: "{{ context.project.root_path }}/{{ inputs.out_dir }}" }

  - id: write_json
    action: fs_op
    tool: write_text
    params:
      path: "{{ context.project.root_path }}/{{ inputs.out_dir }}/trace_{{ inputs.scope|slug }}.json"
      text: "{{ steps.build_graph.json }}"

  - id: write_svg
    when: "{{ inputs.format in ['svg','png'] }}"
    action: coding_op
    tool: render_graphviz_dot
    params:
      dot: "{{ steps.build_graph.dot }}"
      format: "{{ inputs.format }}"
      out_path: "{{ context.project.root_path }}/{{ inputs.out_dir }}/trace_{{ inputs.scope|slug }}.{{ inputs.format }}"

  # 4) Stage/commit artifacts iff changed
  - id: has_diffs
    action: shell_op
    tool: run_shell
    params:
      cmd: "git add {{ inputs.out_dir }} && (git diff --cached --quiet || echo changed)"
      cwd: "{{ context.project.root_path }}"

  - id: commit
    when: "{{ steps.has_diffs.stdout|contains('changed') }}"
    action: shell_op
    tool: run_shell
    params:
      cmd: >
        git commit -m "docs(trace): {{ inputs.scope }} (depth={{ inputs.depth }})"
      cwd: "{{ context.project.root_path }}"

  - id: get_hash
    action: shell_op
    tool: run_shell
    params:
      cmd: "git rev-parse HEAD"
      cwd: "{{ context.project.root_path }}"

  - id: push
    when: "{{ inputs.push and steps.has_diffs.stdout|contains('changed') }}"
    action: shell_op
    tool: run_shell
    params:
      cmd: "git push"
      cwd: "{{ context.project.root_path }}"

  # 5) Log to ConPort for retrieval (Custom Data → Trace)
  - id: log_trace
    action: conport_op
    tool: log_custom_data
    params:
      workspace_id: "{{ context.workspace_id }}"
      category: "Trace"
      key: "{{ inputs.scope }}"
      value:
        depth: "{{ inputs.depth }}"
        out_dir: "{{ inputs.out_dir }}"
        json_path: "{{ inputs.out_dir }}/trace_{{ inputs.scope|slug }}.json"
        image_path: "{{ (inputs.format in ['svg','png']) and (inputs.out_dir ~ '/trace_' ~ (inputs.scope|slug) ~ '.' ~ inputs.format) or '' }}"
        stats: "{{ steps.build_graph.stats }}"
        commit: "{{ steps.get_hash.stdout|trim }}"

  # 6) Post-patch Active Context
  - id: post_patch
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      active_patch:
        current_focus: "Trace: {{ inputs.scope }}"
        requested_scope: "{{ inputs.scope }}"
        workflow: "trace"
        last_commit: "{{ steps.get_hash.stdout|trim }}"
        last_run: "{{ now_iso() }}"

outputs:
  success:
    status: ok
    message: "Trace generated for '{{ inputs.scope }}' (depth={{ inputs.depth }}) and logged."
```
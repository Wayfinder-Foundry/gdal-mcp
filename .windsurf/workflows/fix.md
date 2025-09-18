---
description: Fix recent implementations idempotently by discovering recent changes, patching Active Context, run quality, and optionally committing and pushing.
---

```yaml
name: fix
description: "Fix recent implementations idempotently: discover recent changes, patch Active Context, run quality, and optionally commit/push."

inputs:
  task:         { type: string, required: true }         # e.g., "address feedback on tabular CLI"
  scope:        { type: string }                          # optional fallback path (file/dir) if no recent changes detected
  recursive:    { type: boolean, default: true }          # recurse if scope is a directory
  since:        { type: string, default: "2.days" }       # time window for recent commits (e.g., "3.hours", "2.days", ISO)
  max_commits:  { type: integer, default: 3 }             # cap how many recent commits to consider
  stage:        { type: boolean, default: true }
  commit:       { type: boolean, default: true }
  push:         { type: boolean, default: false }
  type:         { type: string,  default: "fix" }         # conventional commit type
  scope_commit: { type: string }                          # optional conventional scope
  message:      { type: string,  default: "" }            # commit subject override
  quality_gate:
    type: object
    # Same defaults as /continue, but tuned for fix work (tests strongly encouraged)
    default:
      format: true
      lint: true
      typecheck: true
      tests: true
      coverage_threshold: 0

steps:
  # 1) Environment + context load
  - id: env
    action: Read the contents of the file.
    file: .windsurf/workflows/config/env.md

  - id: load
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/load.md

  # 2) Discover "what I just did"
  # Try to infer targets from recent commits (author = current user if your git MCP supports it).
  # Fallback to 'scope' input if discovery yields nothing.
  - id: recent_commits
    action: git_op
    tool: list_recent_commits
    params:
      cwd: "{{ context.project.root_path or '.' }}"
      since: "{{ inputs.since }}"
      limit: "{{ inputs.max_commits }}"

  - id: changed_files
    when: "{{ steps.recent_commits and steps.recent_commits.items and (steps.recent_commits.items | length) > 0 }}"
    action: git_op
    tool: diff_name_only
    params:
      cwd: "{{ context.project.root_path or '.' }}"
      # Compare the oldest of the selected recent commits to HEAD to scoop up the whole burst of work
      base: "{{ steps.recent_commits.items[-1].hash }}"
      head: "HEAD"

  # Optional filter: respect explicit scope if provided (keeps within a folder/file)
  - id: resolve_targets
    action: system
    output: |
      {% set files = (steps.changed_files and steps.changed_files.files) or [] %}
      {% if inputs.scope %}
      {%   set files = files | select('starts_with', inputs.scope) | list %}
      {% endif %}
      {{ {'files': files} }}

  # 3) Pre-patch Active Context – record intention & targets (idempotent, map not string)
  - id: pre_patch
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      active_patch:
        current_focus: "{{ inputs.task }}"
        workflow: "fix"
        requested_scope: >-
          {{ (inputs.scope or (steps.resolve_targets.files and (steps.resolve_targets.files | length ~ ' files'))) or '' }}
        targets: "{{ steps.resolve_targets.files or [] }}"
        recursive: "{{ inputs.recursive }}"
        last_run: "{{ now_iso() }}"

  # 4) Apply fixes via the same safe dev loop used by /continue, but scoped to discovered files
  # If no discovered files, fall back to 'scope' input or project root (empty string lets the dev loop decide).
  - id: dev
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      run_trace: false
      run_deps: false
      scope: "{{ (steps.resolve_targets.files and (steps.resolve_targets.files | join(' '))) or (inputs.scope or '') }}"
      quality_gate: "{{ inputs.quality_gate }}"
      commit_type: "{{ inputs.type }}"
      commit_scope: "{{ inputs.scope_commit or '' }}"
      commit_subject: "{{ inputs.message or inputs.task }}"
      do_stage: "{{ inputs.stage }}"
      do_commit: "{{ inputs.commit }}"
      do_push: "{{ inputs.push }}"

  # 5) Post-patch Active Context with branch/commit info if we committed anything
  - id: post_patch
    when: "{{ steps.dev and steps.dev.commit_hash }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      active_patch:
        current_focus: "{{ inputs.task }}"
        workflow: "fix"
        requested_scope: >-
          {{ (inputs.scope or (steps.resolve_targets.files and (steps.resolve_targets.files | length ~ ' files'))) or '' }}
        targets: "{{ steps.resolve_targets.files or [] }}"
        branch: "{{ steps.dev.branch }}"
        last_commit: "{{ steps.dev.commit_hash }}"
        last_run: "{{ now_iso() }}"

outputs:
  success:
    status: ok
    message: >-
      Fixed: '{{ inputs.task }}'
      {{ steps.dev and steps.dev.commit_hash and (' @ '+steps.dev.commit_hash[:7]) or '' }}

```
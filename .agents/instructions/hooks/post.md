---
description: Operational finalize run after any top‑level workflow.
---

```yaml
name: postflight
description: |
  Post‑workflow hook:
  - (Optional) Capture a light Git snapshot for auditing
  - Sync ConPort (active/product patches + decisions/progress)
  - (Optional) Log a concise run record into ConPort
  - (Optional) Export a markdown snapshot of ConPort state
  - Emit a deterministic postflight summary

# ----------------------------- Inputs ----------------------------------------
inputs:
  # Prefer the Markdown manifest; fall back is built-in defaults.
  paths_manifest: { type: string, required: false, default: ".windsurf/workflows/config/paths.md" }

  # Directory overrides (win over manifest; otherwise defaults below)
  atoms_conport_dir: { type: string, required: false, default: ".windsurf/workflows/atoms/conport" }
  atoms_git_dir:     { type: string, required: false, default: ".windsurf/workflows/atoms/git" }
  config_dir:        { type: string, required: false, default: ".windsurf/workflows/config" }

  # ConPort sync inputs (all optional; no-ops if empty)
  active_patch:  { type: object, required: false }
  product_patch: { type: object, required: false }
  decisions:     { type: array,  required: false }
  progress:      { type: array,  required: false }

  # Behavior toggles
  capture_git_snapshot: { type: boolean, required: false, default: true }
  log_run_record:       { type: boolean, required: false, default: true }
  export_on_change:     { type: boolean, required: false, default: false }

  # Export options (used only if export_on_change)
  export_path:
    type: string
    required: false
    # Default aligns with export atom default
    default: "{{ context.workspace_id }}/context_portal/export.md"

# ----------------------------- Steps -----------------------------------------
steps:
  - id: announce
    action: system
    output: "[POST] starting finalize"

  # Manifest (optional)
  - id: read_paths_manifest
    action: Read the contents of the file.
    file: "{{ inputs.paths_manifest }}"
    on_error: continue
    output: 
      success: |
        [HOOK:POST] Successfully read the path configurations.
      failure: |
        [HOOK:POST] Failed to read the path configurations.

  - id: parse_paths_manifest
    when: "{{ read_paths_manifest.content }}"
    action: coding_op
    tool: parse_yaml
    params: { yaml: "{{ read_paths_manifest.content }}" }
    output:
      success: |
        [HOOK:POST] Successfully parsed the path configurations.
      failure: |
        [HOOK:POST] Failed to parse the path configurations.

  # Resolve final directories (explicit input > manifest > defaults)
  - id: resolve_paths
    action: system
    output_transform:
      paths:
        atoms_conport: >-
          {{
            inputs.atoms_conport_dir
            or (parse_paths_manifest.result.paths and parse_paths_manifest.result.paths.atoms_conport)
            or ".windsurf/workflows/atoms/conport"
          }}
        atoms_git: >-
          {{
            inputs.atoms_git_dir
            or (parse_paths_manifest.result.paths and parse_paths_manifest.result.paths.atoms_git)
            or ".windsurf/workflows/atoms/git"
          }}
        config: >-
          {{
            inputs.config_dir
            or (parse_paths_manifest.result.paths and parse_paths_manifest.result.paths.config)
            or ".windsurf/workflows/config"
          }}

  # (Optional) Git snapshot for audit/ground truth — only if in a repo
  - id: check_git_dir
    action: fs_op
    tool: list_files
    params: { path: "{{ context.project.root_path }}/.git", recursive: false }
    on_error: { ignore: true }
    output: |
      success: |
        [HOOK:POST] Git repo detected.
      failure: |
        [HOOK:POST] No Git repo detected.

  - id: git_snapshot
    when: "{{ inputs.capture_git_snapshot == true and check_git_dir.files and (check_git_dir.files | length >= 0) }}"
    action: Read the contents of the file.
    file: "{{ steps.resolve_paths.paths.atoms_git }}/sweep.md"
    with:
      repo_path: "{{ context.project.root_path }}"
      max_commits: 6
      context_lines: 2
    output: 
      success: |
        [HOOK:POST] Git repo sweeped
        - {{ git_snapshot.files | join('\n- ') }}
      failure: |
        [HOOK:POST] No Git repo detected.

  # ConPort sync: push patches and lists (no‑ops if inputs are empty)
  - id: conport_sync
    action: Read the contents of the file.
    file: "{{ steps.resolve_paths.paths.atoms_conport }}/sync.md"
    with:
      active_patch:  "{{ inputs.active_patch }}"
      product_patch: "{{ inputs.product_patch }}"
      decisions:     "{{ inputs.decisions | default([]) }}"
      progress:      "{{ inputs.progress  | default([]) }}"
      dry_run:       "{{ inputs.dry_run or false }}"
    output: 
      success: |
        [HOOK:POST] ConPort sync complete
      failure: |
        [HOOK:POST] ConPort sync failed

  # Decide if an export is warranted (changed inputs or detected git deltas)
  - id: should_export
    action: coding_op
    tool: select_if
    params:
      condition: >-
        {{
          inputs.export_on_change and (
            (inputs.decisions and (inputs.decisions | length > 0)) or
            (inputs.progress  and (inputs.progress  | length > 0)) or
            (git_snapshot.snapshot and git_snapshot.snapshot.has_changes == true)
          )
        }}
      then: proceed
      else: skip
    output: |
      success: |
        [HOOK:POST] Export decision: proceed
      failure: |
        [HOOK:POST] Export decision: skip

  - id: export_conport
    when: "{{ steps.should_export.result == 'proceed' }}"
    action: Read the contents of the file.
    file: "{{ steps.resolve_paths.paths.atoms_conport }}/export.md"
    with:
      output_path: "{{ inputs.export_path }}"
    output: 
      success: |
        [HOOK:POST] ConPort export complete
      failure: |
        [HOOK:POST] ConPort export failed

  # Optional: write a concise run record into ConPort (custom category)
  - id: log_post_run
    when: "{{ inputs.log_run_record == true }}"
    action: Read the contents of the file.
    file: "{{ steps.resolve_paths.paths.atoms_conport }}/log.md"
    with:
      custom:
        category: "hooks"
        key: "post.last_run"
        value:
          repo_path: "{{ context.project.root_path }}"
          has_changes: "{{ (git_snapshot.snapshot and git_snapshot.snapshot.has_changes) or false }}"
          decisions_logged: "{{ (inputs.decisions and (inputs.decisions | length)) or 0 }}"
          progress_logged:  "{{ (inputs.progress  and (inputs.progress  | length))  or 0 }}"
          exported: "{{ steps.export_conport and steps.export_conport.path and true or false }}"
          export_path: "{{ steps.export_conport and steps.export_conport.path or null }}"
          timestamp: "{{ now_iso() }}"
    output:
      success: |
        [HOOK:POST] Run record logged
      failure: |
        [HOOK:POST] Failed to log run record

  - id: announce_done
    action: system
    output: "[HOOK:POST] finalize complete"

# ----------------------------- Outputs ---------------------------------------
outputs:
  success:
    status: ok
    message: "Postflight complete"
    postflight:
      git:
        has_snapshot: "{{ inputs.capture_git_snapshot == true and (check_git_dir.files and (check_git_dir.files | length >= 0)) }}"
        has_changes: "{{ (git_snapshot.snapshot and git_snapshot.snapshot.has_changes) or false }}"
        recent_commits: "{{ (git_snapshot.snapshot and git_snapshot.snapshot.recent_commits) or [] }}"
      conport:
        synced: true
        exported: "{{ steps.export_conport and steps.export_conport.path and true or false }}"
        export_path: "{{ steps.export_conport and steps.export_conport.path or null }}"
```

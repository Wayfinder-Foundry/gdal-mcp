```yaml
name: preflight
description: |
  Pre‑workflow hook:
  - Read config (env, verbs) and policies index
  - Initialize-check ConPort (no side effects), then load a light snapshot
  - Load a light Git snapshot (quantitative grounding) if repo present
  - Emit a deterministic preflight summary for downstream steps

# ----------------------------- Inputs ----------------------------------------
inputs:
  # Prefer the Markdown manifest; fall back is built-in defaults.
  paths_manifest: { type: string, required: false, default: ".windsurf/workflows/config/paths.md" }

  # Directory overrides (win over manifest; otherwise defaults below)
  atoms_conport_dir: { type: string, required: false, default: ".windsurf/workflows/atoms/conport" }
  atoms_git_dir:     { type: string, required: false, default: ".windsurf/workflows/atoms/git" }
  config_dir:        { type: string, required: false, default: ".windsurf/workflows/config" }
  policies_dir:      { type: string, required: false, default: ".windsurf/workflows/policies" }

  include_activity:  { type: boolean, required: false, default: true }

  # ConPort limits + recency
  conport_limits:
    type: object
    required: false
    default: { decisions: 3, progress: 5, patterns: 5, glossary: 12 }
  recent_activity:
    type: object
    required: false
    default: { hours_ago: 24, limit_per_type: 3 }

  # Optional quick grounding search
  focus_query: { type: string, required: false }
  focus_limit: { type: integer, required: false, default: 5 }

  # Git sweep window
  git_max_commits:   { type: number, required: false, default: 6 }
  git_context_lines: { type: number, required: false, default: 2 }

# ----------------------------- Steps -----------------------------------------
steps:
  - id: acknowledge
    action: Acknowledge the preflight start.
    output: "[PRE] starting preflight"

  # Manifest (optional). If present, it wins over built-ins.
  - id: read_paths_manifest
    action: Read the contents of the file.
    file: "{{ inputs.paths_manifest }}"
    on_error: continue
    output:
      success: "[HOOK:PRE] read paths manifest"
      failure: "[HOOK:PRE] failed to read paths manifest"

  - id: parse_paths_manifest
    when: "{{ read_paths_manifest.content }}"
    action: coding_op
    tool: parse_yaml
    params: { yaml: "{{ read_paths_manifest.content }}" }
    output: 
      success: "[HOOK:PRE] parsed paths manifest"
      failure: "[HOOK:PRE] failed to parse paths manifest"

  # Resolve directories: explicit input > manifest > defaults
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
        policies: >-
          {{
            inputs.policies_dir
            or (parse_paths_manifest.result.paths and parse_paths_manifest.result.paths.policies)
            or ".windsurf/workflows/policies"
          }}

  # Config + policies
  - id: read_env
    action: Read the contents of the file.
    file: "{{ steps.resolve_paths.paths.config }}/env.md"
    output: 
      success: "[HOOK:PRE] successfully read env configurations"
      failure: "[HOOK:PRE] failed to read env configurations"

  - id: read_policies_index
    action: Read the contents of the file, and the linked markdown files.
    file: "{{ steps.resolve_paths.paths.policies }}/.index.md"
    output: 
      success: "[HOOK:PRE] successfully read policies index"
      failure: "[HOOK:PRE] failed to read policies index"

  - id: env_ping
    action: Report the following message.
    output: 
      success: "[HOOK:PRE] env configurations loaded..."
      failure: "[HOOK:PRE] failed to load env configurations"
      

  - id: policies_ping
    action: Report the following message.
    output: 
      success: "[HOOK:PRE] policies index loaded..."
      failure: "[HOOK:PRE] failed to load policies index"

  # ---------- ConPort: initialize-check (no side effects), then load ----------
  - id: conport_init_check
    action: Read the contents of the file.
    file: "{{ steps.resolve_paths.paths.atoms_conport }}/initialize.md"
    output:
      success: "[HOOK:PRE] Detected initialized ConPort project context"
      failure: "[HOOK:PRE] Failed to detect initialized ConPort project context"
    with:
      init: "no"
      import_brief: "no"
      limits: "{{ inputs.conport_limits }}"
      recent_activity: "{{ inputs.recent_activity }}"

  - id: load_conport
    when: "{{ conport_init_check.conport_status == '[CONPORT_ACTIVE]' }}"
    action: Read the contents of the file.
    file: "{{ steps.resolve_paths.paths.atoms_conport }}/load.md"
    output: 
      success: "[HOOK:PRE] successfully loaded ConPort"
      failure: "[HOOK:PRE] failed to load ConPort"
    with:
      limits: "{{ inputs.conport_limits }}"
      recent_activity: "{{ inputs.recent_activity }}"
      include:
        product: true
        active: true
        decisions: true
        progress: true
        patterns: true
        glossary: true
        activity: "{{ inputs.include_activity }}"

  # Optional quick search to prime focus
  - id: focus_search
    when: "{{ inputs.focus_query }}"
    action: Read the contents of the file.
    file: "{{ steps.resolve_paths.paths.atoms_conport }}/search.md"
    output: 
      success: "[HOOK:PRE] successfully searched for existing ConPort"
      failure: "[HOOK:PRE] failed to search existing ConPort"
    with:
      query: "{{ inputs.focus_query }}"
      limit: "{{ inputs.focus_limit }}"

  # ---------- Git: only if repo present ----------
  - id: check_git_dir
    action: fs_op
    tool: list_files
    output: 
      success: "[HOOK:PRE] detected git repo"
      failure: "[HOOK:PRE] failed to detect git repo"
    params: { path: "{{ context.project.root_path }}/.git", recursive: false }
    on_error: { ignore: true }

  - id: git_sweep
    when: "{{ check_git_dir.files and (check_git_dir.files | length >= 0) }}"
    action: Read the contents of the file.
    output: 
      success: "[HOOK:PRE] successfully swept git repo"
      failure: "[HOOK:PRE] failed to sweep git repo"
    file: "{{ steps.resolve_paths.paths.atoms_git }}/sweep.md"
    with:
      repo_path: "{{ context.project.root_path }}"
      max_commits: "{{ inputs.git_max_commits }}"
      context_lines: "{{ inputs.git_context_lines }}"

  # Summarize
  - id: summarize
    action: system
    output_transform:
      preflight:
        env_ok: true
        verbs_ok: true
        policies_ok: true
        conport:
          status: "{{ conport_init_check.conport_status }}"
          counts:
            decisions: "{{ (load_conport.counts and load_conport.counts.decisions) or 0 }}"
            progress:  "{{ (load_conport.counts and load_conport.counts.progress)  or 0 }}"
            patterns:  "{{ (load_conport.counts and load_conport.counts.patterns)  or 0 }}"
            glossary:  "{{ (load_conport.counts and load_conport.counts.glossary)  or 0 }}"
          current_focus: "{{ (load_conport.active or {}).current_focus or null }}"
          activity_present: >-
            {{
              (load_conport.activity and (load_conport.activity | length > 0))
              and true or false
            }}
          focus_results: "{{ (focus_search.results or []) }}"
        git:
          repo_path: "{{ (git_sweep.snapshot or {}).repo_path or context.project.root_path }}"
          has_changes: "{{ (git_sweep.snapshot or {}).has_changes or false }}"
          recent_commits: "{{ (git_sweep.snapshot or {}).recent_commits or [] }}"
          unstaged_preview: "{{ (git_sweep.snapshot or {}).unstaged_preview or '' }}"
          staged_preview:   "{{ (git_sweep.snapshot or {}).staged_preview   or '' }}"

  - id: advise_if_inactive
    when: "{{ conport_init_check.conport_status == '[CONPORT_INACTIVE]' }}"
    action: system
    output: |
      [HOOK:PRE] ConPort appears inactive/minimal. Consider:
      - initialize: seed Product Context / import brief
      - update:     set Active Context (current_focus, open_issues)
      - log:        seed first decisions/progress/patterns

  - id: done
    action: system
    output: "[PRE] preflight complete"

# ----------------------------- Outputs ---------------------------------------
outputs:
  success:
    status: ok
    message: "Preflight ready"
    preflight: "{{ steps.summarize.preflight }}"
```
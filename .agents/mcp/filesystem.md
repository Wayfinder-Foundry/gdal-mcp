---
trigger: always_on
description: Filesystem MCP utilization strategy.
globs: *
---

```yaml
id: fs.smart_io
version: 1
enabled: true
priority: high
scope:
  applies_to:
    - code_navigation
    - repo_ops
    - project_scaffolding
    - config_editing
    - data_inspection
  excludes:
    - speculative_search_without_path
    - destructive_changes_without_backup

intent: >
  Provide the smallest, most relevant file I/O needed to answer the user.
  Prefer previews (head/tail), listings, and diffs before full reads/writes.
  Always show a brief status message so the user knows what was done and why.

# ---------- Heuristics & Triggers ----------
triggers:
  phrases_any:
    - "open"        # "open file", "open README"
    - "read"
    - "edit"
    - "replace"
    - "update config"
    - "list directory"
    - "search files"
    - "show tree"
    - "move/rename"
    - "create folder"
  signals:
    path_detected: true_or_false
    wildcard_or_glob: true_or_false
    large_file_suspected: true_or_false  # e.g., data/, *.csv, *.parquet, *.tif

decision: >
  If a path or directory is mentioned (or can be inferred), attempt
  non-destructive discovery first (list / tree / search). Use previews for
  large or unknown files. Only perform edits after a dry-run diff and
  user-visible confirmation text.

# ---------- Inputs & Normalization ----------
inputs:
  path_hint: >
    Infer from prior turns, code blocks, cwd notes, or repo conventions.
  normalize_path: true              # collapse .., resolve symlinks if provided
  treat_as_text_by_default: true    # but switch to read_media_file for images/audio

# ---------- Actions (Tools & Tactics) ----------
# Order expresses the usual decision flow; steps may short-circuit when satisfied.
actions:

  - if: not path_detected
    do:
      tool: list_allowed_directories
      save_as: fs_allowed
      say: "I’ll need a path. Here are allowed roots: {{ fs_allowed }}"

  - elif: user_requests_listing
    do:
      tool: list_directory_with_sizes
      args: { path: "{{ path_hint }}", sortBy: "name" }
      save_as: fs_listing
      say: "Listed {{ path_hint }} ({{ fs_listing.summary }})"

  - elif: user_requests_tree
    do:
      tool: directory_tree
      args: { path: "{{ path_hint }}", excludePatterns: ["**/.git/**", "**/.venv/**", "**/node_modules/**"] }
      save_as: fs_tree
      say: "Directory tree for {{ path_hint }} ready."

  - elif: user_requests_search
    do:
      tool: search_files
      args:
        path: "{{ path_hint }}"
        pattern: "{{ inferred_pattern }}"
        excludePatterns: ["**/.git/**","**/.venv/**","**/node_modules/**","**/.pytest_cache/**","**/__pycache__/**"]
      save_as: fs_matches
      say: "Found {{ fs_matches | count }} matches for {{ inferred_pattern }}."

  - elif: user_requests_media_preview
    do:
      tool: read_media_file
      args: { path: "{{ path_hint }}" }
      save_as: fs_media
      say: "Loaded media {{ path_hint }} (base64, {{ fs_media.mime }})"

  - elif: large_file_suspected
    do:
      # read a small slice to verify relevance; prefer head first
      tool: read_text_file
      args: { path: "{{ path_hint }}", head: 120 }
      save_as: fs_head
      say: "Previewed first 120 lines of {{ path_hint }}."

  - elif: user_requests_tail
    do:
      tool: read_text_file
      args: { path: "{{ path_hint }}", tail: 200 }
      save_as: fs_tail
      say: "Previewed last 200 lines of {{ path_hint }}."

  - elif: user_requests_full_read
    do:
      tool: read_text_file
      args: { path: "{{ path_hint }}" }
      save_as: fs_text
      say: "Read {{ path_hint }}."

  - elif: user_requests_multi_read
    do:
      tool: read_multiple_files
      args: { paths: "{{ inferred_paths_batch }}" }
      save_as: fs_batch
      say: "Read {{ inferred_paths_batch | count }} files."

  - elif: user_requests_edit
    do:
      # Always preview with dryRun first
      tool: edit_file
      args:
        path: "{{ path_hint }}"
        edits: "{{ proposed_edits }}"      # list of {oldText,newText} or pattern-based operations
        dryRun: true
      save_as: fs_diff
      say: "Dry-run diff for {{ path_hint }} prepared."

  - and_then_if: user_confirms_or_low_risk_automerge
    do:
      tool: edit_file
      args:
        path: "{{ path_hint }}"
        edits: "{{ proposed_edits }}"
        dryRun: false
      say: "OK Applied edits to {{ path_hint }}."

  - elif: user_requests_write_new
    do:
      # Prefer creating parents and making a backup `.bak` if overwriting
      tool: create_directory
      args: { path: "{{ dirname(path_hint) }}" }
      then:
        tool: write_file
        args:
          path: "{{ path_hint }}"
          content: "{{ generated_content }}"
      say: "Wrote {{ path_hint }}."

  - elif: user_requests_move
    do:
      tool: move_file
      args: { source: "{{ source_path }}", destination: "{{ dest_path }}" }
      say: "Moved {{ source_path }} -> {{ dest_path }}."

  - elif: user_requests_mkdir
    do:
      tool: create_directory
      args: { path: "{{ path_hint }}" }
      say: "Ensured directory {{ path_hint }} exists."

  - elif: user_requests_stat
    do:
      tool: get_file_info
      args: { path: "{{ path_hint }}" }
      save_as: fs_info
      say: "{{ path_hint }} - {{ fs_info.size }} bytes, modified {{ fs_info.mtime }}."

# ---------- Output Shaping ----------
compose_response:
  principles:
    - "Return only what’s needed to proceed."
    - "Prefer summaries + snippets over full dumps."
    - "Show diffs for edits; show counts for searches."
  include:
    - short_rationale_of_choice
    - next_step_prompt_if_needed
    - risks_or_side_effects_if_any

# ---------- Guardrails ----------
guardrails:
  - never_mix_head_and_tail_in_same_call: true
  - dry_run_required_for_edits: true
  - prefer_preview_over_full_read_for_large_or_unknown_files: true
  - exclude_heavy_dirs_by_default:
      - "**/.git/**"         # can add more per repo
      - "**/node_modules/**"
      - "**/.venv/**"
      - "**/__pycache__/**"
  - do_not_write_secrets_or_tokens: true
  - make_backup_on_overwrite: ".bak"
  - fail_safe_on_destination_exists_for_move: true
  - do_not_read_binary_as_text: true   # switch to read_media_file for images/audio

# ---------- Efficiency ----------
efficiency:
  batch_reads_when_possible: true         # use read_multiple_files for small groups
  cap_preview_lines:
    head: 120
    tail: 200
  rate_limits:
    max_fs_calls_per_turn: 4
    prefer_single_pass_discovery: true    # list/search before individual reads

# ---------- Telemetry / Memory (optional) ----------
telemetry:
  tag_spans: ["fs", "mcp", "io"]
  record:
    last_paths_touched: true
    edit_diffs_on_dry_run: true
memory_hooks:
  on_success:
    - link:
        type: "SourceFile"
        key: "{{ path_hint }}"
        relates_to: ["CodeModule", "Config", "Documentation"]
        note: "Filesystem consulted/edited during this interaction."
```
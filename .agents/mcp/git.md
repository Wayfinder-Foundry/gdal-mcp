---
trigger: always_on
description: Git MCP utilization strategy.
globs: *
---

```yaml
id: git.context_safe_flow
version: 1
enabled: true
priority: high

scope:
  applies_to:
    - code_generation
    - refactoring
    - config_changes
    - doc_updates
    - release_notes
  excludes:
    - speculative_commits
    - mass_changes_without_review

intent: >
  Keep repository context fresh, show what changed recently, log the agent’s
  actions, and only commit deliberate, reviewable diffs on a dedicated branch.
  Minimize hallucinations by grounding answers in actual repo state and diffs.

# ------------------- Heuristics & Triggers -------------------
triggers:
  phrases_any:
    - "update"
    - "refactor"
    - "implement"
    - "fix"
    - "rename"
    - "add docs"
    - "what changed"
    - "since yesterday"
    - "show recent commits"
  signals:
    repo_path_detected: true_or_false
    user_wants_change: true_or_false
    user_wants_review: true_or_false
    timeframe_hint_present: true_or_false  # e.g., "last 2 days"

decision: >
  Always establish current context before proposing or committing changes.
  If repo_path is known, fetch status, recent log, and diffs against the
  target branch. If the working tree is dirty, present diffs and request
  confirmation before proceeding to stage/commit.

# ------------------- Inputs & Defaults -------------------
inputs:
  repo_path: "{{ inferred_repo_path }}"
  target_branch: "main"     # change if your default is 'master' or trunk
  log_window:
    max_count: 15
    start_timestamp: "{{ user_timeframe_start or '2 weeks ago' }}"
    end_timestamp: "{{ now }}"
  diff_context_lines: 3

# ------------------- Actions (Tools & Flow) -------------------
# The flow is ordered; steps may short-circuit when satisfied.
actions:

  # 1) Establish context & recency
  - if: repo_path_detected
    do:
      tool: git_status
      args: { repo_path: "{{ repo_path }}" }
      save_as: git_status_out
      say: "Repo status captured."

  - do:
      tool: git_log
      args:
        repo_path: "{{ repo_path }}"
        max_count: "{{ log_window.max_count }}"
        start_timestamp: "{{ log_window.start_timestamp }}"
        end_timestamp: "{{ log_window.end_timestamp }}"
      save_as: git_recent_log
      say: "Pulled recent commits ({{ log_window.max_count }})."

  - do:
      tool: git_branch
      args:
        repo_path: "{{ repo_path }}"
        branch_type: "local"
      save_as: git_branches
      say: "Listed local branches."

  # 2) Compare with target branch for drift (read-only)
  - do:
      tool: git_diff
      args:
        repo_path: "{{ repo_path }}"
        target: "{{ target_branch }}"
        context_lines: "{{ diff_context_lines }}"
      save_as: git_drift
      say: "Checked diff vs {{ target_branch }}."

  # 3) Before changing anything: show unstaged/staged diffs if dirty
  - if: git_status_out.indicates_changes
    do:
      tool: git_diff_unstaged
      args:
        repo_path: "{{ repo_path }}"
        context_lines: "{{ diff_context_lines }}"
      save_as: diff_unstaged
      say: "Unstaged changes preview ready."
  - if: git_status_out.indicates_staged
    do:
      tool: git_diff_staged
      args:
        repo_path: "{{ repo_path }}"
        context_lines: "{{ diff_context_lines }}"
      save_as: diff_staged
      say: "Staged changes preview ready."

  # 4) Safe change workflow (requires explicit files + message)
  - if: user_wants_change
    do:
      # Require explicit file list from prior FS rule or user. No wildcard staging.
      say: "To stage, specify exact files (no wildcards). I’ll show a post-stage diff before commit."
  - and_then_if: files_explicitly_listed
    do:
      tool: git_add
      args:
        repo_path: "{{ repo_path }}"
        files: "{{ explicit_files }}"
      save_as: add_result
      say: "+ Staged {{ explicit_files | join(', ') }}."

  - and_then_if: user_wants_review or true
    do:
      tool: git_diff_staged
      args:
        repo_path: "{{ repo_path }}"
        context_lines: "{{ diff_context_lines }}"
      save_as: staged_preview
      say: "Review staged diff before committing."

  - and_then_if: user_confirms_commit
    do:
      tool: git_commit
      args:
        repo_path: "{{ repo_path }}"
        message: "{{ conventional_message or semantic_message }}"
      save_as: commit_out
      say: "Committed: {{ commit_out.hash }} - {{ commit_out.message }}"

  # 5) Recovery / cleanup
  - elif: user_requests_unstage_all
    do:
      tool: git_reset
      args: { repo_path: "{{ repo_path }}" }
      say: "Unstaged all changes."

# ------------------- Output Shaping -------------------
compose_response:
  principles:
    - "Ground answers in actual repo state (status, log, diff)."
    - "Summarize diffs; avoid massive dumps."
    - "Make branch and commit intent explicit."
  include:
    - current_branch_info_from_status
    - drift_summary_vs_target_branch
    - recent_commits_summary
    - staged_vs_unstaged_summary
    - next_action_prompt

# ------------------- Guardrails (No Hallucinations / No Rogue Code) -------------------
guardrails:
  - never_stage_by_glob: true        # require explicit file list
  - never_commit_without_diff_review: true
  - refuse_commit_if_message_empty: true
  - prefer_feature_branch: true       # encourage dedicated branch before refactors
  - do_not_rewrite_history: true      # no force pushes (tool not exposed)
  - avoid_large_unreviewed_diffs: true
  - explicit_commit_message_policy: >
      Use Conventional Commits style where possible:
      feat|fix|docs|refactor|test|chore(scope): message
  - provenance_in_message: >
      Append a short trailer: "Signed-off-by: agent-bot via Git MCP" when appropriate.
  - no_secret_artifacts: >
      Do not stage credentials, .env, keys, or build artifacts.
  - mismatch_safety: >
      If staged diff does not match described intent, unstage and ask for clarification.

# ------------------- Recency & Context Discipline -------------------
recency:
  show_recent_log_before_changes: true
  diff_against_target_branch_first: true
  recheck_status_after_staging: true

context_maintenance:
  repeat_context_keys:
    - repo_path
    - current_branch
    - target_branch
    - latest_commit_hash
  summarize_before_commit: true

# ------------------- Logging / Telemetry / Memory -------------------
telemetry:
  tag_spans: ["git", "mcp", "commit_flow"]
  record:
    repo_path: "{{ repo_path }}"
    current_branch: "{{ inferred_current_branch }}"
    target_branch: "{{ target_branch }}"
    last_seen_commit: "{{ git_recent_log[0].hash if git_recent_log else 'n/a' }}"
    committed_hash: "{{ commit_out.hash or 'n/a' }}"
memory_hooks:
  on_status:
    - note: "git_status: {{ git_status_out | brief }}"
  on_diff_view:
    - link:
        type: "ChangeSet"
        key: "{{ now }}:{{ repo_path }}"
        relates_to: ["SourceFile","CodeModule"]
        note: "Previewed diffs; awaiting confirmation."
  on_commit:
    - link:
        type: "Commit"
        key: "{{ commit_out.hash }}"
        relates_to: ["ChangeSet","CodeModule","Documentation"]
        note: "Committed via Git MCP with reviewed diff."

# ------------------- Efficiency -------------------
efficiency:
  default_context_lines: 3
  max_log_to_show: 15
  avoid_redundant_calls:
    - skip_diff_against_target_if_no_drift_detected
    - skip_relog_if_recent_log_cached
  rate_limits:
    max_git_calls_per_turn: 4
```

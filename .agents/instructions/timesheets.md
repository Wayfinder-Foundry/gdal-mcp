---
description: Generate evenly distributed daily timesheet blurbs from recent git and ConPort activity.
---

```yaml
name: timesheets
description: >
  Generate evenly distributed daily timesheet blurbs from recent git + ConPort activity.
  Writes/updates {project_root}/timesheet.md idempotently. Optionally blends a prompt.

inputs:
  prompt:   { type: string, default: "" }         # optional narrative hint (e.g., "focus on pipeline + GUI")
  back:     { type: string, default: "5.days" }   # lookback window (e.g., "5.days", "1.week", "10.days")
  days:     { type: integer, default: 5 }         # number of blurbs (work days)
  outfile:  { type: string,  default: "{{ context.project.root_path }}/timesheet.md" }
  dry_run:  { type: boolean, default: false }
  push:     { type: boolean, default: false }

steps:
  # 0) Env + load ConPort context
  - id: env
    action: Read the contents of the file.
    file: .windsurf/workflows/config/env.md

  - id: load
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/load.md

  # 1) Pre-patch Active Context (object-only; never stringified JSON)
  - id: pre_patch_active
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      active_patch:
        current_focus: "Generate timesheets"
        workflow: "timesheets"
        last_run: "{{ now_iso() }}"
        window: "{{ inputs.back }}"
        days: "{{ inputs.days }}"

  # 2) Collect recent work signals ------------------------------------------
  # Git: status + log + diffs over window
  - id: git_status
    action: git_op
    tool: status
    params:
      cwd: "{{ context.project.root_path }}"

  - id: git_log
    action: git_op
    tool: log
    params:
      cwd: "{{ context.project.root_path }}"
      pretty: "format:%H|%ad|%an|%s"
      date: "iso"
      since: "{{ parse_back_to_since_iso(inputs.back) }}"   # helper: “5.days” -> ISO timestamp
      max_count: 500

  - id: git_show_summaries
    action: git_op
    tool: show_many
    when: "{{ steps.git_log and steps.git_log.output }}"
    params:
      cwd: "{{ context.project.root_path }}"
      hashes: "{{ steps.git_log.output | extract_hashes }}"
      patch: false
      name_only: true

  # ConPort: recent activity (decisions, progress, patterns, custom)
  - id: conport_recent
    action: conport_op
    tool: get_recent_activity_summary
    params:
      workspace_id: "{{ context.workspace_id }}"
      hours_ago: "{{ back_to_hours(inputs.back, default_hours=120) }}"
      limit_per_type: 20

  - id: conport_progress
    action: conport_op
    tool: get_progress
    params:
      workspace_id: "{{ context.workspace_id }}"
      limit: 200

  - id: conport_decisions
    action: conport_op
    tool: get_decisions
    params:
      workspace_id: "{{ context.workspace_id }}"
      limit: 100

  # 3) Normalize + aggregate signals
  - id: aggregate_signals
    action: coding_op
    tool: timesheet_collect
    params:
      prompt_hint: "{{ inputs.prompt }}"
      git_status: "{{ steps.git_status }}"
      git_log: "{{ steps.git_log }}"
      git_show: "{{ steps.git_show_summaries }}"
      conport_recent: "{{ steps.conport_recent }}"
      conport_progress: "{{ steps.conport_progress }}"
      conport_decisions: "{{ steps.conport_decisions }}"
      repo_root: "{{ context.project.root_path }}"
      prefer_conventional_commit: true
      # expected: { items: [{type, ts, title, detail, paths[], source}], window: {since, until} }

  # 4) Evenly distribute into N daily blurbs (don’t overfit to exact calendar) 
  - id: synthesize_days
    action: coding_op
    tool: timesheet_distribute
    params:
      items: "{{ steps.aggregate_signals.items }}"
      days: "{{ inputs.days }}"
      window: "{{ steps.aggregate_signals.window }}"
      strategy:
        # Strategy: balance by weight (decisions>progress>commits), spread across days
        weight_decision: 3
        weight_progress: 2
        weight_commit: 1
        group_by_paths: true
        max_bullets_per_day: 6
        tone: "concise, outcome-focused, non-redundant"
        include_paths_example: true
      # expected: { days: [{label, date_hint, bullets[]}], header: {since, until} }

  # 5) Render markdown block (idempotent block per window)
  - id: render_md
    action: coding_op
    tool: render_timesheet_markdown
    params:
      header: "{{ steps.synthesize_days.header }}"
      days: "{{ steps.synthesize_days.days }}"
      project_name: "{{ context.project.id or 'Project' }}"
      footer:
        generated_at: "{{ now_iso() }}"
        sources: ["git","conport"]
      # expected: { block_id, markdown }

  # 6) Write/Update file idempotently (replace block for same window)
  - id: write_file
    action: file_op
    tool: write_or_replace_marked_block
    params:
      path: "{{ inputs.outfile }}"
      start_marker: "<!-- TIMESHEET:{{ steps.render_md.block_id }}:START -->"
      end_marker:   "<!-- TIMESHEET:{{ steps.render_md.block_id }}:END -->"
      content: |
        {{ steps.render_md.markdown }}
      mode: upsert_block   # create file if missing; replace block if exists

  # 7) Commit (optional)
  - id: git_add
    when: "{{ not inputs.dry_run }}"
    action: git_op
    tool: add
    params:
      cwd: "{{ context.project.root_path }}"
      paths: ["{{ inputs.outfile }}"]

  - id: git_commit
    when: "{{ not inputs.dry_run }}"
    action: git_op
    tool: commit
    params:
      cwd: "{{ context.project.root_path }}"
      message: >
        docs(timesheets): update timesheet for {{ steps.synthesize_days.header.since | slice(0,10) }}
        – {{ steps.synthesize_days.header.until | slice(0,10) }}

  - id: git_push
    when: "{{ not inputs.dry_run and inputs.push }}"
    action: git_op
    tool: push
    params:
      cwd: "{{ context.project.root_path }}"

  # 8) Post-patch Active Context with artifact pointer
  - id: post_patch_active
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      active_patch:
        current_focus: "Generated timesheets"
        artifact: "{{ inputs.outfile }}"
        last_run: "{{ now_iso() }}"

outputs:
  success:
    status: ok
    message: >-
      Timesheet generated ({{ inputs.days }} days) from window
      {{ steps.synthesize_days.header.since }} → {{ steps.synthesize_days.header.until }}
      at {{ inputs.outfile }}{{ inputs.dry_run and ' (dry-run)' or '' }}.

```
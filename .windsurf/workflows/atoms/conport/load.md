---
description: Load existing ConPort context from the workspace.
---

```yaml
name: load_conport_atom
description: |
  Load existing ConPort context from the workspace and summarize it.
  Sets status to [CONPORT_ACTIVE] if any context has substance; otherwise [CONPORT_INACTIVE].

inputs:
  limits:
    type: object
    required: false
    default: { decisions: 5, progress: 10, patterns: 10, glossary: 20 }
  recent_activity:
    type: object
    required: false
    # { hours_ago?: int, since_timestamp?: iso-string, limit_per_type?: int }
  include:
    type: object
    required: false
    default: { product: true, active: true, decisions: true, progress: true, patterns: true, glossary: true, activity: true }

steps:
  # --- PRODUCT ---------------------------------------------------------------
  - id: product
    when: "{{ inputs.include.product }}"
    action: conport_op
    tool: get_product_context
    params: { workspace_id: "{{ context.workspace_id }}" }

  # --- ACTIVE ----------------------------------------------------------------
  - id: active
    when: "{{ inputs.include.active }}"
    action: conport_op
    tool: get_active_context
    params: { workspace_id: "{{ context.workspace_id }}" }

  # --- DECISIONS -------------------------------------------------------------
  - id: decisions
    when: "{{ inputs.include.decisions }}"
    action: conport_op
    tool: get_decisions
    params:
      workspace_id: "{{ context.workspace_id }}"
      limit: "{{ inputs.limits.decisions }}"

  # --- PROGRESS --------------------------------------------------------------
  - id: progress
    when: "{{ inputs.include.progress }}"
    action: conport_op
    tool: get_progress
    params:
      workspace_id: "{{ context.workspace_id }}"
      limit: "{{ inputs.limits.progress }}"

  # --- SYSTEM PATTERNS -------------------------------------------------------
  - id: patterns
    when: "{{ inputs.include.patterns }}"
    action: conport_op
    tool: get_system_patterns
    params:
      workspace_id: "{{ context.workspace_id }}"

  # --- GLOSSARY (custom data) ------------------------------------------------
  - id: glossary
    when: "{{ inputs.include.glossary }}"
    action: conport_op
    tool: get_custom_data
    params:
      workspace_id: "{{ context.workspace_id }}"
      category: "ProjectGlossary"

  # --- RECENT ACTIVITY SUMMARY ----------------------------------------------
  - id: activity
    when: "{{ inputs.include.activity }}"
    action: conport_op
    tool: get_recent_activity_summary
    params:
      workspace_id: "{{ context.workspace_id }}"
      hours_ago: "{{ inputs.recent_activity.hours_ago or null }}"
      since_timestamp: "{{ inputs.recent_activity.since_timestamp or null }}"
      limit_per_type: "{{ inputs.recent_activity.limit_per_type or 5 }}"

  # --- AGGREGATE + STATUS ----------------------------------------------------
  - id: aggregate
    action: system
    output_transform:
      summary:
        product_present: "{{ steps.product.content and (steps.product.content | length > 0) }}"
        active_present: "{{ steps.active.content and (steps.active.content | length > 0) }}"
        decisions_count: "{{ (steps.decisions.results or []) | length }}"
        progress_count: "{{ (steps.progress.results or []) | length }}"
        patterns_count: "{{ (steps.patterns.results or []) | length }}"
        glossary_count: "{{ (steps.glossary.results or []) | length }}"
        activity_present: "{{ steps.activity.summary and (steps.activity.summary | length > 0) }}"
      status: >-
        {{
          (
            (steps.product.content and steps.product.content | length > 0) or
            (steps.active.content and steps.active.content | length > 0) or
            ((steps.decisions.results or []) | length > 0) or
            ((steps.progress.results or []) | length > 0) or
            ((steps.patterns.results or []) | length > 0) or
            ((steps.glossary.results or []) | length > 0)
          )
          and '[CONPORT_ACTIVE]'
          or '[CONPORT_INACTIVE]'
        }}

  - id: advise_if_empty
    when: "{{ steps.aggregate.status == '[CONPORT_INACTIVE]' }}"
    action: system
    output: |
      ConPort database present but appears empty/minimal.
      Consider running:
      - initialize → import brief.md or define Product Context
      - update    → set Active Context (current_focus, open_issues)
      - log       → seed first decisions/progress/patterns

outputs:
  success:
    status: ok
    conport_status: "{{ steps.aggregate.status }}"
    counts:
      decisions: "{{ steps.aggregate.summary.decisions_count }}"
      progress:  "{{ steps.aggregate.summary.progress_count }}"
      patterns:  "{{ steps.aggregate.summary.patterns_count }}"
      glossary:  "{{ steps.aggregate.summary.glossary_count }}"
    product:  "{{ steps.product.content or {} }}"
    active:   "{{ steps.active.content or {} }}"
    decisions: "{{ steps.decisions.results or [] }}"
    progress:  "{{ steps.progress.results or [] }}"
    patterns:  "{{ steps.patterns.results or [] }}"
    glossary:  "{{ steps.glossary.results or [] }}"
    activity:  "{{ steps.activity.summary or {} }}"
    message: >-
      Loaded ConPort context → {{ steps.aggregate.status }}.
  failure:
    status: failed
    message: "ConPort context load failed."
```
---
description: Log new items into ConPort.
---

```yaml
name: log_conport_atom
description: |
  Log new items into ConPort (decisions, progress, patterns, custom data).
  Safe & idempotent: previews → optional confirm → dedupe → write.

inputs:
  decision:
    type: object
    required: false
    # { summary: str (req), rationale?: str, implementation_details?: str, tags?: [str] }
  progress:
    type: object
    required: false
    # { description: str (req), status?: 'TODO'|'IN_PROGRESS'|'DONE',
    #   parent_id?: int,
    #   linked_item_type?: str, linked_item_id?: str, link_relationship_type?: str }
  pattern:
    type: object
    required: false
    # { name: str (req), description?: str, tags?: [str] }
  custom:
    type: object
    required: false
    # { category: str (req), key: str (req), value: any (req) }
  auto_confirm:
    type: boolean
    required: false
    default: false

steps:
  # ========================= DECISION =========================
  - id: preview_decision
    when: "{{ inputs.decision and inputs.decision.summary }}"
    action: system
    output: |
      [DECISION PREVIEW]
      summary: {{ inputs.decision.summary }}
      rationale: {{ inputs.decision.rationale or '—' }}
      tags: {{ (inputs.decision.tags or []) | join(', ') }}

  - id: confirm_decision
    when: "{{ inputs.decision and inputs.decision.summary and not inputs.auto_confirm }}"
    action: user
    description: "Confirm logging this decision."

  - id: check_existing_decision
    when: "{{ inputs.decision and (inputs.auto_confirm or confirm_decision.approved) }}"
    action: conport_op
    tool: search_decisions_fts
    params:
      workspace_id: "{{ context.workspace_id }}"
      query_term: "{{ inputs.decision.summary }}"
      limit: 5

  - id: dedupe_decision
    when: "{{ inputs.decision and (inputs.auto_confirm or confirm_decision.approved) }}"
    action: coding_op
    tool: select_if
    params:
      condition: "{{ steps.check_existing_decision.results | any(lambda d: (d.summary or '') | lower == (inputs.decision.summary | lower)) }}"
      then: skip
      else: proceed

  - id: log_decision
    when: "{{ inputs.decision and (inputs.auto_confirm or confirm_decision.approved) and steps.dedupe_decision.result == 'proceed' }}"
    action: conport_op
    tool: log_decision
    params:
      workspace_id: "{{ context.workspace_id }}"
      summary: "{{ inputs.decision.summary }}"
      rationale: "{{ inputs.decision.rationale or '' }}"
      implementation_details: "{{ inputs.decision.implementation_details or '' }}"
      tags: "{{ inputs.decision.tags or [] }}"

  # ========================= PROGRESS =========================
  - id: preview_progress
    when: "{{ inputs.progress and inputs.progress.description }}"
    action: system
    output: |
      [PROGRESS PREVIEW]
      description: {{ inputs.progress.description }}
      status: {{ inputs.progress.status or 'IN_PROGRESS' }}

  - id: confirm_progress
    when: "{{ inputs.progress and inputs.progress.description and not inputs.auto_confirm }}"
    action: user
    description: "Confirm logging this progress entry."

  - id: find_progress
    when: "{{ inputs.progress and (inputs.auto_confirm or confirm_progress.approved) }}"
    action: conport_op
    tool: get_progress
    params:
      workspace_id: "{{ context.workspace_id }}"
      limit: 100

  - id: progress_existing
    when: "{{ inputs.progress and (inputs.auto_confirm or confirm_progress.approved) }}"
    action: coding_op
    tool: select_first
    params:
      items: "{{ steps.find_progress.results or [] }}"
      where: "{{ (item.description or '') | lower == (inputs.progress.description | lower) }}"

  # Branch A: update existing (if found)
  - id: update_progress
    when: "{{ inputs.progress and progress_existing.item }}"
    action: conport_op
    tool: update_progress
    params:
      workspace_id: "{{ context.workspace_id }}"
      progress_id: "{{ steps.progress_existing.item.id }}"
      description: "{{ inputs.progress.description }}"
      # status optional; include if provided
      {% raw %}{{ inputs.progress.status and 'status: \"' ~ inputs.progress.status ~ '\"' or '' }}{% endraw %}
      # optional relationships if provided:
      {% raw %}{{ inputs.progress.parent_id and 'parent_id: ' ~ inputs.progress.parent_id or '' }}{% endraw %}
      {% raw %}{{ inputs.progress.linked_item_type and 'linked_item_type: \"' ~ inputs.progress.linked_item_type ~ '\"' or '' }}{% endraw %}
      {% raw %}{{ inputs.progress.linked_item_id and 'linked_item_id: \"' ~ inputs.progress.linked_item_id ~ '\"' or '' }}{% endraw %}
      {% raw %}{{ inputs.progress.link_relationship_type and 'link_relationship_type: \"' ~ inputs.progress.link_relationship_type ~ '\"' or '' }}{% endraw %}

  # Branch B: log new if none found
  - id: log_progress
    when: "{{ inputs.progress and not progress_existing.item }}"
    action: conport_op
    tool: log_progress
    params:
      workspace_id: "{{ context.workspace_id }}"
      description: "{{ inputs.progress.description }}"
      status: "{{ inputs.progress.status or 'IN_PROGRESS' }}"
      {% raw %}{{ inputs.progress.parent_id and 'parent_id: ' ~ inputs.progress.parent_id or '' }}{% endraw %}
      {% raw %}{{ inputs.progress.linked_item_type and 'linked_item_type: \"' ~ inputs.progress.linked_item_type ~ '\"' or '' }}{% endraw %}
      {% raw %}{{ inputs.progress.linked_item_id and 'linked_item_id: \"' ~ inputs.progress.linked_item_id ~ '\"' or '' }}{% endraw %}
      {% raw %}{{ inputs.progress.link_relationship_type and 'link_relationship_type: \"' ~ inputs.progress.link_relationship_type ~ '\"' or '' }}{% endraw %}

  # ========================= PATTERN =========================
  - id: preview_pattern
    when: "{{ inputs.pattern and inputs.pattern.name }}"
    action: system
    output: |
      [PATTERN PREVIEW]
      name: {{ inputs.pattern.name }}
      tags: {{ (inputs.pattern.tags or []) | join(', ') }}

  - id: confirm_pattern
    when: "{{ inputs.pattern and inputs.pattern.name and not inputs.auto_confirm }}"
    action: user
    description: "Confirm logging this system pattern."

  - id: get_patterns
    when: "{{ inputs.pattern and (inputs.auto_confirm or confirm_pattern.approved) }}"
    action: conport_op
    tool: get_system_patterns
    params:
      workspace_id: "{{ context.workspace_id }}"

  - id: dedupe_pattern
    when: "{{ inputs.pattern and (inputs.auto_confirm or confirm_pattern.approved) }}"
    action: coding_op
    tool: select_if
    params:
      condition: "{{ (steps.get_patterns.results or []) | any(lambda p: (p.name or '') | lower == (inputs.pattern.name | lower)) }}"
      then: skip
      else: proceed

  - id: log_pattern
    when: "{{ inputs.pattern and (inputs.auto_confirm or confirm_pattern.approved) and steps.dedupe_pattern.result == 'proceed' }}"
    action: conport_op
    tool: log_system_pattern
    params:
      workspace_id: "{{ context.workspace_id }}"
      name: "{{ inputs.pattern.name }}"
      description: "{{ inputs.pattern.description or '' }}"
      tags: "{{ inputs.pattern.tags or [] }}"

  # ========================= CUSTOM DATA =========================
  - id: preview_custom
    when: "{{ inputs.custom and inputs.custom.category and inputs.custom.key }}"
    action: system
    output: |
      [CUSTOM PREVIEW]
      category: {{ inputs.custom.category }}
      key: {{ inputs.custom.key }}

  - id: confirm_custom
    when: "{{ inputs.custom and inputs.custom.category and inputs.custom.key and not inputs.auto_confirm }}"
    action: user
    description: "Confirm logging this custom data entry."

  - id: get_category_data
    when: "{{ inputs.custom and (inputs.auto_confirm or confirm_custom.approved) }}"
    action: conport_op
    tool: get_custom_data
    params:
      workspace_id: "{{ context.workspace_id }}"
      category: "{{ inputs.custom.category }}"

  - id: existing_custom
    when: "{{ inputs.custom and (inputs.auto_confirm or confirm_custom.approved) }}"
    action: coding_op
    tool: select_first
    params:
      items: "{{ steps.get_category_data.results or [] }}"
      where: "{{ (item.key or '') | lower == (inputs.custom.key | lower) }}"

  # Prefer an upsert if your MCP supports it; otherwise update-or-log.
  - id: upsert_custom
    when: "{{ inputs.custom and (inputs.auto_confirm or confirm_custom.approved) }}"
    action: conport_op
    tool: upsert_custom_data
    params:
      workspace_id: "{{ context.workspace_id }}"
      category: "{{ inputs.custom.category }}"
      key: "{{ inputs.custom.key }}"
      value: "{{ inputs.custom.value | tojson }}"

outputs:
  success:
    status: ok
    message: >-
      Logged:
      {{ inputs.decision and 'decision ' or '' }}
      {{ inputs.progress and 'progress ' or '' }}
      {{ inputs.pattern and 'pattern ' or '' }}
      {{ inputs.custom and 'custom ' or '' }}
    decision_id: "{{ steps.log_decision.id or null }}"
    progress_id: "{{ (steps.update_progress.progress_id or steps.log_progress.progress_id) or null }}"
    pattern_id: "{{ steps.log_pattern.id or null }}"
    custom_key: "{{ inputs.custom and inputs.custom.key or null }}"
```
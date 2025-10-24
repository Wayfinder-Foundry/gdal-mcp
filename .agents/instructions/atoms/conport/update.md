```yaml
# Include with:
#   action: Read the contents of the file.
#   file: .windsurf/workflows/atoms/conport/update.md
#   with:
#     active_patch:  { ... }        # optional map
#     product_patch: { ... }        # optional map
#     decision:      { summary: "...", rationale: "...", tags: [...] }  # optional
#     progress:      { description: "...", status: "IN_PROGRESS" }      # optional
name: update_conport_atom
description: |
  Safe, idempotent ConPort updates. Normalizes incoming patches so that
  `content`/`patch_content` are always OBJECTs (never JSON strings).
  This guards against template engines that stringify booleans/objects.

inputs:
  active_patch:  { type: object }
  product_patch: { type: object }
  decision:
    type: object
    properties:
      summary: { type: string }
      rationale: { type: string }
      implementation_details: { type: string }
      tags: { type: array }
  progress:
    type: object
    properties:
      description: { type: string }
      status: { type: string }
  dry_run:
    type: boolean
    required: false
    default: false

steps:
  # ---------- Normalize patches (string → object if needed) ----------
  - id: normalize_active_patch
    when: "{{ inputs.active_patch }}"
    action: coding_op
    tool: coerce_json_like_to_object
    params_json:
      value: "{{ inputs.active_patch }}"

  - id: normalize_product_patch
    when: "{{ inputs.product_patch }}"
    action: coding_op
    tool: coerce_json_like_to_object
    params_json:
      value: "{{ inputs.product_patch }}"

  # ---------- Active Context (merge → content) ----------
  - id: load_active
    when: "{{ inputs.active_patch }}"
    action: conport_op
    tool: get_active_context
    params_json: { workspace_id: "{{ context.workspace_id }}" }

  - id: merge_active
    when: "{{ inputs.active_patch }}"
    action: coding_op
    tool: merge_objects
    params_json:
      base:  "{{ steps.load_active.content or {} }}"
      patch: "{{ steps.normalize_active_patch.result }}"

  - id: update_active
    when: "{{ inputs.active_patch and inputs.dry_run != true }}"
    action: conport_op
    tool: update_active_context
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      content: "{{ steps.merge_active.result }}"   # final OBJECT

  # ---------- Product Context (merge → content) ----------
  - id: load_product
    when: "{{ inputs.product_patch }}"
    action: conport_op
    tool: get_product_context
    params_json: { workspace_id: "{{ context.workspace_id }}" }

  - id: merge_product
    when: "{{ inputs.product_patch }}"
    action: coding_op
    tool: merge_objects
    params_json:
      base:  "{{ steps.load_product.content or {} }}"
      patch: "{{ steps.normalize_product_patch.result }}"

  - id: update_product
    when: "{{ inputs.product_patch and inputs.dry_run != true }}"
    action: conport_op
    tool: update_product_context
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      content: "{{ steps.merge_product.result }}"

  # ---------- Decision logging (unchanged) ----------
  - id: confirm_decision
    when: "{{ inputs.decision and inputs.decision.summary }}"
    action: system
    say: |
      Log decision?
      summary: {{ inputs.decision.summary }}
      rationale: {{ inputs.decision.rationale or '—' }}
      tags: {{ (inputs.decision.tags or []) | tojson }}

  - id: search_decisions
    when: "{{ inputs.decision and inputs.decision.summary }}"
    action: conport_op
    tool: search_decisions_fts
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      limit: 3
      query_term: "{{ inputs.decision.summary }}"

  - id: log_decision
    when: "{{ inputs.decision and inputs.decision.summary and inputs.dry_run != true and ((not steps.search_decisions.results) or ((steps.search_decisions.results | length) == 0)) }}"
    action: conport_op
    tool: log_decision
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      summary: "{{ inputs.decision.summary }}"
      rationale: "{{ inputs.decision.rationale or '' }}"
      implementation_details: "{{ inputs.decision.implementation_details or '' }}"
      tags: "{{ inputs.decision.tags or [] }}"

  # ---------- Progress (unchanged) ----------
  - id: find_progress
    when: "{{ inputs.progress and inputs.progress.description }}"
    action: conport_op
    tool: get_progress
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      limit: 100
    output_transform:
      existing: "{{ find_progress_for_task(outputs, inputs.progress.description) }}"

  - id: update_progress
    when: "{{ inputs.progress and steps.find_progress.existing and inputs.dry_run != true }}"
    action: conport_op
    tool: update_progress
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      progress_id: "{{ steps.find_progress.existing.id }}"
      description: "{{ inputs.progress.description }}"
      {% raw %}{{ inputs.progress.status and 'status: "' ~ inputs.progress.status ~ '"' or '' }}{% endraw %}

  - id: log_progress
    when: "{{ inputs.progress and not steps.find_progress.existing and inputs.dry_run != true }}"
    action: conport_op
    tool: log_progress
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      status: "{{ inputs.progress.status or 'IN_PROGRESS' }}"
      description: "{{ inputs.progress.description }}"

  # ---------- Type assertions (optional but helpful) ----------
  - id: assert_types
    when: "{{ inputs.active_patch or inputs.product_patch }}"
    action: coding_op
    tool: assert_multiple_objects
    params_json:
      objects:
        - { name: "active_patch",  value: "{{ steps.normalize_active_patch and steps.normalize_active_patch.result or {} }}" }
        - { name: "product_patch", value: "{{ steps.normalize_product_patch and steps.normalize_product_patch.result or {} }}" }
```
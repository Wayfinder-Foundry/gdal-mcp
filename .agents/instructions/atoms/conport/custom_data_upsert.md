---
description: Upsert a single ConPort custom data entry with idempotency, merge options, and dry-run support.
---

```yaml
name: custom_data_upsert
description: |
  Upsert a single custom data item into ConPort's Custom Data store.
  - Idempotent: reads existing value first and optionally merges
  - Merge strategies: replace (default) or deep_merge
  - Dry-run: preview changes without mutation

inputs:
  category: { type: string, required: true }
  key:       { type: string, required: true }
  value:
    type: any
    required: true
    description: JSON-serializable object or JSON string. Will be coerced to object.
  merge_strategy:
    type: string
    required: false
    default: "replace"    # one of: replace | deep_merge
  dry_run:
    type: boolean
    required: false
    default: false
  tags:
    type: array
    required: false
    description: Optional tags to embed into value.meta.tags
  source_path:
    type: string
    required: false
    description: Optional source file path to embed into value.meta.source

steps:
  # Normalize incoming value into an OBJECT
  - id: normalize_value
    action: coding_op
    tool: coerce_json_like_to_object
    params_json:
      value: "{{ inputs.value }}"

  # Optionally enrich with meta tags/source
  - id: add_meta
    when: "{{ inputs.tags or inputs.source_path }}"
    action: coding_op
    tool: merge_objects
    params_json:
      base:  "{{ steps.normalize_value.result or {} }}"
      patch:
        meta:
          {{ inputs.tags and ('tags: ' ~ (inputs.tags | tojson)) or '' }}
          {{ inputs.source_path and ('source: "' ~ inputs.source_path ~ '"') or '' }}

  # Load any existing entry for category+key
  - id: get_existing
    action: conport_op
    tool: get_custom_data
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      category: "{{ inputs.category }}"
      key: "{{ inputs.key }}"

  # Decide final value based on merge strategy
  - id: decide_value
    action: coding_op
    tool: merge_objects
    params_json:
      base:  "{{ (inputs.merge_strategy == 'deep_merge' and (steps.get_existing and steps.get_existing.value or {})) or {} }}"
      patch: "{{ (steps.add_meta and steps.add_meta.result) or steps.normalize_value.result or {} }}"

  # Preview change (diff-like) when dry-run
  - id: preview
    when: "{{ inputs.dry_run }}"
    action: system
    say: |
      [CUSTOM_DATA_PREVIEW]
      category: {{ inputs.category }}
      key: {{ inputs.key }}
      existed: {{ steps.get_existing and (steps.get_existing.value != null) }}
      merge_strategy: {{ inputs.merge_strategy }}
      old_value: {{ (steps.get_existing and (steps.get_existing.value or {})) | tojson }}
      new_value: {{ steps.decide_value.result | tojson }}

  # Perform upsert when not dry-run
  - id: upsert
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: log_custom_data
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      category: "{{ inputs.category }}"
      key: "{{ inputs.key }}"
      value: "{{ steps.decide_value.result }}"

outputs:
  success:
    status: ok
    category: "{{ inputs.category }}"
    key:      "{{ inputs.key }}"
    dry_run:  "{{ inputs.dry_run }}"
    existed:  "{{ steps.get_existing and (steps.get_existing.value != null) }}"
    value:    "{{ steps.decide_value.result }}"
```

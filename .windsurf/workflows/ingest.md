---
description: Ingest a single custom data item into ConPort with idempotent upsert and preserve_focus.
---

```yaml
name: ingest
description: |
  Ingest a single, structured item into ConPort Custom Data using an idempotent upsert atom.
  - Preflight: env/policies + ConPort grounding
  - Upsert: atoms/conport/custom_data_upsert.md with optional deep-merge and meta tags/source
  - Postflight: progress logging, export, preserve current focus by default

inputs:
  category: { type: string, required: true }
  key:       { type: string, required: true }
  value:     { type: any,    required: true,  description: "JSON-serializable object or JSON string" }
  merge_strategy: { type: string, required: false, default: "replace" }   # replace | deep_merge
  tags:      { type: array,  required: false, default: ["workflow:ingestion"] }
  source_path: { type: string, required: false }

  pre_opts:  { type: object, required: false, default: {} }
  post_opts:
    type: object
    required: false
    default: { capture_git_snapshot: true, log_run_record: true, export_on_change: true, preserve_focus: true }

  dry_run: { type: boolean, required: false, default: false }

steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"

  # ---------- Upsert custom data ----------
  - id: upsert
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/custom_data_upsert.md
    with:
      category: "{{ inputs.category }}"
      key: "{{ inputs.key }}"
      value: "{{ inputs.value }}"
      merge_strategy: "{{ inputs.merge_strategy }}"
      dry_run: "{{ inputs.dry_run }}"
      tags: "{{ inputs.tags }}"
      source_path: "{{ inputs.source_path }}"

  # ---------- Prepare progress payload for postflight ----------
  - id: progress_payload
    action: system
    output_transform:
      progress:
        - description: >-
            Ingested custom data — {{ inputs.category }}.{{ inputs.key }}
            {{ inputs.dry_run and '(dry-run)' or '' }}
          status: "{{ inputs.dry_run and 'IN_PROGRESS' or 'DONE' }}"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.progress_payload.progress }}"
      dry_run: "{{ inputs.dry_run }}"
      {% raw %}{% if inputs.post_opts and inputs.post_opts.preserve_focus %}{% endraw %}
      active_patch:
        requested_scope: "{{ inputs.category }}.{{ inputs.key }}"
        workflow: "ingest"
        last_run: "{{ now_iso() }}"
      {% raw %}{% else %}{% endraw %}
      active_patch:
        current_focus: "ConPort ingestion"
        requested_scope: "{{ inputs.category }}.{{ inputs.key }}"
        workflow: "ingest"
        last_run: "{{ now_iso() }}"
      {% raw %}{% endif %}{% endraw %}
      {{ inputs.post_opts | tojson }}

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: >-
      Ingest complete — category={{ inputs.category }}, key={{ inputs.key }}, dry_run={{ inputs.dry_run }}.
```

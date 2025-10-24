---
description: Retrieve information from ConPort.
---

```yaml
name: search_conport_atom
description: |
  Retrieve information from ConPort using FTS or semantic search.
  Selects the right tool based on query type and ensures concise results.
  Designed to be idempotent: repeated queries yield the same results.

inputs:
  query:
    type: string
    required: true
    description: Natural language or keyword search string
  type:
    type: string
    required: false
    description: |
      Search target: one of [decisions, custom, glossary, semantic].
      Defaults to semantic if not provided.
  limit:
    type: integer
    required: false
    default: 5
    description: Max number of results to return

steps:
  - id: route
    action: system
    description: "Determine search type (decisions, custom, glossary, semantic)."
    output: "{{ inputs.type | default('semantic') }}"

  - id: search_decisions
    when: "{{ steps.route.output == 'decisions' }}"
    action: conport_op
    tool: search_decisions_fts
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      query: "{{ inputs.query }}"
      limit: "{{ inputs.limit }}"

  - id: search_custom
    when: "{{ steps.route.output == 'custom' }}"
    action: conport_op
    tool: search_custom_data_value_fts
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      query: "{{ inputs.query }}"
      limit: "{{ inputs.limit }}"

  - id: search_glossary
    when: "{{ steps.route.output == 'glossary' }}"
    action: conport_op
    tool: search_project_glossary_fts
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      query: "{{ inputs.query }}"
      limit: "{{ inputs.limit }}"

  - id: search_semantic
    when: "{{ steps.route.output == 'semantic' }}"
    action: conport_op
    tool: semantic_search_conport
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      query: "{{ inputs.query }}"
      limit: "{{ inputs.limit }}"

  - id: summarize
    action: coding_op
    tool: summarize_results
    params:
      results: >-
        {{ steps.search_decisions.output
           or steps.search_custom.output
           or steps.search_glossary.output
           or steps.search_semantic.output }}
      style: concise

outputs:
  success:
    status: ok
    message: "Search completed for '{{ inputs.query }}'"
    results: "{{ steps.summarize.output }}"
```
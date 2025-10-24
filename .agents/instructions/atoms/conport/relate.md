---
description: Create relationships between ConPort items.
---

```yaml
name: link_conport_atom
description: |
  Create relationships between ConPort items.
  Designed to be idempotent and user-confirmed before changes.

inputs:
  source:
    type: string
    required: true
    description: The ID or name of the source item
  target:
    type: string
    required: true
    description: The ID or name of the target item
  relation_type:
    type: string
    required: false
    default: related_to
    description: |
      Relationship type. Common options: implements, depends_on,
      blocks, clarifies, related_to.
  description:
    type: string
    required: false
    description: Optional human-readable note about this relationship
  auto_confirm:
    type: boolean
    required: false
    default: false
    description: |
      Whether to skip user confirmation and link directly.

steps:
  - id: propose
    action: system
    description: "Propose link and wait for confirmation if auto_confirm is false."
    output: |
      Proposed: {{ inputs.source }} --({{ inputs.relation_type }})--> {{ inputs.target }}
      {{ inputs.description or '' }}

  - id: confirm
    when: "{{ not inputs.auto_confirm }}"
    action: user
    description: "Ask user for confirmation before creating the link."

  - id: create_link
    when: "{{ inputs.auto_confirm or confirm.approved }}"
    action: conport_op
    tool: link_conport_items
    params_json:
      workspace_id: "{{ context.workspace_id }}"
      source: "{{ inputs.source }}"
      target: "{{ inputs.target }}"
      relationType: "{{ inputs.relation_type }}"
      description: "{{ inputs.description | default('') }}"

  - id: notify
    when: "{{ create_link.success }}"
    action: system
    description: "Signal that the link has been created."
    output: "[CONPORT_LINKED] {{ inputs.source }} → {{ inputs.target }}"

outputs:
  success:
    status: ok
    message: "Link created successfully."
    relation: "{{ steps.create_link.output }}"
  failure:
    status: failed
    message: "Link not created."

```
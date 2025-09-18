---
description: Bootstrap the contextual framework to a new or existing project.
---

```yaml
name: bootstrap
description: |
  Mid-project (or fresh) bootstrap:
  - Preflight to load env/policies and take light ConPort/Git snapshots
  - Initialize ConPort (idempotent) and optionally install dependencies
  - Load contexts to verify state
  - Sync recent Git activity into ConPort (progress + active patch)
  - Postflight to sync/log/export as configured

inputs:
  since:
    type: string
    required: false
    default: "14.days"        # e.g., 7.days, 2.weeks, 1.month
  install_deps:
    type: boolean
    required: false
    default: false            # if true, delegate to initialize_atom's install routine
  dry_run:
    type: boolean
    required: false
    default: false            # show planned actions without mutating ConPort
  pre_opts:
    type: object
    required: false
    default: {}               # pass-through to preflight
  post_opts:
    type: object
    required: false
    default: { capture_git_snapshot: true, log_run_record: true, export_on_change: true, preserve_focus: true }

steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"

  # ---------- Initialize ConPort (idempotent) ----------
  - id: initialize_conport
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/initialize.md
    with:
      dry_run: "{{ inputs.dry_run }}"
      install_deps: "{{ inputs.install_deps }}"

  # ---------- Load to verify/reflect current state ----------
  - id: load_conport
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/load.md

  # ---------- Sweep recent Git into ConPort ----------
  - id: sync_conport
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/sync.md

  # ---------- Prepare progress payload for postflight ----------
  - id: progress_payload
    when: "{{ inputs.dry_run != true }}"
    action: system
    output_transform:
      progress:
        - description: >-
            Bootstrap: initialize={{ not inputs.dry_run }}; since={{ inputs.since }};
            deps={{ inputs.install_deps }}; conport_status={{ steps.load_conport.conport_status or 'unknown' }}
          status: "DONE"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ (steps.progress_payload and steps.progress_payload.progress) or [] }}"
      dry_run: "{{ inputs.dry_run }}"
      {% raw %}{% if inputs.post_opts and inputs.post_opts.preserve_focus %}{% endraw %}
      active_patch:
        workflow: "bootstrap"
        last_run: "{{ now_iso() }}"
      {% raw %}{% else %}{% endraw %}
      active_patch:
        current_focus: "Bootstrap"
        workflow: "bootstrap"
        last_run: "{{ now_iso() }}"
      {% raw %}{% endif %}{% endraw %}
      {{ inputs.post_opts | tojson }}

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: >-
      ConPort bootstrap complete (since={{ inputs.since }}, install_deps={{ inputs.install_deps }},
      dry_run={{ inputs.dry_run }}).
```
```yaml
name: initialize_conport_atom
description: |
  Establish ConPort memory status for the current workspace and load context.
  - Detects DB presence at <workspace>/context_portal/context.db
  - If present → loads key context and marks [CONPORT_ACTIVE]
  - If absent  → (optionally) bootstrap and import brief.md, else mark [CONPORT_INACTIVE]
  - Always returns a concise summary for downstream chains

inputs:
  init:
    type: string
    required: false
    default: ask     # one of: ask|yes|no
    description: "'ask' to prompt the user; 'yes' to initialize automatically; 'no' to skip."
  import_brief:
    type: string
    required: false
    default: ask     # one of: ask|yes|no
    description: "Whether to import brief.md into Product Context on first init."
  brief_path:
    type: string
    required: false
    default: ".windsurf/workflows/config/brief.md"
  limits:
    type: object
    required: false
    default: { decisions: 5, progress: 5, patterns: 5, glossary: 50 }
  recent_activity:
    type: object
    required: false
    default: { hours_ago: 24, limit_per_type: 3 }

steps:
  # 1) Resolve workspace paths
  - id: paths
    action: system
    output_transform:
      portal_dir: "{{ context.workspace_id }}/context_portal"
      db_path:    "{{ context.workspace_id }}/context_portal/context.db"

  # 2) Check for existing DB
  - id: list_portal
    action: fs_op
    tool: list_files
    params: { path: "{{ steps.paths.portal_dir }}", recursive: false }
    on_error: { ignore: true }

  - id: detect_db
    action: system
    output_transform:
      has_db: "{{ steps.list_portal.files and (steps.list_portal.files | map(attribute='name') | list) | contains('context.db') }}"

  # 3) If DB exists → load context now (ACTIVE)
  - id: load_if_active
    when: "{{ steps.detect_db.has_db == true }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/load.md
    with:
      limits: "{{ inputs.limits }}"
      recent_activity: "{{ inputs.recent_activity }}"
      include:
        product: true
        active:  true
        decisions: true
        progress:  true
        patterns:  true
        glossary:  true
        activity:  true

  - id: mark_active
    when: "{{ steps.detect_db.has_db == true }}"
    action: system
    output: "[CONPORT_ACTIVE] ConPort memory initialized. Existing contexts and recent activity loaded."

  # 4) If DB missing → decide whether to initialize
  - id: init_decision
    when: "{{ steps.detect_db.has_db != true }}"
    action: system
    say: |
      No ConPort database found at: {{ steps.paths.db_path }}
      Initialize a new ConPort database for this workspace?
      (init={{ inputs.init }}, import_brief={{ inputs.import_brief }}, brief_path={{ inputs.brief_path }})
    output_transform:
      do_init: >-
        {{
          (inputs.init == 'yes')
          or (inputs.init == 'ask' and true)   # treat 'ask' as consent in non-interactive flows; override to 'no' to skip
        }}

  # 5) Optional first-run brief import (only if initializing)
  - id: read_brief
    when: "{{ steps.init_decision.do_init == true }}"
    action: fs_op
    tool: read_file_if_exists
    params: { path: "{{ inputs.brief_path }}" }

  - id: decide_import_brief
    when: "{{ steps.init_decision.do_init == true }}"
    action: system
    output_transform:
      will_import_brief: >-
        {{
          (steps.read_brief.exists == true)
          and (inputs.import_brief == 'yes' or inputs.import_brief == 'ask')
        }}

  - id: bootstrap_product_with_brief
    when: "{{ steps.decide_import_brief.will_import_brief == true }}"
    action: conport_op
    tool: update_product_context
    params:
      workspace_id: "{{ context.workspace_id }}"
      content:
        initial_product_brief: "{{ steps.read_brief.contents | strip }}"

  # 6) Light ping (forces DB creation on first write if needed) + set minimal Active
  - id: set_active_min
    when: "{{ steps.init_decision.do_init == true }}"
    action: conport_op
    tool: update_active_context
    params:
      workspace_id: "{{ context.workspace_id }}"
      content:
        current_focus: "Initialization"
        last_run: "{{ now_iso() }}"

  # 7) After init, load context to confirm (ACTIVE)
  - id: load_after_init
    when: "{{ steps.init_decision.do_init == true }}"
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/load.md
    with:
      limits: "{{ inputs.limits }}"
      recent_activity: "{{ inputs.recent_activity }}"
      include:
        product: true
        active:  true
        decisions: true
        progress:  true
        patterns:  true
        glossary:  true
        activity:  true

  - id: mark_active_after_init
    when: "{{ steps.init_decision.do_init == true }}"
    action: system
    output: "[CONPORT_ACTIVE] ConPort database created and initial context loaded."

  # 8) If user skipped init → mark INACTIVE
  - id: mark_inactive
    when: "{{ steps.detect_db.has_db != true and steps.init_decision.do_init != true }}"
    action: system
    output: "[CONPORT_INACTIVE] Proceeding without ConPort for this session."

outputs:
  success:
    status: ok
    conport_status: >-
      {{
        (steps.detect_db.has_db == true and '[CONPORT_ACTIVE]')
        or (steps.init_decision.do_init == true and '[CONPORT_ACTIVE]')
        or '[CONPORT_INACTIVE]'
      }}
    message: >-
      {{
        (steps.mark_active.output or '')
        or (steps.mark_active_after_init.output or '')
        or (steps.mark_inactive.output or '')
      }}
    product:   "{{ (steps.load_if_active.product or steps.load_after_init.product) or {} }}"
    active:    "{{ (steps.load_if_active.active  or steps.load_after_init.active)  or {} }}"
    decisions: "{{ (steps.load_if_active.decisions or steps.load_after_init.decisions) or [] }}"
    progress:  "{{ (steps.load_if_active.progress  or steps.load_after_init.progress)  or [] }}"
    patterns:  "{{ (steps.load_if_active.patterns  or steps.load_after_init.patterns)  or [] }}"
    glossary:  "{{ (steps.load_if_active.glossary  or steps.load_after_init.glossary)  or [] }}"
    activity:  "{{ (steps.load_if_active.activity  or steps.load_after_init.activity)  or {} }}"
```
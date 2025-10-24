---
description: Bootstrap the contextual framework to a new or existing project.
---

```yaml
name: bootstrap
description: |
  Bootstrap ConPort context persistence framework.
  Initializes database, imports docs, captures Git state, sets up contexts, validates.
  Safe to run multiple times - all operations are idempotent.

inputs:
  import_docs: { type: boolean, default: true }
  create_imprint: { type: boolean, default: true }
  git_lookback_days: { type: integer, default: 14 }
  install_deps: { type: boolean, default: false }
  force_reinit: { type: boolean, default: false }
  pre_opts: { type: object, default: {} }
  post_opts: { type: object, default: { log_run_record: true, export_on_change: true, preserve_focus: false } }
  dry_run: { type: boolean, default: false }

steps:
  - id: preflight
    action: workflow
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"
    on_error: { strategy: continue, output: "[BOOTSTRAP] preflight skipped" }

  - id: check_conport_db
    action: fs_op
    tool: get_file_info
    params: { path: "{{ context.workspace_id }}/context_portal/context.db" }
    on_error: { strategy: continue, output: { exists: false } }

  - id: has_conport
    action: system
    output_transform:
      exists: "{{ steps.check_conport_db.size and steps.check_conport_db.size > 0 }}"
      status: "{{ steps.check_conport_db.size and 'EXISTING' or 'NEW' }}"

  - id: announce_mode
    action: system
    output: |
      [BOOTSTRAP] Mode: {{ inputs.force_reinit and 'REINIT' or steps.has_conport.status }}
      Init: {{ not steps.has_conport.exists or inputs.force_reinit }}
      Docs: {{ inputs.import_docs }}
      Imprint: {{ inputs.create_imprint }}

  - id: initialize_conport
    when: "{{ not steps.has_conport.exists or inputs.force_reinit }}"
    action: conport_op
    tool: get_product_context
    params: { workspace_id: "{{ context.workspace_id }}" }
    on_error: { strategy: continue }

  - id: verify_init
    when: "{{ not steps.has_conport.exists or inputs.force_reinit }}"
    action: fs_op
    tool: get_file_info
    params: { path: "{{ context.workspace_id }}/context_portal/context.db" }
    on_error: { strategy: fail, message: "ConPort init failed" }

  - id: read_readme
    when: "{{ inputs.import_docs and not inputs.dry_run }}"
    action: fs_op
    tool: read_text_file
    params: { path: "README.md" }
    on_error: { strategy: continue, output: { content: "" } }

  - id: import_readme
    when: "{{ inputs.import_docs and steps.read_readme.content and not inputs.dry_run }}"
    action: conport_op
    tool: log_custom_data
    params:
      workspace_id: "{{ context.workspace_id }}"
      category: "ProjectDocs"
      key: "README"
      value: { title: "README", content: "{{ steps.read_readme.content }}", source: "README.md", imported_at: "{{ context.current_time }}" }
    on_error: { strategy: continue }

  - id: find_docs
    when: "{{ inputs.import_docs }}"
    action: fs_op
    tool: search_files
    params: { path: "docs/", pattern: "*.md" }
    on_error: { strategy: continue, output: { results: [] } }

  - id: read_pyproject
    action: fs_op
    tool: read_text_file
    params: { path: "pyproject.toml" }
    on_error: { strategy: continue, output: { content: "" } }

  - id: build_product_context
    action: system
    output_transform:
      context:
        project_name: "{{ context.workspace_id | basename }}"
        workspace_path: "{{ context.workspace_id }}"
        bootstrapped_at: "{{ context.current_time }}"
        conport_version: "{{ steps.has_conport.exists and 'existing' or 'fresh' }}"
        readme_imported: "{{ steps.import_readme and true or false }}"
        docs_count: "{{ (steps.find_docs.results or []) | length }}"
        git_captured_days: "{{ inputs.git_lookback_days }}"
        framework_status: "active"

  - id: update_product_context
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: update_product_context
    params:
      workspace_id: "{{ context.workspace_id }}"
      patch_content: "{{ steps.build_product_context.context }}"
    on_error: { strategy: fail, message: "Failed to init Product Context" }

  - id: git_status
    action: git_op
    tool: git_status
    params: { repo_path: "{{ context.project.root_path }}" }
    on_error: { strategy: continue, output: "" }

  - id: git_log
    action: git_op
    tool: git_log
    params: { repo_path: "{{ context.project.root_path }}", max_count: 20 }
    on_error: { strategy: continue, output: "" }

  - id: git_branch
    action: git_op
    tool: git_branch
    params: { repo_path: "{{ context.project.root_path }}", branch_type: "local" }
    on_error: { strategy: continue, output: [] }

  - id: build_active_context
    action: system
    output_transform:
      context:
        current_focus: "Bootstrap complete"
        workflow: "bootstrap"
        bootstrapped_at: "{{ context.current_time }}"
        git_branch: "{{ steps.git_branch.output[0] if steps.git_branch.output else 'unknown' }}"
        git_status: "{{ steps.git_status.output and 'has_changes' or 'clean' }}"
        recent_commits: "{{ steps.git_log.output | length if steps.git_log.output else 0 }}"
        framework_ready: true

  - id: update_active_context
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: update_active_context
    params:
      workspace_id: "{{ context.workspace_id }}"
      patch_content: "{{ steps.build_active_context.context }}"
    on_error: { strategy: fail, message: "Failed to init Active Context" }

  - id: create_style_imprint
    when: "{{ inputs.create_imprint and not inputs.dry_run }}"
    action: workflow
    file: .windsurf/workflows/imprint.md
    with: { scope: "src/", sample_size: 10, dry_run: false }
    on_error: { strategy: continue }

  - id: load_product
    action: conport_op
    tool: get_product_context
    params: { workspace_id: "{{ context.workspace_id }}" }
    on_error: { strategy: fail, message: "Validation failed - cannot load Product Context" }

  - id: load_active
    action: conport_op
    tool: get_active_context
    params: { workspace_id: "{{ context.workspace_id }}" }
    on_error: { strategy: fail, message: "Validation failed - cannot load Active Context" }

  - id: validation_report
    action: system
    output: |
      [BOOTSTRAP_OK]
      Product: {{ steps.load_product.content and 'OK' or 'EMPTY' }}
      Active: {{ steps.load_active.content and 'OK' or 'EMPTY' }}
      DB: {{ context.workspace_id }}/context_portal/context.db

  - id: log_bootstrap
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: log_custom_data
    params:
      workspace_id: "{{ context.workspace_id }}"
      category: "ProjectDocs"
      key: "bootstrap-log"
      value:
        bootstrapped_at: "{{ context.current_time }}"
        mode: "{{ steps.has_conport.status }}"
        actions:
          initialized_db: "{{ not steps.has_conport.exists or inputs.force_reinit }}"
          imported_readme: "{{ steps.import_readme and true or false }}"
          imported_docs_count: "{{ (steps.find_docs.results or []) | length }}"
          created_imprint: "{{ inputs.create_imprint }}"
    on_error: { strategy: continue }

  - id: postflight
    action: workflow
    file: .windsurf/workflows/hooks/post.md
    with:
      progress: [{ description: "Bootstrap complete", status: "DONE" }]
      active_patch: { current_focus: "Bootstrap complete", workflow: "bootstrap", last_run: "{{ context.current_time }}" }
      log_run_record: "{{ inputs.post_opts.log_run_record }}"
      export_on_change: "{{ inputs.post_opts.export_on_change }}"
      capture_git_snapshot: true
    on_error: { strategy: continue }

outputs:
  success:
    status: ok
    message: |
      Framework BOOTSTRAPPED
      Mode: {{ steps.has_conport.status }}
      Product: {{ steps.load_product.content and 'OK' or 'EMPTY' }}
      Active: {{ steps.load_active.content and 'OK' or 'EMPTY' }}
      README: {{ steps.import_readme and 'Yes' or 'No' }}
      Docs: {{ (steps.find_docs.results or []) | length }}
      Imprint: {{ inputs.create_imprint and 'Yes' or 'No' }}
      Branch: {{ steps.build_active_context.context.git_branch }}
    database_path: "{{ context.workspace_id }}/context_portal/context.db"
    mode: "{{ steps.has_conport.status }}"
    product_context_ok: "{{ steps.load_product.content and true or false }}"
    active_context_ok: "{{ steps.load_active.content and true or false }}"
    dry_run: "{{ inputs.dry_run }}"
---
description: Generate or update documentation for files in scope and commit if changed.
---

```yaml
---
description: Generate or update documentation for files in scope and commit if changed. Hooked with pre/post; no tests.
---

name: document
description: |
  Generate or update docs for the given scope (files/dir), then run a light quality pass (format+lint only).
  Commit if there are diffs. Wrap with preflight/postflight. Do NOT run tests here.

inputs:
  task:  { type: string, required: true }
  scope: { type: string, required: true }
  pre_opts:  { type: object, required: false, default: {} }
  post_opts:
    type: object
    required: false
    default: { capture_git_snapshot: true, log_run_record: true, export_on_change: true }

steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"

  # ---------- Generate/refresh docs ----------
  - id: gen_docs
    action: coding_op
    tool: generate_docs_for_scope
    params:
      scope: "{{ inputs.scope }}"
      repo_root: "{{ context.project.root_path }}"
      # Keep the tool free to choose (docstrings, READMEs, API refs) based on scope contents

  # ---------- Format/lint and commit if anything changed (no tests) ----------
  - id: qa_and_commit
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/update.md
    with:
      scope: "{{ inputs.scope }}"
      quality_gate:
        format: true
        lint: true
        typecheck: false
        tests: false
        coverage_threshold: 0
      commit_type: "docs"
      commit_scope: "auto"
      commit_subject: "{{ inputs.task }}"
      do_stage: true
      do_commit: true
      do_push: false

  # ---------- Prepare progress payload for postflight ----------
  - id: progress_payload
    action: system
    output_transform:
      progress:
        - description: >-
            Docs: '{{ inputs.task }}' — scope={{ inputs.scope }}
            {{ steps.qa_and_commit.commit_hash and 'committed '+steps.qa_and_commit.commit_hash[:7] or 'no changes' }}
          status: "{{ steps.qa_and_commit.commit_hash and 'DONE' or 'IN_PROGRESS' }}"

  # ---------- POST HOOK ----------
  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.progress_payload.progress }}"
      active_patch:
        current_focus: "{{ inputs.task }}"
        requested_scope: "{{ inputs.scope }}"
        workflow: "document"
        last_run: "{{ now_iso() }}"
      {{ inputs.post_opts | tojson }}

outputs:
  success:
    status: ok
    message: >-
      Documentation {{ steps.qa_and_commit.commit_hash and 'updated' or 'checked (no changes)' }}.
      {{ steps.qa_and_commit.commit_hash and ('commit='+steps.qa_and_commit.commit_hash[:7]) or '' }}
```
---
description: Learn and capture coding style patterns to improve alignment and reduce refactoring.
---

```yaml
name: imprint
description: |
  Style Imprinting: Learn coding patterns and stylistic choices.
  Analyzes codebase to extract naming, structure, imports, docs, error handling.
  Stored in ConPort for reference during code generation to reduce refactoring.

inputs:
  scope: { type: string, default: "src/", description: "Directory to analyze" }
  sample_size: { type: integer, default: 10, description: "Number of files to sample" }
  languages: { type: array, default: ["python"] }
  focus_areas: { type: array, default: ["naming", "structure", "types", "imports", "docs", "errors"] }
  merge_strategy: { type: string, default: "deep_merge" }
  pre_opts: { type: object, default: {} }
  post_opts: { type: object, default: { log_run_record: true, export_on_change: true, preserve_focus: true } }
  dry_run: { type: boolean, default: false }

steps:
  - id: preflight
    action: workflow
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"
    on_error: { strategy: continue, output: "[IMPRINT] preflight failed" }

  - id: load_existing_imprint
    action: conport_op
    tool: get_custom_data
    params: { workspace_id: "{{ context.workspace_id }}", category: "StyleImprint", key: "repo-wide" }
    on_error: { strategy: continue, output: { value: null } }

  - id: has_existing
    action: system
    output_transform:
      exists: "{{ steps.load_existing_imprint.value != null }}"
      version: "{{ steps.load_existing_imprint.value and steps.load_existing_imprint.value.version or 0 }}"

  - id: find_source_files
    action: fs_op
    tool: search_files
    params: { path: "{{ inputs.scope }}", pattern: "*.py" }
    on_error: { strategy: fail, message: "Failed to find source files in {{ inputs.scope }}" }

  - id: sample_files
    action: system
    output_transform:
      files: "{{ steps.find_source_files.results[:inputs.sample_size] }}"
      count: "{{ steps.find_source_files.results | length }}"

  - id: read_samples
    action: fs_op
    tool: read_multiple_files
    params: { paths: "{{ steps.sample_files.files }}" }
    on_error: { strategy: continue, message: "Some files could not be read" }

  - id: analyze_naming
    when: "{{ 'naming' in inputs.focus_areas }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: "Analyze NAMING from {{ steps.sample_files.count }} files: Variables (snake_case?), Functions (verb-first?), Classes (CamelCase, suffixes?), Files, Constants. Extract patterns and examples."
      nextThoughtNeeded: true
      thoughtNumber: 1
      totalThoughts: 6
      isRevision: false

  - id: analyze_structure
    when: "{{ 'structure' in inputs.focus_areas and steps.analyze_naming.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: "Analyze STRUCTURE: Classes (dataclasses? Pydantic?), Type hints (Optional[] vs |?), future annotations, field() patterns, decorators. Extract examples."
      nextThoughtNeeded: true
      thoughtNumber: 2
      totalThoughts: 6
      isRevision: false

  - id: analyze_imports
    when: "{{ 'imports' in inputs.focus_areas and steps.analyze_structure.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: "Analyze IMPORTS: Future imports? Grouping (stdlib, third-party, local)? Ordering? Absolute vs relative? Extract pattern."
      nextThoughtNeeded: true
      thoughtNumber: 3
      totalThoughts: 6
      isRevision: false

  - id: analyze_documentation
    when: "{{ 'docs' in inputs.focus_areas and steps.analyze_imports.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: "Analyze DOCS: Docstring style (Google/NumPy/Sphinx)? Type hints in docs or sigs? Module docs? Comments? Extract style."
      nextThoughtNeeded: true
      thoughtNumber: 4
      totalThoughts: 6
      isRevision: false

  - id: analyze_errors
    when: "{{ 'errors' in inputs.focus_areas and steps.analyze_documentation.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: "Analyze ERRORS: Exception types? Try-except patterns? Error message style? Logging? Validation? Extract idioms."
      nextThoughtNeeded: true
      thoughtNumber: 5
      totalThoughts: 6
      isRevision: false

  - id: synthesize_imprint
    when: "{{ steps.analyze_errors.nextThoughtNeeded or steps.analyze_documentation.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: 'SYNTHESIZE as JSON: {"version":{{ steps.has_existing.version + 1 }},"naming":{vars,funcs,classes,files,consts},"structure":{patterns,hints,defaults},"imports":{org,future,style},"docs":{style,comments},"errors":{patterns},"examples":{func,class}}. Be specific with examples.'
      nextThoughtNeeded: false
      thoughtNumber: 6
      totalThoughts: 6
      isRevision: false

  - id: build_imprint_data
    action: system
    output_transform:
      imprint:
        version: "{{ steps.has_existing.version + 1 }}"
        scope: "{{ inputs.scope }}"
        analyzed_files_count: "{{ steps.sample_files.count }}"
        sample_files: "{{ steps.sample_files.files }}"
        last_updated: "{{ context.current_time }}"
        languages: "{{ inputs.languages }}"
        focus_areas: "{{ inputs.focus_areas }}"
        analysis:
          naming: "{{ steps.analyze_naming.thought }}"
          structure: "{{ steps.analyze_structure.thought }}"
          imports: "{{ steps.analyze_imports.thought }}"
          documentation: "{{ steps.analyze_documentation.thought }}"
          error_handling: "{{ steps.analyze_errors.thought }}"
          synthesis: "{{ steps.synthesize_imprint.thought }}"
        previous_version: "{{ steps.load_existing_imprint.value }}"

  - id: merge_imprints
    when: "{{ inputs.merge_strategy == 'deep_merge' and steps.has_existing.exists }}"
    action: system
    output: "[IMPRINT] Merging with v{{ steps.has_existing.version }}"

  - id: upsert_imprint
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: log_custom_data
    params: { workspace_id: "{{ context.workspace_id }}", category: "StyleImprint", key: "repo-wide", value: "{{ steps.build_imprint_data.imprint }}" }
    on_error: { strategy: fail, message: "Failed to save style imprint" }

  - id: preview_imprint
    when: "{{ inputs.dry_run }}"
    action: system
    output: "[IMPRINT_PREVIEW] v{{ steps.build_imprint_data.imprint.version }}, {{ steps.sample_files.count }} files, {{ inputs.focus_areas | join(',') }}"

  - id: log_as_pattern
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: log_system_pattern
    params:
      workspace_id: "{{ context.workspace_id }}"
      name: "Code Style Guide v{{ steps.build_imprint_data.imprint.version }}"
      description: "{{ steps.synthesize_imprint.thought[:500] }}..."
      tags: ["style", "patterns", "imprint", "v{{ steps.build_imprint_data.imprint.version }}"]
    on_error: { strategy: continue }

  - id: build_progress
    action: system
    output_transform:
      progress:
        description: "Style imprint v{{ steps.build_imprint_data.imprint.version }} from {{ steps.sample_files.count }} files"
        status: "{{ inputs.dry_run and 'IN_PROGRESS' or 'DONE' }}"
        linked_item_type: "custom_data"
        linked_item_id: "StyleImprint/repo-wide"

  - id: build_active_patch
    when: "{{ not inputs.post_opts.preserve_focus }}"
    action: system
    output_transform:
      patch:
        current_focus: "Style imprinting"
        workflow: "imprint"
        last_run: "{{ context.current_time }}"
        imprint_version: "{{ steps.build_imprint_data.imprint.version }}"

  - id: postflight
    action: workflow
    file: .windsurf/workflows/hooks/post.md
    with:
      progress: ["{{ steps.build_progress.progress }}"]
      active_patch: "{{ steps.build_active_patch.patch or {} }}"
      log_run_record: "{{ inputs.post_opts.log_run_record }}"
      export_on_change: "{{ inputs.post_opts.export_on_change }}"
      capture_git_snapshot: true
    on_error: { strategy: continue, output: "[IMPRINT] postflight failed" }

outputs:
  success:
    status: ok
    message: |
      ✓ Style imprint v{{ steps.build_imprint_data.imprint.version }}
      Analyzed: {{ steps.sample_files.count }} files in {{ inputs.scope }}
      Focus: {{ inputs.focus_areas | join(', ') }}
      {{ inputs.dry_run and 'Dry run - no changes' or 'Saved to ConPort' }}
    version: "{{ steps.build_imprint_data.imprint.version }}"
    scope: "{{ inputs.scope }}"
    analyzed_count: "{{ steps.sample_files.count }}"
    focus_areas: "{{ inputs.focus_areas }}"
    dry_run: "{{ inputs.dry_run }}"
    previous_version: "{{ steps.has_existing.version }}"
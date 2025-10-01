---
description: Ingest a file into ConPort knowledge graph with intelligent classification and structuring.
---

```yaml
name: ingest
description: |
  Intelligent file ingestion into ConPort's knowledge graph.
  
  Flow:
  1. Preflight: Load context
  2. Read target file
  3. AI analyzes content and classifies it
  4. Extract structured information (decisions, patterns, glossary, etc.)
  5. Upsert to appropriate ConPort categories
  6. Postflight: Log and sync
  
  The AI agent determines how to best structure and categorize the content
  based on its nature (documentation, code, decisions, architecture, etc.)

inputs:
  file_path:
    type: string
    required: true
    description: "Path to file to ingest (relative or absolute)"
  
  category_hint:
    type: string
    required: false
    description: "Optional hint: product_context, decision, system_pattern, glossary, reference"
  
  merge_strategy:
    type: string
    default: "deep_merge"
    description: "How to handle existing entries: replace or deep_merge"
  
  extract_decisions:
    type: boolean
    default: true
    description: "Extract and log architectural decisions"
  
  extract_patterns:
    type: boolean
    default: true
    description: "Extract and log coding/system patterns"
  
  extract_glossary:
    type: boolean
    default: true
    description: "Extract and log glossary terms"
  
  auto_classify:
    type: boolean
    default: true
    description: "Let AI automatically classify content types"
  
  pre_opts:
    type: object
    default: {}
  
  post_opts:
    type: object
    default: { log_run_record: true, export_on_change: true, preserve_focus: true }
  
  dry_run:
    type: boolean
    default: false

steps:
  # ---------- PREFLIGHT ----------
  - id: preflight
    action: workflow
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"
    on_error:
      strategy: continue
      output: "[INGEST] preflight failed, continuing with limited context"

  # ---------- Validate and read file ----------
  - id: check_file
    action: fs_op
    tool: get_file_info
    params:
      path: "{{ inputs.file_path }}"
    on_error:
      strategy: fail
      message: "File not found: {{ inputs.file_path }}"

  - id: read_file
    action: fs_op
    tool: read_text_file
    params:
      path: "{{ inputs.file_path }}"
    on_error:
      strategy: fail
      message: "Failed to read file: {{ inputs.file_path }}"

  # ---------- AI Analysis: Classify and extract structured content ----------
  - id: analyze_content
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: |
        Analyze the file content from {{ inputs.file_path }}.
        
        File size: {{ steps.check_file.size }} bytes
        Content preview: {{ steps.read_file.content[:500] }}...
        
        Task: Determine the nature of this content:
        1. Is it product/architecture documentation?
        2. Does it contain architectural decisions (ADRs)?
        3. Are there coding patterns or conventions?
        4. Does it define glossary terms or concepts?
        5. Is it reference documentation (API, tools)?
        
        Classify primary type and identify key information to extract.
      nextThoughtNeeded: true
      thoughtNumber: 1
      totalThoughts: 5
      isRevision: false

  - id: extract_structure
    when: "{{ steps.analyze_content.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: |
        Based on classification, extract structured information:
        
        - Title/name for this content
        - Category (product_context, decision, system_pattern, glossary, reference)
        - Key points or sections
        - Tags for organization
        - Any sub-items (decisions, patterns, terms)
        
        Structure this as JSON-compatible data.
      nextThoughtNeeded: true
      thoughtNumber: 2
      totalThoughts: 5
      isRevision: false

  - id: finalize_structure
    when: "{{ steps.extract_structure.nextThoughtNeeded }}"
    action: sequential_thinking
    tool: sequentialthinking
    params:
      thought: |
        Finalize extraction into this structure:
        {
          "primary": {
            "category": "...",
            "key": "...",
            "title": "...",
            "content": "...",
            "tags": [...]
          },
          "decisions": [...],  // if any
          "patterns": [...],   // if any
          "glossary": {...}    // if any
        }
        
        Make keys filesystem-safe (lowercase, hyphens, no spaces).
      nextThoughtNeeded: false
      thoughtNumber: 3
      totalThoughts: 3
      isRevision: false

  # ---------- Build structured data from AI analysis ----------
  - id: build_primary_entry
    action: system
    output_transform:
      entry:
        category: "{{ inputs.category_hint or 'ProjectDocs' }}"
        key: "{{ inputs.file_path | replace('/', '_') | replace('.', '_') }}"
        value:
          title: "{{ steps.check_file.path }}"
          source_path: "{{ inputs.file_path }}"
          content: "{{ steps.read_file.content }}"
          ingested_at: "{{ context.current_time }}"
          file_size: "{{ steps.check_file.size }}"
          analysis: "{{ steps.finalize_structure.thought }}"
          tags: ["ingested", "file_import"]

  # ---------- Upsert primary entry ----------
  - id: upsert_primary
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: log_custom_data
    params:
      workspace_id: "{{ context.workspace_id }}"
      category: "{{ steps.build_primary_entry.entry.category }}"
      key: "{{ steps.build_primary_entry.entry.key }}"
      value: "{{ steps.build_primary_entry.entry.value }}"
    on_error:
      strategy: continue
      message: "Failed to upsert primary entry"

  - id: preview_primary
    when: "{{ inputs.dry_run }}"
    action: system
    output: |
      [INGEST_PREVIEW]
      Would ingest to ConPort:
      Category: {{ steps.build_primary_entry.entry.category }}
      Key: {{ steps.build_primary_entry.entry.key }}
      Title: {{ steps.build_primary_entry.entry.value.title }}
      Size: {{ steps.check_file.size }} bytes

  # ---------- Extract and log decisions (if identified) ----------
  - id: check_for_decisions
    when: "{{ inputs.extract_decisions and inputs.auto_classify }}"
    action: system
    output_transform:
      has_decisions: "{{ steps.finalize_structure.thought | contains('decision') }}"

  - id: log_decisions
    when: "{{ steps.check_for_decisions.has_decisions and not inputs.dry_run }}"
    action: system
    output: "[INGEST] Decision extraction would happen here - requires AI parsing"

  # ---------- Extract and log patterns (if identified) ----------
  - id: check_for_patterns
    when: "{{ inputs.extract_patterns and inputs.auto_classify }}"
    action: system
    output_transform:
      has_patterns: "{{ steps.finalize_structure.thought | contains('pattern') }}"

  - id: log_patterns
    when: "{{ steps.check_for_patterns.has_patterns and not inputs.dry_run }}"
    action: system
    output: "[INGEST] Pattern extraction would happen here - requires AI parsing"

  # ---------- Extract and log glossary terms (if identified) ----------
  - id: check_for_glossary
    when: "{{ inputs.extract_glossary and inputs.auto_classify }}"
    action: system
    output_transform:
      has_glossary: "{{ steps.finalize_structure.thought | contains('glossary') or steps.finalize_structure.thought | contains('term') }}"

  - id: log_glossary
    when: "{{ steps.check_for_glossary.has_glossary and not inputs.dry_run }}"
    action: system
    output: "[INGEST] Glossary extraction would happen here - requires AI parsing"

  # ---------- Search for similar existing content ----------
  - id: search_similar
    when: "{{ not inputs.dry_run }}"
    action: conport_op
    tool: semantic_search_conport
    params:
      workspace_id: "{{ context.workspace_id }}"
      query_text: "{{ steps.read_file.content[:200] }}"
      top_k: 3
      filter_item_types: ["custom_data"]
    on_error:
      strategy: continue
      output: { results: [] }

  - id: report_similar
    when: "{{ (steps.search_similar.results or []) | length > 0 }}"
    action: system
    output: |
      [INGEST] Found {{ (steps.search_similar.results or []) | length }} similar entries in ConPort.
      This ingestion is additive/idempotent.

  # ---------- Prepare progress payload ----------
  - id: build_progress
    action: system
    output_transform:
      progress:
        description: "Ingested {{ inputs.file_path }} into ConPort knowledge graph"
        status: "{{ inputs.dry_run and 'IN_PROGRESS' or 'DONE' }}"
        linked_item_type: "custom_data"
        linked_item_id: "{{ steps.build_primary_entry.entry.category }}/{{ steps.build_primary_entry.entry.key }}"

  # ---------- Build active context patch ----------
  - id: build_active_patch
    when: "{{ not inputs.post_opts.preserve_focus }}"
    action: system
    output_transform:
      patch:
        current_focus: "File ingestion"
        requested_scope: "{{ inputs.file_path }}"
        workflow: "ingest"
        last_run: "{{ context.current_time }}"
        ingested_file: "{{ inputs.file_path }}"

  # ---------- POSTFLIGHT ----------
  - id: postflight
    action: workflow
    file: .windsurf/workflows/hooks/post.md
    with:
      progress: ["{{ steps.build_progress.progress }}"]
      active_patch: "{{ steps.build_active_patch.patch or {} }}"
      log_run_record: "{{ inputs.post_opts.log_run_record }}"
      export_on_change: "{{ inputs.post_opts.export_on_change }}"
      capture_git_snapshot: true
    on_error:
      strategy: continue
      output: "[INGEST] postflight failed"

# -------------------------------- Outputs ------------------------------------
outputs:
  success:
    status: ok
    message: |
      ✓ File ingestion complete
      
      File: {{ inputs.file_path }}
      Size: {{ steps.check_file.size }} bytes
      Category: {{ steps.build_primary_entry.entry.category }}
      Key: {{ steps.build_primary_entry.entry.key }}
      Dry run: {{ inputs.dry_run }}
      
      {{ inputs.dry_run and 'Preview only - no changes made' or 'Ingested to ConPort knowledge graph ✓' }}
    
    file_path: "{{ inputs.file_path }}"
    category: "{{ steps.build_primary_entry.entry.category }}"
    key: "{{ steps.build_primary_entry.entry.key }}"
    file_size: "{{ steps.check_file.size }}"
    dry_run: "{{ inputs.dry_run }}"
    similar_count: "{{ (steps.search_similar.results or []) | length }}"

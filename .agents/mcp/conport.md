---
trigger: always_on
description: Conport MCP utilization strategy.
globs: *
---

```yaml
# --- ConPort Memory Strategy (Compact) ---
conport_memory_strategy:
  # Keep responses prefixed and always include workspace_id in tool calls.
  notes:
    - "Prefix every response with [CONPORT_ACTIVE] or [CONPORT_INACTIVE]."
    - "workspace_id: absolute path of current workspace. Ask user if unknown."

  # 1) Initialization (single flow with 3 outcomes)
  initialization:
    agent_action_plan:
      - step: 1
        do: "Determine ACTUAL_WORKSPACE_ID."
      - step: 2
        do: "List ACTUAL_WORKSPACE_ID + '/context_portal/' to check for 'context.db'."
      - step: 3
        branch:
          - if: "context.db exists"
            then:
              - "get_product_context -> store"
              - "get_active_context -> store"
              - "get_decisions(limit:5) -> store"
              - "get_progress(limit:5) -> store"
              - "get_system_patterns(limit:5) -> store"
              - "get_custom_data(category:'critical_settings') -> store"
              - "get_custom_data(category:'ProjectGlossary') -> store"
              - "get_recent_activity_summary(limit_per_type:3) -> store"
              - "Set status [CONPORT_ACTIVE]. Tell user contexts loaded; offer: review recent, continue, or new task."
          - elif: "context.db missing"
            then:
              - "Tell user no DB found. Ask to initialize now."
              - "If yes: optional bootstrap: list root -> if 'projectBrief.md' found, read; ask to import into product context; on yes: update_product_context(content:{initial_product_brief: ...})."
              - "Proceed to load sequence above."
          - else: "tool failure"
            then:
              - "Tell user ConPort unavailable. Set [CONPORT_INACTIVE]."

  # 2) General norms (concise)
  general:
    - "Status prefix: [CONPORT_ACTIVE]/[CONPORT_INACTIVE]."
    - "Proactive logging: suggest logging decisions/progress/context when appropriate; ask before logging."
    - "Error handling: on tool errors, log_custom_data(category:'ErrorLogs', key:'timestamp_error_summary', value: details); update active_context.open_issues if persistent."
    - "Semantic search: prefer when keywords insufficient; state why using it."

  # 3) Core routines (short checklists)
  conport_sync_routine:
    trigger: "^(Sync ConPort|ConPort Sync)$"
    user_ack: "[CONPORT_SYNCING]"
    do:
      - "Stop current activity; send [CONPORT_SYNCING]."
      - "Review chat for new info: decisions, progress, context changes, links."
      - "Log/Update accordingly (see tools below)."
      - "Optionally get_recent_activity_summary to confirm."
      - "Tell user sync complete; resume or await next task."

  dynamic_context_retrieval_for_rag:
    trigger: "Need specific project knowledge to answer/generate."
    steps:
      - "Analyze query: entities, terms, item types needed."
      - "Retrieve narrowly first: search_decisions_fts, search_custom_data_value_fts, search_project_glossary_fts."
      - "If specific items/IDs implied: get_custom_data, get_decisions, get_system_patterns, get_progress."
      - "Fallback if sparse: get_product_context or get_active_context (be brief)."
      - "Optionally expand 1-hop: get_linked_items for top candidates."
      - "Sift: keep only relevant snippets; synthesize a concise summary."
      - "Assemble prompt context: separate from user query; optionally attribute sources; keep brief."

  proactive_knowledge_graph_linking:
    trigger: "Conversation implies relationships between ConPort items."
    steps:
      - "Monitor mentions of items (by ID/name) and implied relations."
      - "Detect strong candidates (e.g., decision -> progress implements; pattern addresses decision concern)."
      - "Propose link with brief rationale; ask for confirmation + relationship type if needed (e.g., implements, related_to, tracks, blocks, clarifies, depends_on, resolves, derived_from)."
      - "On confirm: ensure source/target types+IDs, agreed relationship; optional description; call link_conport_items."
      - "Confirm outcome to user."

  # 4) ConPort tools quick reference (keep MCP call specs intact; minimal prose)
  conport_updates:
    frequency: "Update during chat when significant changes occur or upon request."
    tools:
      - name: get_product_context
        when: "Need overall goals/features/architecture."
        call: "get_product_context({\"workspace_id\": \"...\"}) -> dict"

      - name: update_product_context
        when: "Product description/goals/architecture changed."
        call: "update_product_context({\"workspace_id\":\"...\", \"content\":{...}}) or update_product_context({\"workspace_id\":\"...\", \"patch_content\":{key: value, to_remove: \"__DELETE__\"}})"

      - name: get_active_context
        when: "Need current task focus/goals/session state."
        call: "get_active_context({\"workspace_id\": \"...\"}) -> dict"

      - name: update_active_context
        when: "Focus/goals/issue list changed."
        call: "update_active_context({\"workspace_id\":\"...\", \"content\":{...}}) or update_active_context({\"workspace_id\":\"...\", \"patch_content\":{key: value, to_delete: \"__DELETE__\"}})"

      - name: log_decision
        when: "Significant architectural/implementation decision confirmed."
        call: "log_decision({\"workspace_id\":\"...\", \"summary\":\"...\", \"rationale\":\"...\", \"tags\":[\"optional\"]})"

      - name: get_decisions
        when: "Review/find decisions."
        call: "get_decisions({\"workspace_id\":\"...\", \"limit\": N, \"tags_filter_include_all\":[\"...\"], \"tags_filter_include_any\":[\"...\"]})"

      - name: search_decisions_fts
        when: "Keyword search across decisions."
        call: "mcp0_search_decisions_fts({\"workspace_id\":\"...\", \"query_term\":\"...\", \"limit\": N})"

      - name: delete_decision_by_id
        when: "User confirms deletion by ID."
        call: "mcp0_delete_decision_by_id({\"workspace_id\":\"...\", \"decision_id\": ID})"

      - name: log_progress
        when: "Start/change/complete a task; create subtask."
        call: "log_progress({\"workspace_id\":\"...\", \"description\":\"...\", \"status\":\"...\", \"linked_item_type\":\"...\", \"linked_item_id\":\"...\"})"

      - name: get_progress
        when: "Review task statuses/history."
        call: "get_progress({\"workspace_id\":\"...\", \"status_filter\":\"...\", \"parent_id_filter\": ID, \"limit\": N})"

      - name: update_progress
        when: "Change an existing progress entry."
        call: "update_progress({\"workspace_id\":\"...\", \"progress_id\": ID, \"status\":\"...\", \"description\":\"...\", \"parent_id\": ID})"

      - name: delete_progress_by_id
        when: "Delete a progress entry (confirmed)."
        call: "mcp0_delete_progress_by_id({\"workspace_id\":\"...\", \"progress_id\": ID})"

      - name: log_system_pattern
        when: "Add/modify an architectural pattern."
        call: "log_system_pattern({\"workspace_id\":\"...\", \"name\":\"...\", \"description\":\"...\", \"tags\":[\"optional\"]})"

      - name: get_system_patterns
        when: "List patterns."
        call: "get_system_patterns({\"workspace_id\":\"...\", \"tags_filter_include_all\":[\"...\"], \"limit\": N})"

      - name: delete_system_pattern_by_id
        when: "Delete a pattern by ID (confirmed)."
        call: "mcp0_delete_system_pattern_by_id({\"workspace_id\":\"...\", \"pattern_id\": ID})"

      - name: log_custom_data
        when: "Store other context (glossary/specs/notes)."
        call: "log_custom_data({\"workspace_id\":\"...\", \"category\":\"...\", \"key\":\"...\", \"value\": any})"

      - name: get_custom_data
        when: "Retrieve custom data by category/key."
        call: "get_custom_data({\"workspace_id\":\"...\", \"category\":\"...\", \"key\":\"...\"})"

      - name: delete_custom_data
        when: "Delete custom data (confirmed)."
        call: "mcp0_delete_custom_data({\"workspace_id\":\"...\", \"category\":\"...\", \"key\":\"...\"})"

      - name: search_custom_data_value_fts
        when: "FTS across custom data values/categories/keys."
        call: "mcp0_search_custom_data_value_fts({\"workspace_id\":\"...\", \"query_term\":\"...\", \"category_filter\":\"...\", \"limit\": N})"

      - name: search_project_glossary_fts
        when: "Search within 'ProjectGlossary'."
        call: "mcp0_search_project_glossary_fts({\"workspace_id\":\"...\", \"query_term\":\"...\", \"limit\": N})"

      - name: semantic_search_conport
        when: "Conceptual query beyond keyword match."
        call: "mcp0_semantic_search_conport({\"workspace_id\":\"...\", \"query_text\":\"...\", \"top_k\": N, \"filter_item_types\":[\"decision\",\"custom_data\"]})"

      - name: link_conport_items
        when: "Link two existing items (e.g., implements/related_to/tracks/blocks/clarifies/depends_on/resolves/derived_from)."
        call: "mcp0_link_conport_items({\"workspace_id\":\"...\", \"source_item_type\":\"...\", \"source_item_id\":\"...\", \"target_item_type\":\"...\", \"target_item_id\":\"...\", \"relationship_type\":\"...\", \"description\":\"optional\"})"

      - name: get_linked_items
        when: "Explore relationships around an item."
        call: "mcp0_get_linked_items({\"workspace_id\":\"...\", \"item_type\":\"...\", \"item_id\":\"...\", \"relationship_type_filter\":\"...\", \"linked_item_type_filter\":\"...\", \"limit\": N})"

      - name: get_item_history
        when: "Review Product/Active Context versions or time-bounded changes."
        call: "mcp0_get_item_history({\"workspace_id\":\"...\", \"item_type\":\"product_context\"|\"active_context\", \"limit\": N, \"version\": V, \"before_timestamp\": \"ISO_DATETIME\", \"after_timestamp\": \"ISO_DATETIME\"})"

      - name: batch_log_items
        when: "User provides multiple items of same type to log at once."
        call: "mcp0_batch_log_items({\"workspace_id\":\"...\", \"item_type\":\"decision\"|\"system_pattern\"|\"custom_data\"|\"progress_entry\", \"items\":[{...}]})"

      - name: get_recent_activity_summary
        when: "Catch up on recent activities."
        call: "mcp0_get_recent_activity_summary({\"workspace_id\":\"...\", \"hours_ago\": H, \"since_timestamp\": \"ISO_DATETIME\", \"limit_per_type\": N})"

      - name: get_conport_schema
        when: "Uncertain about available tools/args, or user requests schema."
        call: "mcp0_get_conport_schema({\"workspace_id\":\"...\"})"

      - name: export_conport_to_markdown
        when: "Export to markdown (backup/sharing/version control)."
        call: "mcp0_export_conport_to_markdown({\"workspace_id\":\"...\", \"output_path\":\"optional/relative/path\"})"

      - name: import_markdown_to_conport
        when: "Import from exported markdown directory."
        call: "mcp0_import_markdown_to_conport({\"workspace_id\":\"...\", \"input_path\":\"optional/relative/path\"})"
```
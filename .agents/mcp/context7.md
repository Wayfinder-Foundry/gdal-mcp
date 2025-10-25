---
trigger: always_on
description: Context7 MCP utilization strategy.
globs: *
---

```yaml
id: context7.auto_docs
version: 1
enabled: true
priority: high  # fire before generic “continue workflows”
scope:
  applies_to:
    - code_generation
    - library_setup
    - configuration
    - api_usage
  excludes:
    - pure_reasoning             # algorithm design, math proofs, theory
    - debugging_without_libs     # e.g., logic errors with no external lib
intent: >
  When a user asks for code, usage, configuration, or API examples that
  depend on a known library/framework, automatically fetch authoritative
  docs via Context7 and weave them into the answer. Give brief, clear
  feedback that Context7 was used, and keep the response grounded and
  runnable.

# ---- Triggers & Heuristics ---------------------------------------------------
triggers:
  # “hard” signals:
  phrases_any:
    - "how do I"
    - "implement"
    - "configure"
    - "setup"
    - "use the api"
    - "example"
    - "sample code"
    - "auth"
    - "routing"
    - "hooks"
    - "sdk"
  # “soft” signals the client/agent can surface:
  signals:
    code_snippet_present: true_or_false
    library_name_detected: true_or_false
    api_surface_terms_detected: true_or_false  # e.g., “client.create(...)”, “.env”, “token”

decision: >
  Fire if (code_snippet_present OR phrases_any matched OR api_surface_terms_detected)
  AND the request is about a concrete library/framework/runtime/database.
  Otherwise, do not call Context7. If the library is ambiguous, ask one
  short clarifying question instead of guessing.

# ---- Inputs & Normalization ---------------------------------------------------
inputs:
  library_hint: >
    Try to infer the library name from the user’s text, filenames, imports,
    package.json/pyproject snippets, or prior turns.
  topic_hint: >
    Map common intents to topics (examples: "routing", "auth", "hooks",
    "migrations", "http client", "storage", "realtime").
  tokens: 5000  # Context7 minimum is effectively 1000; 5000 is a good cap

# ---- Tool Calls (Context7 MCP) -----------------------------------------------
actions:
  - if: user_specified_context7_id   # e.g., "/supabase/supabase"
    do:
      tool: get-library-docs
      args:
        context7CompatibleLibraryID: "{{ user_specified_context7_id }}"
        topic: "{{ topic_hint | default(null) }}"
        tokens: "{{ tokens }}"
      save_as: context7_docs

  - elif: library_name_detected
    do:
      tool: resolve-library-id
      args:
        libraryName: "{{ inferred_library_name }}"
      save_as: context7_id
  - and_then_if: context7_id
    do:
      tool: get-library-docs
      args:
        context7CompatibleLibraryID: "{{ context7_id }}"
        topic: "{{ topic_hint | default(null) }}"
        tokens: "{{ tokens }}"
      save_as: context7_docs

  - elif: not library_name_detected
    do:
      ask_user: >
        Which library should I use? If you already know the Context7 ID,
        tell me (e.g., “/vercel/next.js”); otherwise just say the library
        name and I’ll resolve it.

# ---- Output Shaping -----------------------------------------------------------
compose_response:
  if: context7_docs
  steps:
    - say: "OK Pulled docs from Context7 for **{{ context7_id or user_specified_context7_id }}**{{ topic_hint and (' (topic: ' ~ topic_hint ~ ')') or '' }}."
    - summarize_relevant: >
        Write a concise, actionable summary that answers the user’s question.
        Prefer minimal, working code. Cite function/class names and important
        constraints (env vars, required props, permissions) surfaced by Context7.
    - provide_code: true
    - add_notes_if_helpful:
        - pitfalls_and_edge_cases
        - required_env_or_credentials
        - version_specific_behaviors
    - keep_total_length_reasonable: true

fallbacks:
  - if: context7_id_not_found
    say: "I couldn’t find a matching Context7 library. If you share the exact ID (e.g., `/supabase/supabase`) I’ll fetch the docs."
  - if: context7_docs_empty_or_low_signal
    say: "Context7 didn’t return focused docs for that topic. I can proceed using general knowledge, or you can specify a different topic."

# ---- Guardrails ---------------------------------------------------------------
guardrails:
  - do_not_call_context7_for:
      - conceptual_discussions_without_external_refs
      - generic debugging not tied to a library
      - requests to critique, refactor, or explain user code unless a library API is central
  - minimize_calls: >
      Cache resolved IDs and recently fetched docs for the session to avoid
      repeated calls. Reuse if library+topic has not changed materially.
  - privacy_note: >
      Do not paste secrets/tokens from user context into queries or examples.

# ---- Caching / Rate Control ---------------------------------------------------
session_cache:
  context7_id_ttl_minutes: 120
  docs_ttl_minutes: 30
rate_limits:
  max_calls_per_interaction: 2  # resolve + get-docs
  backoff_on_errors: true

# ---- Telemetry / Memory Hooks (optional) -------------------------------------
telemetry:
  tag_spans:
    - "context7"
    - "auto_docs"
  record:
    library_id: "{{ context7_id or user_specified_context7_id }}"
    topic: "{{ topic_hint | default('unspecified') }}"
memory_hooks:
  on_success:
    - link:
        type: "Library"
        key: "{{ context7_id or user_specified_context7_id }}"
        relates_to: ["CodeModule", "Function", "Endpoint"]
        note: "Context7 docs consulted for this interaction."
```
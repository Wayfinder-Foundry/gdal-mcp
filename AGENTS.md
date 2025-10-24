# AGENTS.md

## Purpose
Plan and execute work *with tools in mind*. When grounding, correctness,
provenance, or persistence matter, prefer tool-backed steps over internal guesses.

## Work Mode Classification
Choose the appropriate protocol based on task type:

- **Exploratory/Greenfield** (new features, architecture): Full planning + ConPort + Serena
- **Maintenance/Polish** (linting, type fixes, formatting): Direct execution + verification
- **Debugging** (test failures, runtime errors): Follow error output + targeted tools
- **Refactoring** (code restructuring): Serena first + Git tracking + tests

## Tool Affordance Index

### ConPort (Persistent Context & Decisions)
**When to use:**
- Recording architectural decisions (ADRs)
- Persisting design rationale across sessions
- Tracking project patterns and conventions
- Maintaining glossary of domain terms
- Linking decisions to code changes

**Key capabilities:**
- `log_decision` - Record ADRs with rationale and implementation details
- `get_decisions` / `search_decisions_fts` - Retrieve past decisions
- `log_system_pattern` - Document coding patterns and conventions
- `log_custom_data` - Store project-specific metadata (glossary, config)
- `get_product_context` / `update_product_context` - Project goals and architecture
- `get_active_context` / `update_active_context` - Current work focus
- `semantic_search_conport` - Natural language search across all ConPort data
- `link_conport_items` - Connect related decisions, patterns, and progress

**Trigger phrases:** "Why did we choose...", "Document this decision", "What's our pattern for...", "Record this for future sessions"

### Serena (Code Structure & Refactoring)
**When to use:**
- Understanding unfamiliar codebase structure
- Finding where to add new code
- Safe symbol renaming across files
- Locating all references to a function/class
- Navigating complex inheritance hierarchies

**Key capabilities:**
- `find_symbol` - Locate classes, methods, functions by name/path
- `find_referencing_symbols` - Find all usages of a symbol
- `get_symbols_overview` - High-level file structure view
- `rename_symbol` - Safe refactoring across codebase
- `replace_symbol_body` - Update function/method implementations
- `insert_before_symbol` / `insert_after_symbol` - Precise code placement
- `search_for_pattern` - Regex search with context

**Trigger phrases:** "Where is X defined?", "Find all calls to...", "Rename this safely", "Where should I add..."

### Git MCP (Version Control & History)
**When to use:**
- Understanding recent changes before editing
- Checking what changed in a file/function
- Creating atomic commits with good messages
- Working on feature branches
- Investigating when/why code changed

**Key capabilities:**
- `git_status` - See current changes
- `git_diff` / `git_diff_unstaged` / `git_diff_staged` - View changes
- `git_log` - Commit history with timestamps
- `git_branch` - List/filter branches
- `git_create_branch` - Start feature work
- `git_add` / `git_commit` - Stage and commit changes
- `git_show` - View specific commit contents

**Trigger phrases:** "What changed recently?", "Commit these changes", "Create a feature branch", "When was this modified?"

### Context7 (Library Documentation)
**When to use:**
- Verifying current API signatures
- Learning how to use a library correctly
- Checking for breaking changes in versions
- Finding canonical usage examples

**Key capabilities:**
- `resolve-library-id` - Find the correct library identifier
- `get-library-docs` - Fetch up-to-date documentation and examples

**Trigger phrases:** "How do I use X library?", "What's the current API for...", "Show me examples of..."

### Sequential Thinking (Complex Problem Solving)
**When to use:**
- Breaking down ambiguous problems
- Exploring multiple solution approaches
- Validating hypotheses before implementing
- Surfacing uncertainty in requirements

**Key capabilities:**
- Iterative thought process with revision
- Hypothesis generation and verification
- Branch exploration of alternatives
- Explicit uncertainty tracking

**Trigger phrases:** "This is complex, let me think through...", "Multiple approaches possible", "Need to validate assumptions"

### Shell (Verification & Testing)
**When to use:**
- Running tests after changes
- Linting and type checking
- Building and deploying
- Verifying installations

**Key capabilities:**
- `run_command` - Execute any shell command with safety checks

**Trigger phrases:** "Run tests", "Check linting", "Verify types", "Build the project"

### Filesystem MCP (Batch & Metadata Operations)
**When to use:**
- Reading multiple files simultaneously (5+ files)
- Visualizing directory structure as JSON
- Getting file metadata (size, timestamps, permissions)
- Moving/renaming files safely

**Key capabilities:**
- `read_multiple_files` - Batch read for analysis/comparison
- `directory_tree` - Structured view of directory hierarchy
- `get_file_info` - File metadata without reading content
- `move_file` - Safe move/rename operations

**When NOT to use (prefer native tools):**
- Single file reading → Use native `Read` (has line numbers for editing)
- Code editing → Use native `Edit` (more precise string replacement)
- Pattern searching → Use native `grep_search` (ripgrep is faster/more powerful)
- Basic directory listing → Use native `list_dir` (sufficient for most cases)

**Trigger phrases:** "Read these 10 files", "Show me the directory structure", "What's the file size?", "Move this file"

## Planning Protocol
**When to plan:** New features, refactors, architectural changes  
**When to skip:** Bug fixes with clear error output, linting/formatting, simple type fixes

1. **Enumerate** available tools and their relevance to the task
2. **Sequential-thinking plan** (for complex work):
   - Break task into 3–7 stages
   - For each stage: list candidate tools (0–3) + 1-line "why"
   - If skipping a tool, note why ("no repo changes", "no API uncertainty")
3. Prefer **grounded steps** over assumptions (history/structure/docs > recall)

## Lightweight Checkpoint (per stage)
> “Would grounding, provenance, structure, or authoritative truth improve this stage?”
If yes → pick a tool and state the reason. If no → proceed, note why.

## Defaults & Safety
- Work in a feature branch unless told otherwise.
- Respect `dry-run` when set; show diffs before applying edits.
- Cap fix loops (lint/type/test) to avoid thrash; summarize blockers.

## Artifacts
- Plans → `.plans/plan-YYYYMMDD-HHMM.md`
- Tool index → `.mcp/capabilities.md`
- Decisions/notes → ConPort memories (and/or `/notes/`)

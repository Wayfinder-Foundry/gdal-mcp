---
trigger: model_decision
description: Always consult ConPort (knowledge graph) before proposing plans or making changes. Retrieve relevant specs, architecture, decisions, and style rules.
globs: 
---

# ConPort Preflight Checklist (Do this before coding)

1) Search ConPort for the current task
   - Use the semantic search atom: `.windsurf/workflows/atoms/conport/search.md`
   - Query with your task (e.g., "Implement Data.Points model")
   - Review top results across:
     - ArchitectureSummaries (e.g., `data_contract`, `validation_architecture`)
     - System Patterns (e.g., Lask Data Pattern, Lask Validation Pattern, Lask Code Style Pattern)
     - SpecSummaries/SpecConstraints (LAS/COPC)
     - ProjectGlossary terms

2) Extract constraints and invariants
   - For Data work, confirm: `schema` (PDRF + Extra Bytes), `crs`, `bounds`, chunking, lazy semantics
   - For Validation work, confirm profiles and rule IDs you must honor
   - For Style, confirm naming/typehints/constants/shadowing rules

3) Patch Active Context with focus
   - Use `.windsurf/workflows/atoms/conport/update.md` to set `current_focus`, `requested_scope`, and timestamp

4) Cross‑check style and patterns
   - CodeStyleGuide: `style.typehints`, `style.naming`, `style.dictionaries`, `style.aliasing`, `style.shadowing`, `style.constants`
   - System Patterns: Data, Validation, Processor

5) Only then propose a plan or edits
   - Plans must cite relevant ConPort items (rule IDs, pattern names, or summary keys)

Notes
- The `/continue` workflow already runs a ConPort semantic search preflight for the provided task.
- When ambiguous, run a second targeted search (type=custom or decisions) before proceeding.

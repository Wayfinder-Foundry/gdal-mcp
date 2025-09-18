---
trigger: model_decision
description: Review CodeStyleGuide rules (ConPort) and docs/styleguide/ before implementing or editing code. Ensure style, naming, type hints, and structure align with Lask patterns.
globs: 
---

Before writing or editing code:

1. Check ConPort for CodeStyleGuide entries (category=CodeStyleGuide) and read relevant rules:
   - style.typehints, style.naming, style.namespacing, style.constants, style.dictionaries,
     style.aliasing, style.shadowing, style.functions, style.organization, style.scope, style.solid.
2. Cross-check affected system patterns in ConPort (Lask Data Pattern, Processor Pattern, Validation Pattern) to keep architecture consistency.
3. Prefer domain-idiomatic names, full type hints, no magic values, minimal public exports, and structured types over Dict[str, Any].
4. For long dot chains, create local aliases; avoid shadowing imported names (prefix locals with _ if needed).
5. Keep modules focused (single responsibility) and APIs lean; depend on abstractions.

Sources:
- docs/styleguide/
- ConPort: CodeStyleGuide items
- ConPort: system_patterns.md

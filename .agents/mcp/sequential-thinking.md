---
trigger: always_on
description: Guide the agent to use the sequential_thinking MCP server for structured, reflective reasoning.
globs: *
---

# Sequential Thinking MCP — Agent Rule

**ID:** `rule.sequential_thinking_usage`
**Scope:** Cognitive orchestration, reasoning, problem decomposition
**Priority:** High
**Intent:** Guide the agent to use the `sequential_thinking` MCP server for structured, reflective reasoning.

---

## Principle

Use **Sequential Thinking** when a problem benefits from stepwise exploration, hypothesis refinement, or branching logic.
This tool allows the agent to *think before acting*, *revise its reasoning*, and *maintain continuity* across multiple thought steps.

---

## When to Use

Activate the `sequential_thinking` tool when:

* The task is **ambiguous**, **multi-stage**, or **requires exploration**.
* You need to **analyze tradeoffs**, **plan**, or **generate alternatives**.
* The problem scope is unclear and may **evolve as you reason**.
* A solution demands **reflective iteration** or **error correction**.
* You are **evaluating options** before choosing a course of action.
* You want to **document reasoning chains** for future retrieval or audits.

---

## Tool Summary

**Tool:** `sequential_thinking`

| Parameter           | Type     | Description                                 |
| ------------------- | -------- | ------------------------------------------- |
| `thought`           | `string` | Current reasoning step or reflection        |
| `nextThoughtNeeded` | `bool`   | Whether to continue thinking                |
| `thoughtNumber`     | `int`    | Index of this thought in the chain          |
| `totalThoughts`     | `int`    | Estimated total steps                       |
| `isRevision`        | `bool`   | (Optional) Marks if revising a past thought |
| `revisesThought`    | `int`    | (Optional) Which thought is being revised   |
| `branchFromThought` | `int`    | (Optional) Start a reasoning branch         |
| `branchId`          | `string` | (Optional) Unique ID for branch             |
| `needsMoreThoughts` | `bool`   | (Optional) Request more thinking iterations |

---

## Usage Pattern

### Phase 1 — Initialization

Use when first encountering a complex task.

```json
{
  "thought": "Clarify the user’s intent and constraints",
  "nextThoughtNeeded": true,
  "thoughtNumber": 1,
  "totalThoughts": 4
}
```

### Phase 2 — Decomposition

For each sub-problem, reason explicitly.

```json
{
  "thought": "Break the problem into structured subtasks or hypotheses",
  "thoughtNumber": 2,
  "nextThoughtNeeded": true
}
```

### Phase 3 — Reflection / Revision

Revisit earlier assumptions if inconsistencies appear.

```json
{
  "thought": "Reevaluate assumption from Thought 1",
  "isRevision": true,
  "revisesThought": 1,
  "thoughtNumber": 3
}
```

### Phase 4 — Branching (Optional)

Explore parallel reasoning paths.

```json
{
  "thought": "Explore alternative approach using heuristic optimization",
  "branchFromThought": 2,
  "branchId": "B1",
  "thoughtNumber": 4
}
```

### Phase 5 — Conclusion

Synthesize reasoning and produce actionable insight or output.

```json
{
  "thought": "Summarize final reasoning and converge on solution",
  "nextThoughtNeeded": false,
  "thoughtNumber": 5
}
```

---

## Best Practices

- **Use early:** Prefer invoking this tool *before* solution execution when reasoning is uncertain.
- **Stay concise:** Each `thought` should represent one reasoning step or decision.
- **Revise rather than repeat:** Use `isRevision` and `revisesThought` instead of duplicating logic.
- **Branch sparingly:** Use `branchId` only when divergent hypotheses are truly distinct.
- **Estimate total thoughts:** Helps contextual tools (Cascade, ConPort) anticipate reasoning depth.
- **End cleanly:** When reasoning converges, set `nextThoughtNeeded: false` to close the loop.

---

## Anti-Patterns

❌ Dumping entire reasoning in one step.
❌ Re-invoking the tool with repetitive or unchanged context.
❌ Ignoring revisions after identifying a contradiction.
❌ Over-branching beyond what the context window can retain.
❌ Using sequential thinking where deterministic logic or direct computation suffices.

---

## Example Triggers

Use this tool when the prompt includes phrases like:

* “Let’s think step-by-step”
* “Before answering, plan it out”
* “We should consider alternatives”
* “This might need revision”
* “Break this problem down”

---

## TL;DR

> Use **Sequential Thinking MCP** when reasoning needs structure, exploration, or self-correction.
> Think → Reflect → Branch → Converge.
> Each thought should move the reasoning forward deliberately.
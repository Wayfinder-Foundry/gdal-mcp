---
description: Delegate work to codex.
---

# Codex Two‑Layer Agent Policy

This document formalizes a two‑layer agent model where Cascade acts as the dispatcher and context manager, and Codex (MCP) acts as the workhorse solver. The goal is to maximize speed and reliability while maintaining safety, observability, and a great UX.

## Purpose
- Ensure repeatable, production‑safe collaboration between Cascade and Codex.
- Standardize how tasks are framed, delegated, executed, verified, and recorded.
- Prioritize correctness first, then performance and binary size.

## Scope
- Applies to all development, packaging, and diagnostic tasks where Codex MCP is available.
- Cascade remains the user‑facing agent and the single authority for tool usage and changes.

---

## Architecture Overview
- **Layer 1 — Cascade (Dispatcher/Context Manager)**
  - Owns context assembly, safety, and final execution.
  - Crafts Task Cards for Codex with acceptance criteria and an output contract.
  - Applies changes, runs commands/tests, updates memory, and reports back to the user.
- **Layer 2 — Codex (Workhorse Solver)**
  - Receives Task Cards and returns deterministic artifacts: diffs, commands, hooks/specs, tests, and rationale.
  - Does not run commands or mutate state directly; proposes actions for Cascade to apply.

---

## Roles & Responsibilities

### Cascade (Layer 1)
- **Context assembly**: Gather relevant files/snippets, logs (trimmed/tails), environment details (OS, Python, tool versions), recent diffs, and constraints.
- **Task planning**: Convert user requests into Task Cards with clear objectives and acceptance criteria.
- **Tool orchestration**: Decide which MCP tools to call and when; batch read‑only operations; serialize writes.
- **Safety gate**: Classify commands as safe/semi‑safe/unsafe. Never auto‑run unsafe commands. Validate patches before applying.
- **Execution & verification**: Apply diffs, run builds/tests, collect outputs, and determine pass/fail.
- **Memory & reporting**: Persist key decisions, artifacts, and outcomes; summarize for the user.

### Codex (Layer 2)
- **Deterministic outputs**: Follow the Output Contract precisely; provide fully specified diffs and artifacts.
- **Completeness**: Include all hidden imports, hooks, binaries/data, config, and verification steps required for success on a clean environment.
- **Transparency**: Provide rationale, risks, and assumptions; include a confidence score.
- **Non‑destructive**: Do not attempt to run commands or modify state; propose only.

---

## Interaction Protocol

- **MCP tools**: Use `codex` to start a session and `codex-reply` for follow‑ups. Cascade owns session lifecycle.
- **Single Source of Truth**: Task Cards are the authoritative input for Codex. Only Cascade composes them.
- **Granularity**: Prefer smaller, well‑scoped Task Cards. If scope expands, split into multiple cards.
- **Iteration**: If acceptance criteria are not met, Cascade provides new evidence (logs/diffs) via `codex-reply` and requests amendments.

---

## Task Card Template (used by Cascade)

```yaml
system_context:
  project: <name>
  env:
    os: <windows|linux|macos>
    python: <3.x>
    tools:
      pyinstaller: <ver>
      wine: <ver>
      others: [<...>]
  constraints:
    - <e.g., onefile, no admin installs, no internet, etc.>

objective: |
  <Clear, concise goal>

inputs:
  files:
    - path: <absolute-or-project-rel>
      purpose: <why relevant>
      snippet: |
        <bounded excerpt>
  logs:
    - name: <id>
      tail: |
        <last 100–200 lines>
  flags:
    - <current CLI flags/spec snippets>

acceptance_criteria:
  - <bullet list of testable outcomes>

output_contract:
  patches: v4a|unified
  commands: include safety_category
  tests: explicit commands + expected outcomes
  artifacts: full file contents when new
  risks: bullets
  confidence: 0.0–1.0
```

---

## Output Contract (required from Codex)

```json
{
  "proposedChanges": [
    { "path": "<file>", "format": "v4a|unified", "content": "<patch>" }
  ],
  "terminalCommands": [
    { "cmd": "<command>", "category": "safe|semi|unsafe", "rationale": "<why>" }
  ],
  "tests": [
    { "cmd": "<command>", "expect": ["<contains string>", "exit 0"] }
  ],
  "artifacts": [
    { "path": "<file>", "contents": "<full text>" }
  ],
  "risks": ["<item>", "<item>"] ,
  "assumptions": ["<item>"] ,
  "confidence": 0.0
}
```

- **Patches** must uniquely identify change hunks and avoid ambiguous context.
- **Commands** are proposals only; Cascade decides and runs them.
- **Tests** are runnable on target OS; expectations are explicit.
- **Artifacts** contain complete file content when creating new files.

---

## Execution Flow

1. **Intake** (Cascade)
   - Parse user request; gather context; create Task Card.
2. **Delegate** (Cascade → Codex)
   - Call `codex` with Task Card and Output Contract.
3. **Produce** (Codex)
   - Return patches/commands/tests/artifacts per contract.
4. **Apply & Verify** (Cascade)
   - Apply patches; run commands/tests; collect results.
5. **Iterate or Close**
   - If criteria unmet, send `codex-reply` with new logs/diffs; repeat.
   - If met, persist decisions and report to user.

---

## Safety & Guardrails

- **Command gating**: Unsafe commands (e.g., deletes, system installs) never auto‑run.
- **Patch validation**: Apply only when context matches exactly; fail fast on mismatch.
- **Secrets handling**: Never include credentials in prompts or artifacts; prefer env/secret managers.
- **File scope**: Only touch files listed in Task Cards unless explicitly expanded.

---

## Observability & Memory

- **Traceability**: Store Task Cards, Codex responses, applied patches, command outputs, and outcomes.
- **Metrics**: Track iteration count, time‑to‑fix, size deltas, regression rate.
- **Knowledge**: Promote recurring solutions to reusable playbooks/patterns.

---

## When to Offload vs Keep Local

- **Offload to Codex**
  - Complex packaging (PyInstaller hooks/specs), multi‑lib refactors, tricky dependency graphs.
  - Multi‑file architectural proposals with tests and migration steps.
- **Keep local (Cascade)**
  - Small edits, formatting, quick searches, simple flag tweaks, deterministic command runs.

---

## Versioning & Evolution

- Changes follow lightweight review: propose diff → discuss → approve → apply.
- Backwards‑compatible updates preferred; breaking changes announced in the summary.

---

## Operational Workflow (Codex Manager)

Use this checklist for every Codex‑delegated task. Cascade (you) is the dispatcher; Codex is the solver.

1) Intake & Scope
   - Gather: paths, key snippets, recent diffs, error logs (tail 100–200 lines), OS/tooling, constraints.
   - Decide granularity: split into small Task Cards if the scope spans more than ~2–3 files or >20 lines per file.
   - Define acceptance criteria and a minimal verification plan (compile, unit subset, CLI dry‑run, etc.).

2) Compose Task Card (authoritative input to Codex)
   - Include: objective, inputs (files/logs with bounded excerpts), constraints, acceptance criteria, Output Contract.
   - Always specify patch format (v4a recommended) and command safety categories.

3) Delegate to Codex
   - Start a new Codex session; for follow‑ups, use `codex-reply` and quote prior relevant snippets (not the whole file).
   - Prefer several small Task Cards over one large one; serialize writes, batch reads.

4) Apply & Verify
   - Validate patches against current files (unique context, imports at top, no mid‑file imports).
   - Apply diffs; compile or lint quickly; run minimal verification (dry‑run, CLI, unit subset).
   - If a gate fails, capture the exact failure tail and iterate with `codex-reply`.

5) Close & Record
   - Commit with a clear message; log decisions (what/why), and update TODOs.
   - Summarize results for the user; include follow‑up recommendations.

Guardrails
- Never auto‑run unsafe commands (installs, destructive ops).
- Keep patches minimal; avoid touching unrelated lines.
- No secrets in prompts; if necessary, use placeholders and env variables.

## Prompt Patterns Library

Use these templates verbatim and fill the marked fields. Keep prompts concise and executable.

Pattern: Fix/Refactor with Verification
```
Repository root: <abs path>

Task: <short statement>

Files to change:
- <path>: <why relevant>

Requirements:
- <bulleted functional/non‑functional requirements>

Acceptance criteria:
- <bulleted, testable outcomes>

Output Contract:
- Patches: v4a
- Commands: safe|semi|unsafe with rationale
- Tests: commands + expected output or exit codes
- Artifacts: full file contents for new files
```

Pattern: Investigate & Propose
```
Context:
- <logs tails>
- <file snippets>

Goal: Identify root cause and propose a minimal patch + verification plan.

Deliverables:
- Root cause summary
- One or more patch options (v4a)
- Minimal commands/tests to verify
- Risks/assumptions, confidence
```

Pattern: Multi‑step Migration (chunked)
```
Objective: <e.g., remove feature X, add Y>

Step 1: Discovery
- find/grep targets; inventory call sites; propose plan

Step 2: API/Enum updates
- patch enums/types; fix imports; compile

Step 3: Surfaces
- patch CLI/GUI; compile; dry‑run

Step 4: Cleanups & docs
- sweep docs; add guardrails/tests; final commit
```

## Chunking & Iteration Strategy

- Prefer ≤300 changed lines per commit. If larger, split by module or concern.
- Reads in parallel; writes are serialized. Always re‑read files before applying a patch Codex produced earlier.
- On failure, attach the exact error tail and current snippet to `codex-reply`.

## Failure Recovery Playbook

- Patch fails to apply → fetch fresh file, re‑anchor hunk, re‑ask Codex to rebase patch.
- Compile/lint fails → paste the exact error lines; ask Codex for a corrective patch only for the reported errors.
- Tests/dry‑run fail → paste failing output and expected behavior; request minimal fix.
- Ambiguity → ask Codex to propose options with trade‑offs and pick the smallest diff first.

## Quality Gates

- Syntax gate: `python3 -m compileall <touched files>` must pass.
- Lint gate (if configured): run quick lints; fix imports at top.
- Runtime gate: prefer dry‑run/CLI smoke over full test suites unless required.
- Safety gate: commands marked unsafe must never be auto‑run; prompt the user.

## Command Safety Matrix

- safe: read‑only, local compile/lint, dry‑run.
- semi: local write within repo, non‑destructive tooling.
- unsafe: installation, deletion, external calls with side‑effects.

## Observability & Memory Checklist

- Log decisions with rationale and implementation details.
- Update TODOs when tasks are added/completed; create follow‑ups for docs/tests.
- Summarize to the user with what changed, how verified, and next steps.

## Minimal SLAs
 
  - Codex responses should:
    - Conform to Output Contract.
    - Include a confidence score and risks.
    - Provide exact file paths and executable commands.
  - Cascade ensures:
    - Commands are safe to run and executed with correct cwd/env.
    - Verification is performed and outcomes are recorded.

---

## Appendix: MCP Tooling Notes

- Use `codex` to start and `codex-reply` to continue sessions; include prior context snippets and IDs.
- Prefer batched read‑only operations; serialize writes.
- Respect platform differences (Windows vs Linux vs Wine) and state acceptance criteria accordingly.

# Policies: Behavior & Guardrails for Autonomous Workflows

This directory defines **how** the agent should behave (tone, defaults, caution) and **what it must not do** (hard guardrails). These docs are **natural‑language first** so they’re easy to write and maintain. Your hooks (e.g., `hooks/pre.md`) load them and translate them into runtime switches; your building blocks stay single‑responsibility and code‑focused.

* `always.md` → standing guidance that shapes behavior (observability, “prefer X over Y”, skepticism level).
* `never.md` → crisp prohibitions with explicit, waivable exceptions.

Your existing config makes these policies actionable:

* `config/env.md` provides the workspace and tool paths the hooks rely on.&#x20;
* `config/verbs.md` is the verb router the hooks can sanity‑check before any workflow runs.&#x20;
* `conport/load.md` already summarizes current context—perfect for “preflight” signal + policy application.&#x20;
* `conport/sync.md` shows a clean pattern for delegating to building blocks without duplicating logic (a good pattern for how hooks should behave).&#x20;

---

## Philosophy

1. **Policies are meta, not mechanized.**
   Keep them human‑readable. Let hooks interpret them; don’t embed steps here. (Steps belong in `workflows/` or `workflows/atoms/`.)

2. **Bias to safety + clarity over “cleverness.”**
   Autonomous agents do best with clear constraints, not vague encouragements. If a rule matters, write it down.

3. **Waivers > hard locks (with receipts).**
   Most “never” rules should be *block‑by‑default* but **explicitly waivable** with a small input (e.g., `waive_never: ['spatial.algorithms']` or `allow_dangerous: true`). This keeps you productive without normalizing risky behavior.

4. **Short, testable, and observable.**
   Every rule should be easy to detect (“did we try to do X?”) and produce lightweight telemetry (e.g., “\[STEP\_OK] …”) so you can debug runs quickly.

5. **No duplication with building blocks.**
   Policies tell the agent *how to think*, not *what to run*. Your blocks (`load`, `update`, `log`, `search`, `relate`, `export`) remain single‑purpose and composable.&#x20;

---

## What belongs in `always.md`

Use `always.md` to set the “operating system” for the agent:

* **Observability & etiquette**
  “Acknowledge each major step with a one‑liner and summarize intended actions before applying changes.”

* **Skepticism & defaults**
  “When unsure, propose 2–3 options with trade‑offs. Prefer idempotent edits and reversible changes.”

* **Libraries & reuse**
  “Prefer battle‑tested libraries over bespoke algorithms (e.g., GDAL/PDAL/rasterio/pyproj for geospatial) unless explicitly waived.”

* **Feedback loop**
  “If a constraint blocks progress, surface the rule ID and a safe waiver suggestion rather than silently proceeding.”

> Keep it descriptive and concise—paragraphs or bullet points. The **pre hook** reads this file and turns it into small runtime flags (“verbosity”, “skepticism\_level”, “ack\_each\_step”) before the main workflow runs. It can also fetch a quick context snapshot via `load_conport` to ground behavior.&#x20;

---

## What belongs in `never.md`

This is your enforceable safety net. Each rule should be:

* **Short**: one sentence plus rationale.
* **Specific**: concrete action that can be detected.
* **Labeled**: a stable `id` (e.g., `spatial.algorithms`, `git.force_push`).
* **Scoped**: define what counts as a violation and known exceptions.
* **Severed**: `severity: block | warn`.

Examples you described (good fits):

* `spatial.algorithms` (**block**)
  Do not implement custom spatial interpolation or CRS math. Use GDAL/PDAL/rasterio/pyproj unless `waive_never: ['spatial.algorithms']`.

* `git.force_push` (**block**)
  Do not force‑push or rewrite history unless `allow_dangerous: true`.

* `recommendations.staleness` (**warn**)
  If making library or reference recommendations, check freshness via available MCPs; warn when you can’t verify currency.

> The **pre hook** loads `never.md`, compiles a denylist, and enforces it throughout the run; the **post hook** records any warnings/blocks into ConPort activity so you have an audit trace (via your existing `sync`/`update` patterns). &#x20;

---

## Suggested authoring pattern (lightweight & optional)

Policies remain natural language, but adding a tiny metadata header at the top helps hooks reason about them without making the docs feel “machiney”.

For `always.md` (optional front‑matter):

```
---
policy: always
version: 1
telemetry: normal   # quiet | normal | verbose
skepticism: high    # low | medium | high
ack_each_step: true
---
```

For `never.md` (rule cards; keep the prose body below for humans):

```
---
policy: never
version: 1
rules:
  - id: spatial.algorithms
    severity: block
    rationale: "Avoid bespoke geospatial math; reuse proven libs."
    waiver: "waive_never: ['spatial.algorithms']"
  - id: git.force_push
    severity: block
    waiver: "allow_dangerous: true"
  - id: recommendations.staleness
    severity: warn
---
```

Hooks can treat this header as **hints**; if absent, they still parse the human text and proceed.

---

## Lifecycle & placement

* **Load order per run:** `always.md` → `never.md` → `hooks/pre.md` → workflow → `hooks/post.md`.
  If there’s a conflict, **never > workflow > always**.
  The pre hook should also validate `env` and `verbs` so routing fails fast with a clear error. &#x20;

* **Change management:** bump a `version:` number in the front‑matter and write a one‑line note in the body. Let the post hook record that change to recent activity so it’s visible in context loads.&#x20;

* **Scope creep check:** if you find yourself writing steps (“run tests”, “log decision”) in policies, that content belongs in a **hook** or **workflow**, not here.

---

## Why this design works

* It keeps **policy** (human‑readable, high‑level) separate from **mechanics** (your YAML building blocks).
* Hooks become simple routers and validators that **consume** policy/config (`env.md`, `verbs.md`), then call existing blocks (`load`, `update`, `sync`, etc.)—no duplication. &#x20;
* You get **observability** without noise, and **guardrails** without being hand‑tied (thanks to waivers).
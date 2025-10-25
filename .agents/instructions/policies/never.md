# never.md

**Purpose**
This file defines strict guardrails: actions that should **never** be taken unless explicitly overridden. These rules are meant to keep workflows safe, predictable, and consistent with human development practices.

If a rule is violated, the agent must:

* **Stop** the risky action,
* **Explain** which rule was triggered (by ID), and
* **Suggest** safe alternatives or how to explicitly waive the rule.

---

## Guardrails

### 1. **No Reinventing Established Algorithms** (`algorithms.reinvent`)

* Do not re-implement well-understood algorithms or utilities that have established library support (e.g., sorting, regression, spatial transforms).
* Use battle-tested libraries like `numpy`, `pandas`, `scipy`, `geopandas`, GDAL, PDAL, or PROJ instead.
* **Rationale**: Reinvented algorithms are error-prone, less maintainable, and harder for humans and agents to collaborate on.
* **Override**: Allowed only if explicitly instructed to, or if no suitable library exists.

---

### 2. **No Destructive Git Actions Without Explicit Approval** (`git.destructive`)

* Never force-push, delete branches, or rewrite commit history without confirmation.
* Always prefer non-destructive operations (merge, squash-merge, rebase with backups).
* **Rationale**: Prevents accidental loss of history and team disruption.
* **Override**: Requires explicit approval flag (e.g., `allow_dangerous: true`).

---

### 3. **No Unverified Dependencies** (`dependencies.unverified`)

* Do not introduce libraries, tools, or packages without verifying source, version, and compatibility.
* Always check ecosystem reputation (stars, contributors, maintenance frequency).
* **Rationale**: Avoids supply chain risk and brittle builds.
* **Override**: Allowed if a human explicitly approves the dependency.

---

### 4. **No Silent Failures** (`execution.silent_fail`)

* Do not ignore errors or continue silently after a failure.
* Always explain what failed, why it may have failed, and possible fixes.
* **Rationale**: Transparency and debuggability are critical.
* **Override**: None. Errors must always be surfaced.

---

### 5. **No Out-of-Scope Code Generation** (`scope.out_of_bounds`)

* Do not create large systems, speculative features, or tangential code unless explicitly asked.
* Stay within the current project’s scope and conventions.
* **Rationale**: Prevents scope creep and wasted effort.
* **Override**: Requires explicit human instruction.

---

### 6. **No Ignoring Policy or Context** (`policy.ignore`)

* Do not skip or override `always.md` rules, `env.md` configuration, or `verbs.md` mappings.
* **Rationale**: Ensures consistent adherence to defined environment and behavior.
* **Override**: None. Context and policy must always be respected.

---

## Waivers

* Rules can only be waived if explicitly allowed in their description.
* Waivers should be recorded automatically in ConPort logs with the **rule ID** and rationale for the override.
* Example waiver:

  ```yaml
  waive_never:
    - algorithms.reinvent
  ```

---

## Notes

* **Priority**: If rules conflict, `never.md` overrides `always.md`. Safety beats convenience.
* **Auditability**: Hooks (`pre` and `post`) should read this file and record any violations or waivers into ConPort logs for traceability.
* **Extensibility**: Add new rules here as needed, keeping them **short, specific, and enforceable**.

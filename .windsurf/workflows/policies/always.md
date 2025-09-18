# always.md

**Purpose**
This file defines standing policies that are **always in effect** during workflow execution. Unlike pre/post hooks (which run concrete steps), these guidelines establish the *behavioral baseline* the agent should internalize before carrying out any task.

---

## Standing Instructions

1. **Acknowledge Actions Verbally**

   * Before and after executing each step, provide a short confirmation of what is happening.
   * Example: *“Running lint on `src/` with `ruff` … Done.”*
   * This ensures traceability and helps humans (and agents) debug workflow runs.

2. **Log Significant Events Automatically**

   * Use the ConPort `log_conport` building block to record decisions, patterns, and progress **without requiring explicit human prompting**.
   * Favor concise but meaningful entries that explain the rationale for important steps.

3. **Favor Established Libraries and Tools**

   * **Do not implement algorithms from scratch** unless explicitly asked to, or unless **no suitable, safe library exists**.
   * For numerical, data processing, or ML tasks: prefer `numpy`, `pandas`, `scipy`, `scikit-learn`, `rasterio`, `geopandas`, etc.
   * For geospatial operations: use GDAL/PDAL, PROJ, or equivalent rather than hand-rolled math.
   * This improves reliability, code readability, and alignment with industry culture.

4. **Idempotency as a Default**

   * Assume every workflow may be re-run.
   * Design or suggest solutions that **check state before acting** to prevent duplication, data loss, or runaway side effects.

5. **Use `sequential-thinking` for complex tasks**

   * If the agent has access to the `sequential-thinking` MCP, use it to guide the agent through complex tasks.
   * If the agent does not have access to `sequential-thinking` tools, create and use a `plan.md` to track progress and reflect on decisions.

6. **Provide Debugging Context**

   * Where possible, summarize what is being done in plain language.
   * Highlight assumptions and defaults used (e.g., “Using `/usr/bin/npx` detected in env.md”).
   * If an action fails, suggest likely causes and next steps before retrying.

7. **Encourage Clarity in Output**

   * Prefer structured responses (lists, bullet points, numbered steps) when conveying multiple ideas.
   * Keep explanations brief but sufficient for another developer to understand what was done and why.

---

## Notes

* These rules do not replace **pre/post hooks** (operational logic) but **apply globally** to all workflows.
* If a workflow or policy conflicts, the more specific instruction takes precedence (e.g., `/refactor` dry-run logic).
* Agents should treat these as part of their **operating personality** when executing tasks.

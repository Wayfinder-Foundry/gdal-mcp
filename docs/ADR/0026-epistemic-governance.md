---
status: proposed
date: 2025-10-19
updated: 2025-10-22
decision-makers: [jgodau, cascade-ai]
tags: [epistemology, governance, prompting, fastmcp, agent-autonomy]
---

# ADR-0026: Epistemic Governance Through Thin Prompting and Justification

## Context

GDAL-MCP requires a governance layer that ensures scientific correctness without constraining
agent reasoning. Traditional approaches (prescriptive prompts, MRKL/ReAct scaffolding) were
designed for weaker models and become increasingly limiting as model capability grows.

The epistemic governance framework (`docs/design/epistemology/`, `docs/design/prompting/`)
establishes a different approach:

- **Thin global prompting** establishes epistemic posture without procedural templates
- **Risk classification** detects when justification is required at tool boundaries
- **Preflight prompts** surface justification only when risk exists and cache is missing
- **Justification schema** (`JUSTIFICATION_SCHEMA.md`) captures methodological reasoning
- **Domain methodology docs** provide on-demand scaffolding, never pre-loaded
- **Receipts and persistence** enable observability and reuse

This architecture trusts agent autonomy while requiring epistemic accountability when stakes
warrant it. As models improve, the same infrastructure scales from "verify methodology" to
"discover better methodology."

## Decision

### 1. Adopt Thin Prompting as the Interface Layer

The global prompt remains intentionally lightweight to:
- Establish epistemic posture (awareness of justification requirements)
- Avoid prescribing reasoning procedures
- Preserve forward-compatibility with increasingly capable models
- Allow methodological emergence rather than compliance

**Implementation**: Global prompt declares epistemic stance; no ReAct loops, CoT templates,
or step-by-step workflows.

### 2. Implement Risk-Aware Justification at Tool Boundaries

Tools classified as epistemically risky (CRS/datum, resampling, hydrology, aggregation) trigger
justification generation when:
- No cached justification exists for the input hash
- Cached justification exists but is stale (input hash mismatch)

**Implementation**: 
- Risk classifier (`mcp/risk/`) maps tool invocations to risk classes
- Input hashing ensures cache validity per epistemic context
- Preflight prompt generates justification object on-demand
- Justification persisted and referenced in execution receipt

### 3. Standardize on Universal Justification Schema

All epistemic reasoning externalizes through a single schema covering:
- Domain (risk class identifier)
- Intent (what property/behavior must be preserved)
- Assumptions (known, uncertain, dependencies)
- Candidate methods (considered, rejected with reasons)
- Selected method (choice, rationale, tradeoffs)
- Epistemic status (confidence, residual uncertainty, revisit conditions)

**Implementation**: Pydantic models enforce schema; methodology docs provide domain examples;
agents generate conforming objects via preflight prompts.

### 4. Treat Methodology Docs as On-Demand Resources

Methodology guidance (`docs/design/epistemology/*.md`) is:
- Referenced by justifications (not embedded in prompts)
- Consulted by agents when reasoning about risk classes
- Updated as domain understanding evolves
- Never pre-loaded into global context

**Implementation**: Resource URIs point to methodology; agents discover via MCP resources;
justifications cite specific methodology sections.

### 5. Emit Machine-Readable Receipts for All Risky Operations

Every tool execution in an epistemic risk class produces a receipt containing:
- Risk class and input hash
- Decision state (proceed, warn, blocked)
- Justification reference (if generated or cached)
- Execution outcome and metadata

**Implementation**: Receipts logged to stderr, optionally stored, enable observability and
educational transparency.

### 6. Preserve Agent Autonomy Over Methodological Choice

The system does not:
- Prescribe specific algorithms or workflows
- Require adherence to canonical methods
- Inject step-by-step reasoning templates
- Pre-constrain the solution space

The system does:
- Require articulation of reasoning when risk exists
- Validate conformance to justification schema
- Cache decisions to avoid redundant prompting
- Surface methodology docs as optional scaffolds

**Implementation**: Agents select methods freely; justifications document choices;
enforcement validates structure, not content.

## Consequences

### Positive

- **Preserves reasoning autonomy**: Agents think in their own way, constrained only by
  justification requirements
- **Scales forward**: Same architecture works for verifying known methods and discovering
  novel ones
- **Minimizes cognitive overhead**: Justification only when risk present and cache missing
- **Enables observability**: Receipts make scientific choices auditable without blocking work
- **Reduces prompt brittleness**: Thin prompts age better than procedural templates
- **Supports iterative refinement**: Justifications can be updated as evidence improves

### Negative

- **Requires disciplined schema design**: Justification structure must support diverse
  reasoning styles
- **Defers some validation to runtime**: Cannot pre-validate all methodological choices
- **Assumes model competence**: Architecture trusts agents to reason scientifically when
  prompted
- **Adds implementation complexity**: Risk classification, hashing, caching, preflight logic

### Neutral

- **Shifts from "guide the agent" to "hold the agent accountable"**: Different mental model
  for developers
- **Documentation becomes runtime resource**: Methodology docs are live references, not specs
- **Testing focuses on schema compliance**: Not procedure adherence

## Implementation Path

### Phase 1: Core Infrastructure (Tasks 2001-2004)
- Risk classification and input hashing
- Justification schema and validation
- Disk-backed storage with caching
- Middleware enforcement and receipts
- Thin global prompt and preflight template

### Phase 2: Tool Integration (Tasks 2005-2008)
- Wrap reprojection tool with enforcement
- Extend to resampling, hydrology, aggregation
- Validate receipt generation and observability
- Iterate on justification examples

### Phase 3: Documentation & Refinement
- Update methodology docs with justification examples
- Capture prompt regression suite for preflight behavior
- Document epistemic governance patterns for contributors
- Refine schema based on real-world justifications

## Status

Proposed — philosophy documented in `docs/design/epistemology/README.md` and
`docs/design/prompting/README.md`; implementation tasks to follow.

## References

- `docs/design/epistemology/README.md` — Epistemic governance manifesto
- `docs/design/prompting/README.md` — Prompting as interface layer
- `docs/design/prompting/TLDR.md` — Quick reference
- `docs/design/prompting/DIAGRAM.md` — Flow visualization
- `docs/design/epistemology/JUSTIFICATION_SCHEMA.md` — Schema definition
- `docs/design/epistemology/RISK_CLASSES.md` — Risk taxonomy
- Methodology docs: `CRS.md`, `RESAMPLING.md`, `HYDROLOGY.md`, `AGGREGATION.md`

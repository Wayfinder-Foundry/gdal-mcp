# JUSTIFICATION_SCHEMA.md

*A reusable structure for scientific reasoning in geospatial agents*

## 1. Purpose

This schema defines **how an agent externalizes epistemic reasoning** — not for logging, not for auditing alone, but for *transparency, revision, and scientific growth.*

It provides a universal format the agent can use whenever methodology is required.
Every domain-specific justification (CRS, resampling, hydrology, aggregation) becomes an **instantiation** of this schema.

This enables:

* epistemic consistency across workflows,
* portability across models/contexts,
* and long-term refinement of reasoning.

---

## 2. Epistemic Design Principles

This schema assumes:

1. **Reasoning precedes tooling** — the *justification* is the scientific act; execution is an implementation detail.
2. **Correctness is not binary** — validity is contextual and bounded by assumptions.
3. **Uncertainty is part of epistemic honesty** — a method is justified *alongside the conditions under which it may later need revision.*
4. **Scientific defensibility requires explicit articulation**, not silent inference.

---

## 3. The Justification Schema (Abstract Form)

```yaml
epistemic_justification:
  domain: <which epistemic risk class this reasoning belongs to>
  intent:
    description: <what property or outcome must be preserved or respected>
    context: <what problem or data condition motivates this requirement>

  assumptions:
    known: [ list of assumptions that must hold true for this to remain valid ]
    uncertain: [ list of assumptions the agent *cannot guarantee* ]
    dependencies: [ CRS, datum, resolution, surface integrity, etc. ]

  candidate_methods:
    considered: [ brief list of possible approaches or CRSs / methods ]
    rejected:
      - method: <name or description>
        reason: <why it was not chosen>

  selected_method:
    name: <method / CRS / approach selected>
    rationale: <why this method best satisfies the stated intent + assumptions>
    tradeoffs: <what is preserved vs sacrificed>

  epistemic_status:
    confidence_level: <low | medium | high>
    residual_uncertainty_sources: [ factors that constrain confidence ]
    conditions_for_revisit: [ when a future revision would be appropriate ]
```

This is not a procedural form — it is a *cognitive artifact.*
A representation of *thinking*, not a worksheet.

---

## 4. Notes on Interpretation

| Section             | Why it exists                                                        |
| ------------------- | -------------------------------------------------------------------- |
| `intent`            | anchors reasoning in purpose rather than habit                       |
| `assumptions`       | makes the geodesy/topology/statistics *explicit instead of implicit* |
| `candidate_methods` | preserves non-chosen alternatives (prevents tunnel vision)           |
| `selected_method`   | carries the justification logic                                      |
| `epistemic_status`  | makes uncertainty *visible and revisitable*                          |

---

## 5. Lifecycle of a Justification Object

The justification object is expected to:

| Phase   | Action                                                            |
| ------- | ----------------------------------------------------------------- |
| Create  | when an epistemic trigger fires (uncertainty or risk class)       |
| Use     | drives selection of method/tool                                   |
| Persist | becomes a durable memory capsule                                  |
| Revisit | may be revised when new constraints, data, or methodology appears |
| Improve | future models can refine the rationale, not just replace it       |

This design **future-proofs reasoning** against both model drift and domain shifts.

---

## 6. Why this Structure Matters

This schema enables:

* reproducibility of reasoning, not just execution
* peer-alignment with human geospatial experts
* persistent scientific improvement
* agent self-reflection across time

It transforms the agent from:
**operator → methodologist → researcher**

---

## 7. Forward Compatibility

This schema is intentionally domain-general.
Future MCPs or methodology modules can reuse it outside geospatial processing (e.g. ecological inference, uncertainty-aware hazard modeling, spatial optimization).

It is designed to be a **living epistemic substrate**, not a static template.

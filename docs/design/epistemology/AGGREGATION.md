# AGGREGATION.md

*Methodological scaffold for epistemically grounded aggregation and statistical summarization*

## 1. Purpose

Aggregation is not merely the reduction of resolution — it is the **construction of meaning** through selective compression of information.
Where CRS protects *space*, resampling protects *signal*, and hydrology protects *process*, aggregation protects **interpretation**.

Every aggregation method encodes a belief about:

> “What does it *mean* for many measurements to become one?”

This methodology ensures that belief is explicit rather than implicit.

---

## 2. When Aggregation Methodology Is Required

Escalation is required when:

* statistics are used to **replace** raw surface values,
* decision-support or modeling relies on a *single summary number*,
* spatial heterogeneity may be meaningful (not noise),
* hydrologic or geomorphic extremes matter more than central tendency,
* “mean” is not obviously a correct epistemic choice.

This maps to the **Interpretation / Aggregation** epistemic risk class recorded in `EPISTEMIC_RISK_CLASSES.md` and is executed under the policy described in `IMPLEMENTATION_PLAN.md`.

---

## 3. Epistemic Prompting Questions

Before aggregation, the agent should surface:

1. **What property of the distribution matters?**
   (central tendency, extremes, thresholds, dominant class, etc.)

2. **Is the surface uniform, or is local variability part of the meaning?**

3. **Should aggregation reflect *representation* or *risk*?**
   (Median vs 95th percentile is a *belief* about impact)

4. **Is the goal descriptive (what is typical?) or operational (what governs behavior?)**

5. **Would a different statistical operator change the *interpretation*?**
   (not the numeric value — the *meaning*)

6. **Under what future contexts should this summarization be revisited?**

---

## 4. Schema Mapping for Aggregation

| Schema Field        | Interpretation                                          |
| ------------------- | ------------------------------------------------------- |
| `domain`            | always `aggregation_justification`                      |
| `intent`            | what *interpretive truth* the aggregation is preserving |
| `assumptions`       | what is considered “signal” vs “noise” in variability   |
| `candidate_methods` | expressed as epistemic meaning, not statistic name      |
| `selected_method`   | which interpretation is being “privileged”              |
| `epistemic_status`  | conditions for future revision                          |

---

## 5. Structured Reasoning Workflow

1. Identify **what aspect of the distribution is meaningful**
2. Determine whether central tendency or extremes encode truth
3. Enumerate interpretive approaches (not statistical labels)
4. Reject those that contradict epistemic intent
5. Select method aligned with scientific objective
6. Preserve uncertainty and revision triggers

---

## 6. Worked Example (Watershed Aggregation)

**Scenario:**
A watershed’s slope characteristics are being summarized to support flood / erosion risk estimation.

```
epistemic_justification:
  domain: aggregation_justification

  intent:
    description: "Capture hydrologically relevant slope behavior, not just average terrain."
    context: "Aggregation will influence hydrologic risk interpretation, especially peak flow."

  assumptions:
    known:
      - "Erosion, runoff velocity, and channelization are driven by steeper portions of terrain."
      - "Mean slope underrepresents hydrologically dominant behavior."
    uncertain:
      - "Exact spatial threshold for extreme-driven contribution unclear."
    dependencies:
      - "Interpretation hinges on tail behavior, not central tendency."

  candidate_methods:
    considered:
      - "central tendency representation"
      - "dominant-behavior representation"
      - "peak-condition representation"
    rejected:
      - method: "central tendency representation"
        reason: "Hides hydrologically controlling features; erases risk-bearing signal."

  selected_method:
    name: "dominant-behavior representation (e.g., median or upper-quartile summary)"
    rationale: "Better reflects geomorphic control on runoff mechanics."
    tradeoffs: "Hydraulically inactive flat areas underrepresented; acceptable for hydrology-first context."

  epistemic_status:
    confidence_level: "medium"
    residual_uncertainty_sources:
      - "Exact percentile sensitivity unvalidated for this basin morphology."
    conditions_for_revisit:
      - "If field-calibrated hydrology or fluvial geomorphology priors become available."
      - "If purpose shifts from risk interpretation to landform description."
```

---

## 7. When Aggregation Does *Not* Require Epistemic Justification

Justification is not required when:

* aggregation is purely visual / cartographic,
* the statistic is noninterpretive (e.g., counting pixels),
* heterogeneity is known to be irrelevant to outcome,
* no modeling or inference is downstream,
* aggregation is reversible or optional.

---

## 8. Forward Compatibility

Aggregation is the most philosophically flexible of the four methodologies and should be expected to evolve as:

* models perform **distribution-shape reasoning** (not scalar reduction),
* risk-aware summaries become first-class primitives,
* hydrology and ecology workflows converge,
* uncertainty becomes quantitatively tracked.

This scaffold ensures aggregation remains:
✅ transparent
✅ justifiable
✅ revisable
✅ scientifically intelligible

rather than **opaque and habitual.**

---

## Related References

- **Risk Registry**: `EPISTEMIC_RISK_CLASSES.md`
- **Implementation Blueprint**: `IMPLEMENTATION_PLAN.md`

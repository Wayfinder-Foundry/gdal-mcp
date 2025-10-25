# HYDROLOGY.md

*Methodological scaffold for hydrologic realism and surface-process correctness*

## 1. Purpose

Hydrologic conditioning is the transformation of a *measured surface* into a *hydrologically valid surface*.
This is not algorithmic cleanup — it is the enforcement of **process truth**: water must be able to flow as it would in the real landscape.

A DEM may be *geometrically correct* but **hydrologically wrong** due to:

* sampling artifacts,
* lidar noise,
* insufficient resolution,
* digitizing discontinuities,
* or artificial barriers (roads/culverts not represented).

This methodology ensures the agent justifies ***why*** and ***how*** hydrologic continuity is restored.

---

## 2. When Hydrologic Methodology Is Required

Escalation to methodology is required when:

* hydrologic derivatives (flow direction, flow accumulation, stream extraction, basins) will be computed,
* depressions may be ambiguous (natural vs artifact),
* sinks affect headwaters, not just trunk streams,
* connectivity is uncertain or scale-dependent,
* downstream hydrology could change based on correction strategy.

This maps to the **Topology / Hydrology epistemic risk class** documented in `EPISTEMIC_RISK_CLASSES.md` and is governed operationally via `IMPLEMENTATION_PLAN.md`.

---

## 3. Epistemic Prompting Questions

Before conditioning, the agent should surface:

1. **Is this surface intended to represent physical hydrology, or literal sampled elevation?**
2. **Are depressions likely to be *real terrain* or *artifact noise*?**
3. **Is preserving microtopography more important than removing local discontinuities?**
4. **Does hydrologic continuity matter locally or basin-wide?**
5. **Should depressions be *preserved*, *filled*, or *breached* — and *why*?**
6. **Under what future conditions should this choice be revisited?**
   (e.g., higher resolution DEM, culvert integration, fluvial reinforcement)

---

## 4. Mapping the Epistemic Schema to Hydrology

| Schema Field        | Interpretation in Hydrology                                           |
| ------------------- | --------------------------------------------------------------------- |
| `domain`            | always `hydrology_conditioning_justification`                         |
| `intent`            | whether hydrologic realism or literal surface fidelity is prioritized |
| `assumptions`       | what is considered “real” vs "artifact" depressions                   |
| `candidate_methods` | expressed as *interpretive intent*, not algorithm names               |
| `selected_method`   | articulation of *why* one hydrologic worldview is chosen              |
| `epistemic_status`  | whether decision is provisional or stable                             |

---

## 5. Structured Reasoning Workflow

1. Identify whether depressions are hydrologically meaningful
2. Assess whether continuity or depression preservation should dominate
3. List interpretive approaches (preserve / restore / enforce)
4. Reject those that contradict the hydrologic intent
5. Justify selected conditioning method
6. Declare residual uncertainty and revision triggers

---

## 6. Worked Example (Headwater Sensitivity)

**Scenario:**
A DEM contains shallow depressions that interrupt flow path initiation in headwater basins.

```
epistemic_justification:
  domain: hydrology_conditioning_justification

  intent:
    description: "Restore hydrologic continuity where depressions are artifacts, while preserving terrain realism."
    context: "DEM will drive flow routing in a headwater-dominated catchment."

  assumptions:
    known:
      - "High-frequency sinks in headwaters are likely lidar sampling artifacts."
      - "Hydraulic realism requires continuous downgradient pathways."
    uncertain:
      - "Some depressions may be true geomorphic features (wetlands/peat pockets)."
    dependencies:
      - "Microtopography influences drainage initiation more than trunk direction."

  candidate_methods:
    considered:
      - "preserve-depression realism"
      - "restore surface continuity"
      - "enforce drainage connectivity"
    rejected:
      - method: "preserve-depression realism"
        reason: "Risk of preserving noise; interrupts headwater routing."
      - method: "enforce drainage connectivity"
        reason: "Too aggressive; flattens terrain signal beyond hydrologic realism."

  selected_method:
    name: "restore surface continuity (selective filling)"
    rationale: "Removes artifact depressions without over-carving; retains natural slope breaks."
    tradeoffs: "True wetlands may be partially normalized; acceptable given headwater routing priority."

  epistemic_status:
    confidence_level: "medium"
    residual_uncertainty_sources:
      - "Wetland presence cannot be confirmed without ancillary data."
    conditions_for_revisit:
      - "If ancillary hydrology (NHD, culvert inventory, or field data) becomes available."
      - "If future resolution improves sub-basin terrain detail."
```

---

## 7. When Hydrology Conditioning Does *Not* Require Epistemic Justification

Escalation is not necessary when:

* hydrology is not being derived,
* DEM is already hydrologically enforced by authoritative workflow,
* depressions are known real geomorphology (karst, marsh, kettle lake),
* conditioning is *post-processing* after hydrologic modeling (not pre-conditioning).

---

## 8. Forward Compatibility

Hydrology methodology is expected to evolve more than CRS or resampling because future models may:

* infer culverts/bridges from context,
* blend terrain with hydrography networks,
* use geomorphic priors to distinguish “structural” vs “spurious” sinks,
* dynamically condition DEMs based on basin context.

This schema protects forward evolution by:
✅ keeping interpretation primary,
✅ recording uncertainty,
✅ enabling revision when evidence improves.

---

## Related References

- **Risk Registry**: `EPISTEMIC_RISK_CLASSES.md`
- **Implementation Blueprint**: `IMPLEMENTATION_PLAN.md`



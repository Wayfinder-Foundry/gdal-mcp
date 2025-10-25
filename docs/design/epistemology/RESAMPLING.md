# RESAMPLING.md

*Methodological scaffold for epistemically grounded resampling and resolution changes*

## 1. Purpose

Resampling is not a formatting change — it is a **statement about what information is preserved when the spatial lattice is reconstructed.**
If a DEM encodes real-world surface energy, slope discontinuity, microtopography, or drainage structure, resampling directly affects *physical truth*, not just visual appearance.

Most silent GIS errors occur here because interpolation is assumed to be neutral.
It is not.
Each resampling method encodes a **theory of what is “important” in the data.**

This methodology ensures that resampling reflects the **intended scientific meaning** of the raster.

---

## 2. When Resampling Methodology is Required

Epistemic escalation is required when:

* the raster encodes *physical signal* (terrain/hydrology, hazards, geophysics),
* slope/flow/gradient will be derived downstream,
* values represent measurement rather than classification,
* spatial frequency structure matters (fine-scale terrain / headwaters / breaks),
* up/down-sampling alters interpretive resolution.

This corresponds to the **Resolution / Resampling epistemic risk class** in `EPISTEMIC_RISK_CLASSES.md` and follows the governance flow in `IMPLEMENTATION_PLAN.md`.

---

## 3. Epistemic Prompting Questions

Before selecting any resampling method, the agent should surface:

1. **What property of the raster must be preserved?**
   (classification fidelity, terrain realism, gradient continuity, statistical representativeness, etc.)

2. **Does the raster encode *physical measurement* or *categorical abstraction*?**

3. **Is high-frequency terrain signal important?**
   (headwaters, gullies, local maxima/minima → hydrology sensitive)

4. **Are we upsampling or downsampling (and is this reversible)?**

5. **Will smoothing alter scientific interpretation downstream?**

6. **Under what conditions should a future revision occur?**
   (e.g., realigned DEM, corrected LiDAR base, multi-scale analysis)

---

## 4. Mapping Schema → Resampling Context

| Schema Field        | Resampling Interpretation                                   |
|---------------------|-------------------------------------------------------------|
| `domain`            | always `resampling_justification`                           |
| `intent`            | what information must survive the spatial transform         |
| `assumptions`       | physical vs categorical meaning of pixels                   |
| `candidate_methods` | NOT “nearest/bilinear/cubic” → but the *property preserved* |
| `selected_method`   | which preservation type aligns with intent                  |
| `epistemic_status`  | residual uncertainty + when to revisit choice               |

---

## 5. Structured Reasoning Workflow

1. Identify whether raster encodes *signal* or *category*
2. Determine which *aspect of truth* must survive (value, gradient, topology, shape)
3. Consider candidate preservation strategies
4. Reject inappropriate resampling types explicitly
5. Select the method aligned to epistemic intent
6. Document uncertainty + revision triggers

---

## 6. Worked Example (DEM → slope → hydrology)

**Scenario:**
A DEM being resampled before slope and flow routing are computed.

```
epistemic_justification:
  domain: resampling_justification

  intent:
    description: "Preserve microtopography and slope fidelity required for accurate drainage direction."
    context: "Upsampling DEM before hydrology workflow; terrain signal drives flow routing."

  assumptions:
    known:
      - "DEM contains high-frequency terrain detail relevant to drainage structure."
      - "Hydrologic derivatives depend on local slope accuracy."
    uncertain:
      - "Input DEM may include sensor noise at sub-pixel scale."
    dependencies:
      - "Smoothing may erase headwater initiation points."

  candidate_methods:
    considered:
      - "classification-preserving (nearest-value semantics)"
      - "gradient-preserving (bilinear value continuity)"
      - "smoothness-prior (cubic / spline)"
    rejected:
      - method: "smoothness-prior"
        reason: "Introduces artificial terrain continuity → erases micro-basins."
      - method: "classification-preserving"
        reason: "Appropriate for categorical rasters, not continuous terrain."

  selected_method:
    name: "gradient-preserving interpolation (bilinear)"
    rationale: "Minimizes smoothing while preserving local slope continuity; hydrologically stable."
    tradeoffs: "Very small blurring of extremely small discontinuities; acceptable within DEM resolution limits."

  epistemic_status:
    confidence_level: "medium"
    residual_uncertainty_sources:
      - "Edge-case microtopography may still be lost if resolution gap is large."
    conditions_for_revisit:
      - "If later LiDAR integration provides finer source DEM."
      - "If drainage enforcement requires explicit sink/breach review after resampling."
```

---

## 7. When Resampling Escalation Is *Not* Required

No methodology justification is needed when:

* data is categorical and transformation is classification-preserving,
* resampling is for map display only,
* resolution is unchanged (copy),
* values are symbolic (e.g., mask/grids, boolean layers),
* output is not used for measurement-derived inference.

---

## 8. Forward Compatibility

This scaffold is intentionally **property-first**, not algorithm-first.
A future model may:

* discover new interpolation families,
* derive adaptive kernels from local geomorphology,
* learn hybrid frequency-aware methods,

…and the schema will still apply, because **the epistemic commitment is to what is preserved, not how.**

This is how the agent remains capable of *scientific evolution.*

---

## Related References

- **Risk Registry**: `EPISTEMIC_RISK_CLASSES.md`


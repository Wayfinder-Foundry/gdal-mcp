# CRS.md

*Methodological scaffold for epistemically grounded CRS and datum selection*

## 1. Purpose

This document defines **how** an agent justifies a chosen Coordinate Reference System (CRS) or datum transformation when epistemic risk is present.

CRS selection is not a formatting decision — it is a *scientific commitment* about which geospatial property must remain truthful. In hydrology, reprojection can change drainage structure, slope, accumulation, and pour point location even when the raster “looks correct.”

This methodology ensures the CRS choice is:

* *motivated* (linked to a geospatial objective),
* *transparent* (assumptions surfaced),
* *defensible* (tradeoffs acknowledged), and
* *revisable* (uncertainty preserved).

---

## 2. When CRS Methodology is Required

CRS justification is required whenever **space is transformed in a way that could alter the interpretation of physical processes**, especially when:

* hydrology, slope, or drainage depends on spatial fidelity,
* area or distance accuracy is essential to the model,
* vertical alignment with a geoid matters,
* projected vs. geographic assumptions change meaning.

This corresponds to the **CRS / DATUM epistemic risk class** in `EPISTEMIC_RISK_CLASSES.md` and is operationalized through the controls described in `IMPLEMENTATION_PLAN.md`.

---

## 3. Epistemic Prompting Questions

Before filling the justification schema, the agent should explicitly reason through:

1. **What scientific property must be preserved?**
   (distance, area, angular relationships, hydrologic realism, etc.)

2. **What downstream analysis depends on the CRS?**

3. **What datum assumptions already exist in the source data?**

4. **Is a vertical datum involved?**
   (geoid vs ellipsoid: especially important for DEM-based hydrology)

5. **What distortion tradeoffs are acceptable?**
   (none? local only? large-scale but not local hydrology?)

6. **Under what conditions would a different CRS be preferable?**
   (future refinements, multi-dataset harmonization, basin-scale work, etc.)

These questions *precede* method/tool selection.

---

## 4. Instantiating the Universal Epistemic Schema for CRS

Below is how CRS reasoning maps into the justification schema:

| Schema Field        | CRS-Specific Interpretation                                  |
| ------------------- | ------------------------------------------------------------ |
| `domain`            | always `crs_datum_justification`                             |
| `intent`            | the spatial or hydrological property requiring protection    |
| `assumptions`       | datum alignment, ellipsoid vs geoid, tolerance of distortion |
| `candidate_methods` | possible CRSs or datum transformation paths                  |
| `selected_method`   | chosen CRS + WHY it is correct for this context              |
| `epistemic_status`  | level of confidence + when to revisit                        |

---

## 5. Structured Justification Workflow

The reasoning flow:

1. **Identify the geospatial property to preserve**
2. **Surface datum & ellipsoid assumptions**
3. **Enumerate candidate CRSs (even briefly)**
4. **Reject inappropriate CRSs explicitly**
5. **Select CRS based on intent → constraint alignment**
6. **Declare residual uncertainty & revision conditions**

The presence of step 6 is what differentiates *scientific reasoning* from *procedure*.

---

## 6. Worked Example (Hydrology-Sensitive CRS Choice)

**Scenario:**
A DEM initially stored in a geographic CRS (EPSG:4326) is being prepared for hydrologic conditioning and streamflow modeling.

```
epistemic_justification:
  domain: crs_datum_justification

  intent:
    description: "Preserve hydrologic realism: drainage direction and slope must map truthfully to surface geometry."
    context: "DEM will be used to derive flow accumulation and network connectivity."

  assumptions:
    known:
      - "Input DEM is in WGS84 geographic CRS (EPSG:4326), degrees not meters."
      - "Hydrologic flow direction computation assumes Euclidean distance in projected space."
    uncertain:
      - "Vertical datum consistency between source DEM and target CRS may not be guaranteed."
    dependencies:
      - "Hydrology is sensitive to local distortion; angular preservation is irrelevant."

  candidate_methods:
    considered:
      - "EPSG:4326 (no reprojection)"
      - "UTM zone 10N (EPSG:32610)"
      - "NAD83 / BC Albers (EPSG:3005)"
    rejected:
      - method: "EPSG:4326"
        reason: "Degrees-based coordinate spacing produces non-physical slope magnitude."
      - method: "EPSG:3005"
        reason: "Equal-area system is optimized for cartography; not hydrology."

  selected_method:
    name: "EPSG:32610 (UTM Zone 10N)"
    rationale: "Minimizes local distortion of surface geometry; supports hydrologic gradient fidelity."
    tradeoffs: "Limited to zone scale; cross-zone basins would require mosaic handling."

  epistemic_status:
    confidence_level: "medium-high"
    residual_uncertainty_sources:
      - "Unverified vertical datum (geoid vs ellipsoid)."
    conditions_for_revisit:
      - "If basin extends beyond UTM zone boundary."
      - "If a hydrology-specific projected CRS is available for local watershed."
```

---

## 7. When CRS Escalation Is *Not* Required

No methodology justification is required when:

* input data is already in the scientifically appropriate CRS,
* reprojection is for *display only*,
* the transformation is lossless (metadata-only change),
* downstream analysis is CRS-agnostic (rare in raster hydrology).

---

## 8. Forward Compatibility

This methodology explicitly allows **future replacement of CRS choice** under better knowledge or improved projections because it encodes:

* uncertainty sources,
* revision triggers,
* and rejected alternatives.

This converts CRS selection from *final answer* into *living scientific reasoning.*

---

## Related References

- **Risk Registry**: `EPISTEMIC_RISK_CLASSES.md`
- **Implementation Blueprint**: `IMPLEMENTATION_PLAN.md`


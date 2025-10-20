# Epistemic Risk Classes

*When a geospatial agent must escalate from procedure → methodology*

## 1. Purpose

This document defines **where** geospatial operations carry *epistemic risk* — meaning situations where the correctness of the result depends on the **methodological justification**, not merely the computational outcome.

These risk classes are the conditions under which the agent must **elevate reasoning from “do” to “justify.”** They activate the epistemic escalation described in `AGENT_EPISTEMOLOGY.md`.

---

## 2. The Four Primary Classes of Epistemic Risk

| Class                             | Core Risk                                            | Why It Matters                                                           |
|-----------------------------------|------------------------------------------------------|--------------------------------------------------------------------------|
| 1. CRS / Datum Risk               | Misinterpretation of space or elevation              | Can distort scale, area, or topology without visible failure             |
| 2. Resolution / Resampling Risk   | Loss or mutation of signal                           | Results remain “numerically valid” but become scientifically meaningless |
| 3. Topology / Hydrology Risk      | Structural discontinuity in surfaces or networks     | Breaks flow direction, drainage, adjacency, routing                      |
| 4. Aggregation / Statistical Risk | Unjustified mathematical combination of spatial data | Converts true spatial signals into misleading summaries                  |

These four classes cover *all* categories where GIS can silently produce wrong science.

---

## 3. Subclasses Within Each Category

### 1. CRS / DATUM RISK

* Horizontal CRS mismatch (projection vs ellipsoid assumption)
* Vertical datum mismatch (geoid vs ellipsoid height)
* Mixed geodetic epochs (tectonic movement)
* Loss of linear vs areal property preservation

### 2. RESOLUTION / RESAMPLING RISK

* Pixel aggregation (nearest vs bilinear vs cubic)
* Over-smoothing or staircasing
* Mixed resolution mosaics
* Derived terrain artifacts from interpolation

### 3. TOPOLOGY / HYDROLOGY RISK

* DEM hydrological conditioning
* Sink/breach decisions
* Snap-to-stream tolerance
* Breaklines vs implicit surfaces

### 4. AGGREGATION / STATISTICAL RISK

* Averaging across nonlinear terrain proxies
* Zonal statistics on mixed-resolution rasters
* Spatial joins that assume stationarity
* Ignoring variance or uncertainty in combined layers

---

## 4. Silent Failure Modes (representative)

| Class       | Silent Failure Example                                                                             |
|-------------|----------------------------------------------------------------------------------------------------|
| CRS         | A DEM “looks fine” but distances shrink by 8% due to wrong projection; watershed boundaries shift. |
| Resolution  | Aggregation smooths slope rasters, reducing hazard classification severity without any error flag. |
| Hydrology   | Flow routing selects a false pour point because microtopography was lost during conditioning.      |
| Aggregation | Zonal mean temperature hides extreme microclimate pockets → false suitability conclusions.         |

None of these *crash*.
They “succeed” — but produce invalid science.

---

## 5. Epistemic Escalation Triggers (internally framed)

Escalate to methodology whenever you (the agent):

### CRS / Datum Risk

* are unsure whether the target CRS preserves the scientific property required (distance, area, hydrology, azimuth integrity)
* cannot confirm vertical datum compatibility
* detect a likely mismatch between input and target assumptions

### Resolution / Resampling Risk

* realize that interpolation or kernel choice could change interpretation of terrain or gradients
* are unsure whether native resolution held ecological or hydrological meaning

### Topology / Hydrology Risk

* suspect the DEM’s drainage structure may not be topologically sound
* are taking actions that implicitly assume “surface connectivity”

### Aggregation / Statistical Risk

* combine values whose meaning depends on spatial variance or sampling theory
* are unsure whether aggregation obscures signal vs noise

---

## 6. Boundary Conditions (non-escalation)

Escalation is *not required* when:

* Data is already in target CRS and verified compatible.
* Resampling is identity-resolution (copy) or for pure display.
* Hydrology/topology is not inferred from the data.
* Aggregation is not interpretive (e.g. metadata concatenation, structural staging ops).

This reinforces that escalation is **contextual**, not universal.

---

## 7. Relationship to Methodology

After a risk class is triggered, the agent should *not immediately call a GDAL tool.*
Instead, it should seek a **methodological scaffold** appropriate to the risk:

| Risk Class  | Methodology Type                        |
|-------------|-----------------------------------------|
| CRS / Datum | Geodetic justification                  |
| Resolution  | Sampling / interpolation justification  |
| Hydrology   | Topological continuity justification    |
| Aggregation | Statistical defensibility justification |

Methodology comes **before** execution.

---

## 8. Forward-Compatibility

These classes are intentionally broad because future models may:

* invent new hydrological correction heuristics,
* propose projection strategies not in today’s textbooks,
* discover new sampling-aware transformations,

…yet these four epistemic gateways will *still* define
**when** justification is required.

This preserves scientific rigor *while remaining compatible with future discovery.*

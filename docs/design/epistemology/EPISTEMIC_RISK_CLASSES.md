# EPISTEMIC_RISK_CLASSES.md

A registry of decision contexts that require an `epistemic_justification` before high-impact geospatial operations proceed. Use this alongside `JUSTIFICATION_SCHEMA.md` and the implementation blueprint in `IMPLEMENTATION_PLAN.md`.

---

## Risk Classes

- **CRS_DATUM**
  - **Trigger**: Reprojection or datum transformations that change spatial meaning.
  - **Why**: Projection choice alters distances, areas, hydrologic realism.
  - **Methodology**: `CRS.md`

- **RESAMPLING**
  - **Trigger**: Raster resampling, resolution changes, or grid realignments.
  - **Why**: Resampling encodes which signal (classification, gradient, smoothness) is preserved.
  - **Methodology**: `RESAMPLING.md`

- **HYDROLOGY**
  - **Trigger**: Conditioning, sink filling/breaching, flow routing, drainage adjustments.
  - **Why**: Alters process truth about how water moves across the surface.
  - **Methodology**: `HYDROLOGY.md`

- **AGGREGATION**
  - **Trigger**: Statistical summarization that collapses distributions into a single value.
  - **Why**: Privileges an interpretation (central tendency, extremes, dominant class).
  - **Methodology**: `AGGREGATION.md`

---

## Escalation Outcomes

- **Proceed**: Justification present and input hash matches.
- **Warn**: Justification present but stale (hash mismatch) – proceed with caution and emit a receipt.
- **Block**: High-risk tool without justification when policy marks it critical (see `IMPLEMENTATION_PLAN.md`).

---

## References

- `JUSTIFICATION_SCHEMA.md` – schema for justification objects.
- `IMPLEMENTATION_PLAN.md` – operational plan for preflight, hashing, storage, and receipts.

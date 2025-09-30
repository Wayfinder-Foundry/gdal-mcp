# ADR-0005-mvp-scope-tools-and-primitives.md

## Title

MVP scope: core tools & primitives for GDAL MCP

## Status

Proposed

## Context

We want a focused MVP aligned with common workflows and easy distribution. The user preference is to emulate core GDAL features: **info**, **reprojection**, **conversion**, and **VRT**—keeping vectors minimal at first.

## Decision

**Raster tools**

* `raster_info(uri, band?) -> RasterInfo`
* `reproject_raster(src_uri, dst_crs, resampling?=nearest, dst_res?, align?) -> Resource+Summary`
* `convert_raster(src_uri, driver='COG'|... , options?: dict) -> Resource+Summary`
* `build_vrt(uris: list[str], options?: dict) -> Resource+Summary`

**Vector tools (minimal)**

* `vector_info(uri) -> VectorInfo`
* `reproject_vector(src_uri, dst_crs) -> Resource+Summary`

**Deferred (post-MVP)**

* `raster_window_stats`, `thumbnail`, `clip_vector`, `clip_raster`.

## Consequences

* Pro: Tight surface, simpler testing, quicker distribution story.
* Con: Some analytics (stats/clips) deferred; may require follow-up release.

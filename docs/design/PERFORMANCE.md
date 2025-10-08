---
type: product_context
title: Performance Plan & SLOs
tags: [performance, benchmarking, slo]
---

# Performance Plan & SLOs

Initial targets; will calibrate after baseline runs.

## SLOs (v0)

- get_info
  - p95 < 500ms (small), < 2s (medium)
- translate (e.g., GeoTIFF → COG)
  - p95 < 10s (medium ~512MB), single-thread default
- warp
  - p95 < 20s (medium reprojection)
- Memory
  - Steady-state RSS < 1.5× input size for translate/warp; no leaks across 100 runs

## Benchmark Harness

- Script: `scripts/bench.py`
- Cases: tiny (KB), small (MB), medium (hundreds MB)
- Metrics: wall/CPU time, RSS peak, IO bytes, GDAL error counts
- Output: `bench/` JSON per case + `bench/REPORT.md`
- Determinism: fixed seeds, temp dirs `TMPDIR/gdal-mcp/<run>/<case>`

## Tuning & Config

- GDAL creation options (COG tiling, block sizes), resampling choice
- Concurrency cap: `GDAL_MCP_MAX_CONCURRENCY`
- Env verification at startup: GDAL, PROJ data paths, temp/cache dirs

## Acceptance Criteria

- Baselines produced and stored in repo
- Regressions tracked; CI can run tiny/small cases on PRs
- Logs contain timings and error counts at INFO level (stderr)

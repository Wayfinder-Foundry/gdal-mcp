# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-10

### Highlights
- **Phase 2A resource suite (ADR-0023)**: Catalog discovery, metadata format inspection, and knowledge/reference APIs built for autonomous geospatial reasoning.
- **Shared planning helpers**: New `src/shared/catalog/`, `src/shared/metadata/`, and `src/shared/reference/` modules centralize discovery, classification, and guidance logic for tools and resources.
- **Agent-ready documentation**: Expanded ADR set (0023–0025) and styleguide docs to guide future contributions.

### Added
- `metadata://{file}/format` resource backed by `src/shared/metadata/format.py` for driver/format inspection using rasterio/pyogrio fallbacks.
- Catalog resources `catalog://workspace/{all|raster|vector}/{subpath}` with filtered listings, hidden-file toggles, and dynamic extension detection.
- Reference resources:
  - `reference://crs/common/{coverage}` with curated global/continental CRS registry.
  - `reference://resampling/{available,guide}/{*}` exposing enriched resampling metadata, normalization helpers, and selection heuristics.
  - `reference://compression/available/{kind}` and `reference://glossary/geospatial/{term}` supporting agent planning and vocabulary lookup.
- Shared reference utilities (`Category`, `OpType`, `ResamplingInfo`, `CompressionInfo`, `GlossaryEntry`) with Python 3.10-compatible `StrEnum` backports.
- New pytest coverage: `test/test_catalog_resources.py`, `test/test_metadata_format.py`, `test/test_reference_shared.py` exercising discovery, metadata, and reference flows.

### Changed
- `pyproject.toml` bumped to **v0.2.0** to signal new resource capabilities while retaining backwards-compatible tool APIs.
- `README.md` refreshed with resource taxonomy overview, geospatial reasoning roadmap, and updated testing guidance.
- Catalog scanner (`src/shared/catalog/scanner.py`) now caches results, auto-augments extension lists via rasterio/pyogrio when present, and exposes `scan()` / `clear_cache()` helpers.

### Removed
- Deprecated `src/models/compression.py` in favour of richer reference compression registry.

### Documentation
- Added ADR-0023 (Resource Taxonomy & Hierarchy), ADR-0024 (Context Usage & Logging Policy), ADR-0025 (Catalog Resource Suite) plus design notes on migration and FastMCP context usage.
- Introduced 16-part styleguide under `docs/styleguide/` governing code quality and consistency.

---

## [0.1.0] - 2025-09-30

🎉 **First Production Release - Historic Milestone**

First successful live tool invocation of GDAL operations through conversational AI (2025-09-30)!

### Added
- **GitHub Actions CI/CD pipeline** with modular workflows (quality gates, test matrix Python 3.10-3.12, build verification, PyPI publishing)
- **Dependency review workflow** for security scanning on pull requests
- **PathValidationMiddleware** for workspace scoping and secure file access control (ADR-0022)
- **Context support** for real-time LLM feedback and tool optimization (ADR-0020)
- Comprehensive ADR documentation (22 architecture decisions)
- ConPort integration for project knowledge management
- FastMCP dev tooling and inspector support
- Modular, reusable GitHub Actions workflows (quality.yml, test.yml, build.yml)

### Changed
- **BREAKING: Tool naming convention** changed from dots to underscores for MCP protocol compatibility
  - `raster.info` → `raster_info`
  - `raster.convert` → `raster_convert`
  - `raster.reproject` → `raster_reproject`
  - `raster.stats` → `raster_stats`
  - `vector.info` → `vector_info`
- **CLI renamed**: `gdal-mcp` → `gdal` (repository name stays `gdal-mcp`)
- **Complete Python-native rewrite** using Rasterio, PyProj, Shapely, Pyogrio (no GDAL CLI dependency)
- Switched to `src/` layout package structure for better organization
- Migrated to FastMCP 2.x with native configuration (fastmcp.json)
- Updated all tool descriptions for LLM optimization (ADR-0021)

### Fixed
- **Historic milestone**: First successful live tool invocation in Cascade AI (2025-09-30)
- MCP protocol compliance: Tool names now use underscores instead of dots
- Removed sensitive configuration files from git history using git filter-branch
- Fixed tool registration and capability advertisement
- Workspace scoping now correctly validates file paths against allowed directories
- CI workflow configuration: Use system-installed dependencies (not `uv run` isolated environments)
- Code formatting: 24 files reformatted with ruff
- Lint errors: Fixed 10 ruff errors (unused imports, import order, unused variables, f-strings)

### Security
- Removed `.mcp-config.json` with sensitive tokens from entire git history
- Added `.gitignore` entries for IDE configs and generated artifacts
- Implemented workspace scoping middleware for secure file access

### Documentation
- Added comprehensive GitHub Actions workflow documentation with GitLab CI comparison
- Updated all tool docstrings with USE WHEN, REQUIRES, OUTPUT, SIDE EFFECTS sections
- Created `docs/LIVE_TEST_SETUP.md` with testing procedures
- Removed IDE/tool-specific directories from repository (78 files)
- **README.md**: Vision statement, GitHub Actions badges, historic milestone celebration
- **QUICKSTART.md**: Installation methods, workspace configuration, tool examples
- **CONTRIBUTING.md**: ADR review requirement + Dask example for heavy processing

## [0.0.2] - 2025-09-30

### Added
- **GitHub Actions CI/CD pipeline** with quality gates, test matrix (Python 3.10-3.12), and PyPI publishing
- **Dependency review workflow** for security scanning on pull requests
- **PathValidationMiddleware** for workspace scoping and secure file access control (ADR-0022)
- **Context support** for real-time LLM feedback and tool optimization (ADR-0020)
- Comprehensive ADR documentation (22 architecture decisions)
- ConPort integration for project knowledge management
- FastMCP dev tooling and inspector support

### Changed
- **BREAKING: Tool naming convention** changed from dots to underscores for MCP protocol compatibility
  - `raster.info` → `raster_info`
  - `raster.convert` → `raster_convert`
  - `raster.reproject` → `raster_reproject`
  - `raster.stats` → `raster_stats`
  - `vector.info` → `vector_info`
- **Complete Python-native rewrite** using Rasterio, PyProj, Shapely, Pyogrio (no GDAL CLI dependency)
- Switched to `src/` layout package structure for better organization
- Migrated to FastMCP 2.x with native configuration (fastmcp.json)
- Updated all tool descriptions for LLM optimization (ADR-0021)
- Switched from `uvx` to `uv run --with` for development to avoid caching issues

### Fixed
- **Historic milestone**: First successful live tool invocation in Cascade AI (2025-09-30)
- MCP protocol compliance: Tool names now use underscores instead of dots
- Removed sensitive configuration files from git history using git filter-branch
- Fixed tool registration and capability advertisement
- Workspace scoping now correctly validates file paths against allowed directories

### Security
- Removed `.mcp-config.json` with sensitive tokens from entire git history
- Added `.gitignore` entries for IDE configs and generated artifacts
- Implemented workspace scoping middleware for secure file access

### Documentation
- Added comprehensive GitHub Actions workflow documentation with GitLab CI comparison
- Updated all tool docstrings with USE WHEN, REQUIRES, OUTPUT, SIDE EFFECTS sections
- Created `docs/LIVE_TEST_SETUP.md` with testing procedures
- Removed IDE/tool-specific directories from repository (78 files)

## [0.0.1] - 2025-09-05

### Added
- Initial public release of GDAL MCP with support for GDAL command-line tools (`gdalinfo`, `gdal_translate`, `gdalwarp`, `gdalbuildvrt`, `gdal_rasterize`, `gdal2xyz`, `gdal_merge`, `gdal_polygonize`) exposed as MCP tools.
- Added comprehensive design document `gdal_mcp_design.md`, README, CONTRIBUTING, Code of Conduct, and other project documentation.

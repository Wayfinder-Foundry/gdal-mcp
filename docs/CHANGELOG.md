# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [2.0.0] - 2025-09-30

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

## [1.0.0] - 2025-09-05

### Added
- Initial public release of GDAL MCP with support for GDAL command-line tools (`gdalinfo`, `gdal_translate`, `gdalwarp`, `gdalbuildvrt`, `gdal_rasterize`, `gdal2xyz`, `gdal_merge`, `gdal_polygonize`) exposed as MCP tools.
- Added comprehensive design document `gdal_mcp_design.md`, README, CONTRIBUTING, Code of Conduct, and other project documentation.

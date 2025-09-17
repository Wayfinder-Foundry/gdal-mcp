# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Refactored `Resampling` and `Format` enums into dedicated modules (`server/enums/resampling.py` and `server/enums/format.py`) to improve code organization
- Fixed enum `all()` methods to return string values instead of enum members for clearer validation logic
- Updated enum method signatures and behavior to be consistent with string-based validation

### Added
- Planned enhancements and future improvements.

## [1.0.0] - 2025-09-05

### Added
- Initial public release of GDAL MCP with support for GDAL command-line tools (`gdalinfo`, `gdal_translate`, `gdalwarp`, `gdalbuildvrt`, `gdal_rasterize`, `gdal2xyz`, `gdal_merge`, `gdal_polygonize`) exposed as MCP tools.
- Added comprehensive design document `gdal_mcp_design.md`, README, CONTRIBUTING, Code of Conduct, and other project documentation.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-24

### 🎉 Major Release - Geospatial Reasoning Substrate

This release transforms gdal-mcp from a tool wrapper into a **geospatial reasoning substrate** that enables models to compose GDAL operations with domain understanding, justified decisions, and persistent context.

### Added

#### Reflection Preflight System
- **Pre-execution reasoning prompts** for consequential geospatial operations
- **Justification schema** with intent, alternatives, choice, and confidence levels
- **Disk-based reflection store** with domain-aware caching and atomic writes
- **Decorator-based middleware** for seamless tool integration (`@requires_reflection`)
- **Risk classification framework** for operation consequence assessment

#### Domain-Aware Prompts
- **CRS selection reasoning** - Distance/area/shape preservation analysis
- **Resampling method justification** - Signal property preservation logic
- **Hydrology conditioning rationale** - Flow path preservation reasoning
- **Aggregation statistic reasoning** - Interpretation goal analysis
- **Prompt registration system** - LLM-driven reasoning infrastructure

#### Architecture & Infrastructure
- **Middleware layer** for cross-cutting concerns (preflight, reflection store)
- **Resource-based reference data** for static/semi-static geospatial knowledge
- **Agent guidelines** (AGENTS.md) with tool affordance index and work mode classification
- **Comprehensive test suite** - 72 passing tests with full coverage
- **Type safety** - Full mypy strict mode compliance across reflection system

### Changed
- **Reorganized middleware** - Moved from single file to dedicated module
- **Enhanced error handling** - Proper exception chaining with `from exc`
- **Updated agent guidelines** - Trust-based approach enabling emergent workflows
- **Improved documentation** - Updated README with v1.0.0 features and vision

### Technical Details
- Python 3.11+ required
- FastMCP 2.0 integration
- Pydantic 2.0+ for type-safe models
- Ruff linting and mypy strict mode compliance
- Atomic file operations for crash safety

### Philosophy
This release establishes the foundation for **geospatial reasoning**: models can now compose GDAL operations with domain understanding, justified decisions, and persistent context - enabling discovery of novel analysis workflows beyond prescribed procedures.

---

## [0.2.1] - 2025-10-10

### Fixed
- Resource discovery improvements
- Metadata format detection enhancements

---

## [0.2.0] - 2025-10-10

### Added
- **Workspace Catalog Resources** - `catalog://workspace/{all|raster|vector}/{subpath}`
- **Metadata Intelligence** - `metadata://{file}/format` for driver/format details
- **Reference Library** - CRS, resampling, compression, and glossary resources
- Shared reference utilities for agent planning
- ADR-0023, ADR-0024, ADR-0025 documentation

### Changed
- Enhanced resource discovery capabilities
- Improved agent planning with reference knowledge

---

## [0.1.0] - 2025-09-30

### 🎉 Initial Release - MVP Complete

### Added
- **Core Raster Tools**
  - `raster_info` - Inspect raster metadata
  - `raster_convert` - Format conversion with compression and tiling
  - `raster_reproject` - CRS transformation with explicit resampling
  - `raster_stats` - Comprehensive band statistics

- **Vector Tools**
  - `vector_info` - Inspect vector dataset metadata

- **Infrastructure**
  - FastMCP 2.0 integration
  - Python-native stack (Rasterio, PyProj, pyogrio, Shapely)
  - Type-safe Pydantic models
  - Workspace security with PathValidationMiddleware
  - Context API for real-time LLM feedback
  - Comprehensive test suite (23 tests)
  - CI/CD pipeline with GitHub Actions
  - Docker deployment support

- **Documentation**
  - QUICKSTART.md
  - CONTRIBUTING.md
  - 22 Architecture Decision Records (ADRs)
  - Design documentation

### Philosophy
First successful live tool invocation - GDAL operations are now conversational!

---

[1.0.0]: https://github.com/Wayfinder-Foundry/gdal-mcp/compare/v0.2.1...v1.0.0
[0.2.1]: https://github.com/Wayfinder-Foundry/gdal-mcp/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Wayfinder-Foundry/gdal-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Wayfinder-Foundry/gdal-mcp/releases/tag/v0.1.0

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-24

### 🎉 Major Release - First MCP Server with Epistemic Governance

**The first geospatial AI substrate with epistemic reasoning.** This release introduces a reflection middleware 
system that requires AI agents to justify methodological decisions before executing geospatial operations with 
significant consequences.

### Added

#### 🧠 Reflection Middleware System
- **FastMCP middleware interception** - Pre-execution reasoning for all flagged tools
- **ReflectionMiddleware** - Intercepts tool calls, checks cache, triggers prompts when needed
- **Declarative reflection config** - Maps tools to required justifications (ReflectionSpec)
- **Persistent justification cache** - `.preflight/justifications/{domain}/sha256:{hash}.json`
- **SHA256-based cache keys** - Content-addressed storage for integrity and deduplication
- **Automatic cache hits** - Same parameters = instant execution (no re-prompting)
- **Partial cache support** - Independent caching per reflection domain

#### 📝 Reflection Domains
- **`crs_datum`** - Coordinate system selection and datum transformations
  - Prompt: `justify_crs_selection` - Why this projection? What properties to preserve?
  - Cache key: `dst_crs` only (source-agnostic reasoning)
- **`resampling`** - Interpolation method choice for raster operations
  - Prompt: `justify_resampling_method` - How to interpolate? What artifacts acceptable?
  - Cache key: `method` only
- **Tool integration:** `raster_reproject` requires both CRS and resampling justifications

#### 🔧 Structured Justification Schema
- **Intent** - What property/goal must be preserved
- **Alternatives** - Other methods considered and why rejected
- **Choice** - Selected method with rationale and tradeoffs
- **Confidence** - Low/medium/high certainty in methodology

#### 🛠️ New Tools & Infrastructure
- **`store_justification`** - Explicit tool for AI to cache methodological reasoning
- **Justification models** - Pydantic schemas with full validation (`Justification`, `Choice`, `Alternative`)
- **Cache inspection** - On-disk JSON files for auditing and provenance
- **Legacy API fallback** - Safe handling of both FastMCP 2.0 and legacy APIs

### Changed

#### API & Type System
- **Flattened parameters** - `raster_reproject(uri, output, dst_crs, resampling, ...)` (was nested `Params` object)
- **tuple → list** - JSON-RPC compatibility for `bounds` and `resolution` parameters
- **Simplified prompts** - `justify_crs_selection(dst_crs)` and `justify_resampling_method(method)` (removed unused params)
- **Case-insensitive compression** - `deflate`/`DEFLATE` both accepted in `raster_convert`

#### Middleware Architecture
- **Middleware migration** - Uses `context.message.name/arguments` (not deprecated `context.request`)
- **Graceful degradation** - Skips preflight if tool name undetermined (prevents hard failures)
- **Improved error messages** - Clear instructions: "Call prompt X with args Y, then retry"

#### Documentation
- **README overhaul** - Attention-grabbing examples, before/after comparison, real-world scenarios
- **NEW: docs/REFLECTION.md** - 500+ line technical deep dive (architecture, cache, integration guide)
- **NEW: docs/ROADMAP.md** - Strategic vision from v1.0 → v2.0
- **NEW: test/TESTING_RESULTS_v1.0.0.md** - Formal validation report (7/7 tests passing)
- **Enhanced: test/REFLECTION_TESTING.md** - Added cache behavior and source CRS placeholder docs

### Fixed
- **Line length compliance** - Pre-commit hook formatting (100 char limit)
- **Type safety** - Full mypy strict mode across reflection system
- **Import ordering** - Ruff auto-formatting applied

### Testing

#### Comprehensive Validation (7/7 tests passing)
1. ✅ **First use** - Both CRS and resampling prompts triggered
2. ✅ **Cache hit** - Identical parameters, no prompts (instant execution)
3. ✅ **Partial cache (new CRS)** - Only CRS prompt, resampling cached
4. ✅ **Partial cache (new resampling)** - Only resampling prompt, CRS cached
5. ✅ **Full cache miss** - Both parameters different, both prompts
6. ✅ **Relative paths** - Path resolution works, cache behavior correct
7. ✅ **Lowercase compression** - Case-insensitive validation works

#### Test Artifacts
- **7 output files** created in `test/data/` (test1-7*.tif)
- **6 justification files** cached in `.preflight/justifications/` (3 CRS, 3 resampling)
- **Cache hit rate** - 57% in isolated tests, >80% in realistic workflows

#### UX Validation
- **Helpful** ✅ - Guides next step only when required
- **Intentional** ✅ - Enforces epistemic guardrails at correct points
- **Educational** ✅ - Captures rationale and tradeoffs
- **Verifiable** ✅ - Auditable on-disk justifications with stable keys
- **Non-conflicting** ✅ - Minimal interruption, clear instructions, fast on cache hits

### Performance
- **First invocation** (cache miss): ~10-30 seconds (includes LLM reasoning)
- **Subsequent invocations** (cache hit): ~6ms (negligible overhead)
- **Cache size**: ~1-2KB per justification JSON file

### Technical Details
- Python 3.11+ required
- FastMCP 2.0 native middleware support
- Pydantic 2.0+ for type-safe models
- 72 comprehensive tests passing
- Full mypy strict mode compliance
- Ruff linting with pre-commit hooks

### Documentation
- **README.md** - User-facing overview with compelling examples
- **docs/ROADMAP.md** - Strategic planning (v1.0 → v2.0)
- **docs/REFLECTION.md** - Technical deep dive for developers
- **test/TESTING_RESULTS_v1.0.0.md** - Formal validation report
- **test/REFLECTION_TESTING.md** - Manual testing guide with 7 scenarios

### Philosophy
This release establishes GDAL MCP as the **first MCP server with epistemic governance**. AI agents must demonstrate 
methodological understanding through structured reasoning before executing operations that have geospatial consequences. 
The reflection system enforces domain expertise while maintaining workflow efficiency through intelligent caching.

**Vision:** Enable discovery of novel geospatial analysis workflows through tool composition with domain understanding, 
not just prescribed procedures.

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

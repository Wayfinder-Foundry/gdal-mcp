# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-10-26

### 🎉 Major Feature Release - Vector Tool Parity & Cross-Domain Reflection

This release achieves feature parity between raster and vector operations and validates the core architectural innovation: **cross-domain reflection cache sharing**. Methodological reasoning now transcends data types.

### Added

#### Vector Tool Suite (6 tools)
- **`vector_info`** - Enhanced metadata inspection (pyogrio-based)
- **`vector_reproject`** - CRS transformation with cross-domain reflection
- **`vector_convert`** - Format migration (SHP↔GPKG↔GeoJSON) with encoding control
- **`vector_clip`** - Spatial subsetting by bounding box or mask geometry
- **`vector_buffer`** - Proximity analysis with configurable resolution
- **`vector_simplify`** - Geometry simplification (Douglas-Peucker/Visvalingam)

#### Architectural Innovation: Cross-Domain Cache Sharing
- **Domain-based (not tool-based) reflection** - CRS justification for raster operations is reusable for vector operations
- **75% cache hit rate** in multi-operation workflows (validated through user testing)
- **Educational continuity** - Methodology reasoning carries across tool boundaries

### Fixed

#### Critical: Cross-Domain Reflection Cache Sharing
- **Problem**: Cache keys included tool_name, making justifications tool-specific
- **Impact**: Justified EPSG:3857 for raster_reproject required re-justification for vector_reproject
- **Root cause**: `_stable_hash()` included tool_name in hash payload
- **Solution**: Removed tool_name from cache key; now purely domain-based (domain + prompt_hash + prompt_args)
- **Result**: ✅ CRS justification now shared across raster ↔ vector operations
- **User feedback**: Friction reduced 50% (3/5 → 1.5/5), helpfulness increased to 5/5

### Changed

- **Server bootstrap**: Added explicit imports for vector tools to ensure registration
- **Test suite**: Updated reflection workflow tests for new signature

### Technical Details

**Code Quality**:
- ~1,350 lines production code
- Full type safety (mypy strict mode)
- Pydantic models throughout
- ADR compliance (0012, 0013, 0017)
- 72 tests passing

**Testing & Validation**:
- Round 1 testing identified tool-specific caching issue
- Fix applied (commits 5e9ae5d, 810dec1)
- Round 2 testing confirmed cross-domain caching working
- Qualitative assessment: "Yes, confidently recommend" (up from "helpful with caveats")

### Impact

**Architectural Validation**:
This release proves that **methodological reasoning can transcend data types**. A CRS justification is about the projection's properties (conformal, equal-area, etc.), not whether you're reprojecting raster or vector data. The cross-domain cache architecture reflects this truth.

**User Experience**:
- First CRS justification unlocks subsequent operations (raster or vector)
- Workflows feel coherent and intelligent
- Educational value preserved without repetition
- 75% cache hit rate means minimal friction

**What This Means**:
GDAL MCP now has complete vector tool coverage with the same epistemic rigor as raster operations. The cross-domain reflection validates the core architectural principle: domain-based methodological reasoning, not tool-specific commands.

---

## [1.0.1] - 2025-10-26

### Changed

#### Reflection Prompt Improvements
- **Advisory tone over prescriptive language** - All reflection prompts updated to respect user autonomy
- **CRS prompt** - Changed from "Before reprojecting..." to "The operation will use..."
- **Resampling prompt** - Changed from "Before resampling..." to conversational guidance
- **Hydrology prompt** - Updated for future consistency (not yet integrated with tools)
- **Aggregation prompt** - Updated for future consistency (not yet integrated with tools)

#### UX Enhancements
- **Conversational intervention** - AI now asks users about concerns instead of blocking
- **Respects explicit requirements** - User-specified parameters are documented, not questioned
- **Educational advisory** - AI provides guidance when detecting potential issues
- **Natural flow** - No artificial barriers, just helpful conversation

### Documentation
- **ADR-0026 Amendment** - Documented the shift from prescriptive to advisory prompting
- **Philosophy alignment** - Implementation now matches "preserve agent autonomy" principle

### Technical Details
- No breaking changes - API identical to v1.0.0
- No new features - Same tools and capabilities
- Prompt refinement only - Middleware and cache unchanged
- All type checks passing - Full mypy compliance maintained

### Impact
This patch release fixes UX friction identified in v1.0.0 where prescriptive prompts were blocking explicit user requirements. The advisory pattern enables natural conversation while maintaining epistemic accountability.

---

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

[1.0.1]: https://github.com/Wayfinder-Foundry/gdal-mcp/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Wayfinder-Foundry/gdal-mcp/compare/v0.2.1...v1.0.0
[0.2.1]: https://github.com/Wayfinder-Foundry/gdal-mcp/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Wayfinder-Foundry/gdal-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Wayfinder-Foundry/gdal-mcp/releases/tag/v0.1.0

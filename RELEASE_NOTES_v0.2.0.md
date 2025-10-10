# GDAL MCP v0.2.0 Release Notes

**Release Date**: October 10, 2025  
**Codename**: "Knowledge Infrastructure"

---

## Overview

Version 0.2.0 introduces a comprehensive knowledge infrastructure that enables AI agents to reason about geospatial problems with domain expertise. Building on the solid foundation of v0.1.0's tool execution capabilities, this release adds the contextual awareness and reference data that transform gdal-mcp from a GDAL interface wrapper into a **geospatially-enabled AI assistant**.

This release directly advances the vision outlined in [VISION.md](docs/design/VISION.md): creating AI systems that understand spatial problems, compose analytical workflows, and bridge the gap between domain expertise and technical implementation.

## What's New

Version 0.2.0 adds three categories of resources that provide AI agents with the knowledge to make informed geospatial decisions:

### 1. **Catalog Resources** - Workspace Awareness
Agents can now discover and inventory datasets in your workspace without explicit file paths. The catalog system automatically scans configured workspace directories, classifies files by type (raster/vector/other), and provides structured metadata for each dataset.

### 2. **Reference Resources** - Domain Knowledge
Built-in reference data for common geospatial decisions: CRS selection by region, resampling method guidance for different data types, compression options with use-case recommendations, and a geospatial terminology glossary.

### 3. **Metadata Resources** - Dataset Intelligence
Agents can inspect dataset characteristics before processing: format detection, driver information, spatial properties, and statistical summaries. This enables context-aware processing decisions.

## How This Improves the Experience

### Reduced Interaction Overhead
With catalog resources, agents can discover available datasets independently, reducing the need for users to provide explicit file paths or enumerate available data. This streamlines workflows and enables more natural conversational interactions.

### Context-Aware Processing
Reference resources provide agents with domain knowledge about CRS selection, resampling methods, and compression options. Agents can now make informed technical decisions based on data characteristics and intended use cases, rather than relying on generic defaults.

### Enhanced Reasoning Capabilities
The combination of catalog discovery, metadata inspection, and reference data enables agents to reason about geospatial problems more effectively. For example, an agent can discover a DEM, recognize it as elevation data, select appropriate resampling for terrain analysis, and choose a suitable CRS for the region—all without explicit user guidance.

### Educational Support
The geospatial glossary and reference documentation help bridge knowledge gaps. Agents can explain terminology, recommend best practices, and provide context for technical decisions, making geospatial analysis more accessible to domain experts without deep GIS backgrounds.

## Practical Examples

### Example 1: Workspace-Aware Processing
```
User: "Reproject all DEMs in my workspace to UTM"
Agent: [Scans catalog for raster datasets]
       [Identifies elevation.tif and terrain.tif as DEMs]
       [Determines appropriate UTM zones from spatial bounds]
       [Selects cubic resampling for continuous elevation data]
       "Found 2 DEMs. Reprojecting elevation.tif to EPSG:32610 and terrain.tif to EPSG:32611..."
```

The agent discovers datasets, infers data types, and makes appropriate technical choices without requiring explicit instructions for each step.

### Example 2: Informed Technical Decisions
```
User: "Prepare this land cover raster for web display"
Agent: [Inspects metadata: categorical raster, 30m resolution]
       [Consults resampling reference: MODE for categorical data]
       [Consults CRS reference: EPSG:3857 for web display]
       [Consults compression reference: PNG for categorical preservation]
       "Converting to Web Mercator with MODE resampling and PNG compression to preserve land cover classes."
```

The agent combines metadata inspection with reference knowledge to make technically sound decisions aligned with data characteristics and use case requirements.

### Example 3: Educational Context
```
User: "Should I use bilinear or cubic resampling?"
Agent: [Consults resampling reference]
       "It depends on your data type and operation:
        - Bilinear: Fast, good for continuous data during upsampling
        - Cubic: Higher quality, better for continuous data but slower
        - For categorical data (land cover, classifications), use MODE or NEAREST instead
        What type of data are you working with?"
```

The agent provides contextual guidance based on reference data, helping users make informed decisions.

---

## 🏗️ Technical Improvements

### Resource Taxonomy

We've introduced a structured URI scheme for organizing knowledge:

- **`catalog://`** - Workspace dataset discovery
  - `catalog://workspace/all` - All datasets
  - `catalog://workspace/raster` - Raster datasets only
  - `catalog://workspace/vector` - Vector datasets only

- **`metadata://`** - Dataset inspection
  - `metadata://{file}/format` - Driver and format details
  - `metadata://{file}/raster` - Raster-specific metadata
  - `metadata://{file}/vector` - Vector-specific metadata

- **`reference://`** - Domain knowledge
  - `reference://crs/common/{region}` - CRS recommendations by region
  - `reference://resampling/available` - Resampling method catalog
  - `reference://compression/available` - Compression options
  - `reference://glossary/geospatial` - Terminology reference

### Enhanced Security

- **Path Validation Middleware**: All file operations are validated against configured workspace directories
- **Workspace Scoping**: Prevents access to files outside allowed directories
- **Detailed Error Messages**: Clear guidance when paths are rejected

### Code Quality

- **150+ Lint Fixes**: Improved code consistency and maintainability
- **Module Docstrings**: Every module now has clear documentation
- **Type Annotations**: Better IDE support and type safety
- **Test Coverage**: New tests for catalog, metadata, and reference systems

---

## 📦 What's Included

### New Resources (12 total)

**Catalog Resources (3)**
- Workspace dataset discovery with filtering
- Hidden file handling
- Extension-based classification

**Metadata Resources (4)**
- Format detection (raster/vector/unknown)
- Raster metadata extraction
- Vector metadata extraction
- Statistics computation

**Reference Resources (5)**
- Common CRS by region (50+ entries)
- Resampling methods with guidance (15 methods)
- Compression options (7 methods)
- Geospatial glossary (20+ terms)
- Resampling selection heuristics

### New Shared Modules

- `src/shared/catalog/` - Dataset scanning and caching
- `src/shared/metadata/` - Format detection logic
- `src/shared/reference/` - CRS, resampling, compression, glossary data
- `src/shared/raster/` - Raster info and statistics
- `src/shared/vector/` - Vector info extraction

### Documentation

- **3 New ADRs**: Resource taxonomy, context usage, catalog design
- **16 Style Guides**: Python best practices and conventions
- **FastMCP Context Guide**: Logging and progress reporting patterns
- **Project Brief**: Vision and architecture overview

---

## 🔄 Migration Guide

### Breaking Changes

**None.** Version 0.2.0 is fully backward compatible with v0.1.0 tool APIs.

### New Capabilities

All existing tools (`raster_info`, `raster_convert`, `raster_reproject`, `raster_stats`, `vector_info`) continue to work exactly as before. The new resources are **additive** - they enhance agent capabilities without changing existing behavior.

### Configuration

**Dynamic Versioning**: We've switched to `hatch-vcs` for automatic version management from git tags. No configuration changes required.

**Workspace Scoping**: Ensure `GDAL_MCP_WORKSPACES` environment variable is set to allow access to your data directories:

```bash
export GDAL_MCP_WORKSPACES="/path/to/workspace1:/path/to/workspace2"
```

---

## 🎓 Learning Resources

### For Users

- **QUICKSTART.md**: Updated with resource examples
- **README.md**: New resource taxonomy section
- **VISION.md**: Understand the long-term direction

### For Developers

- **ADR-0023**: Resource taxonomy and hierarchy
- **ADR-0024**: Context usage and logging policy
- **ADR-0025**: Catalog resource implementation
- **docs/styleguide/**: 16 guides on code quality

---

## Alignment with Vision

This release directly advances the goals outlined in [VISION.md](docs/design/VISION.md):

### From Command Executor to Reasoning Agent
Version 0.1.0 established reliable tool execution. Version 0.2.0 adds the knowledge infrastructure that enables **agentic reasoning**—agents can now understand context, consult domain knowledge, and make informed decisions rather than simply executing commands.

### Building Toward Autonomous Workflows
The catalog, metadata, and reference systems provide the foundation for multi-step workflow composition. Agents can now:
- Discover what data exists
- Understand data characteristics
- Select appropriate processing methods
- Explain technical decisions

These capabilities are prerequisites for the autonomous workflow planning targeted in Phase 3.

### Bridging Domain Expertise and Technical Implementation
The reference resources and glossary help bridge the gap between geospatial domain knowledge and technical GIS implementation. Domain experts can work with agents that understand both the spatial problem and the technical solution space.

## What's Next

Version 0.2.0 completes **Phase 2A** (Resources) and sets the stage for **Phase 2B** (Prompts) and **Phase 3** (Multi-step Workflows):

### Upcoming in v0.3.0
- **Prompt Resources**: Guided reasoning templates for common geospatial analysis patterns
- **Workflow Composition**: Multi-step analysis planning and execution
- **State Management**: Session context and intermediate result handling
- **Enhanced Catalog**: Spatial indexing and metadata caching for performance

### Long-term Direction
The vision is to enable domain experts to express geospatial problems in natural language and receive complete, correct analytical workflows. Version 0.2.0 provides the knowledge infrastructure that makes this possible—agents now have access to the domain knowledge, workspace awareness, and reference data needed to reason about spatial problems effectively.

---

## 🙏 Acknowledgments

This release represents a fundamental rethinking of how AI agents should interact with geospatial tools. Special thanks to the FastMCP team for building the protocol that makes this possible.

---

## 📊 Stats

- **92 files changed**
- **4,355 lines added**
- **787 lines removed**
- **12 new resources**
- **16 style guides**
- **3 new ADRs**
- **150+ lint fixes**

---

## 🔗 Links

- **GitHub Release**: https://github.com/Wayfinder-Foundry/gdal-mcp/releases/tag/v0.2.0
- **Pull Request**: https://github.com/Wayfinder-Foundry/gdal-mcp/pull/new/feat-mvp-resources
- **Documentation**: https://github.com/Wayfinder-Foundry/gdal-mcp/tree/v0.2.0/docs
- **Changelog**: https://github.com/Wayfinder-Foundry/gdal-mcp/blob/v0.2.0/docs/CHANGELOG.md

---

**Ready to upgrade?**

```bash
# Pull the latest release
git fetch origin
git checkout v0.2.0

# Install dependencies
uv sync

# Verify installation
uv run gdal --version
```

**Questions or feedback?** Open an issue on GitHub or start a discussion!

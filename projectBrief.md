# GDAL MCP Project Brief

**Project**: GDAL MCP - Democratizing Geospatial Analysis Through Conversational AI  
**Status**: Phase 1 Complete (v0.1.0) | Phase 2 In Progress  
**Last Updated**: 2025-10-09

---

## Executive Summary

**GDAL MCP bridges the gap between geospatial domain expertise and technical implementation by enabling AI agents to understand spatial problems, compose analytical workflows, and execute GDAL operations through natural language.**

This is not a GDAL command wrapper. It is a foundation for **agentic geospatial reasoning** that democratizes powerful analysis tools for domain experts who understand the science but struggle with the syntax.

---

## The Problem

Geospatial analysis requires two forms of expertise that rarely coexist:

1. **Domain Knowledge** - Understanding terrain, hydrology, ecology, geology, urban planning
2. **Technical Implementation** - GDAL syntax, projection systems, algorithm parameters, data formats

**Current Reality:**
- A 30-year veteran hydrologist who deeply understands watersheds cannot perform basic slope analysis because they don't know GDAL syntax
- GIS analysts spend hours on Stack Overflow translating "what I want to do" into "the exact command to do it"
- Domain experts are blocked by technical complexity, not lack of understanding
- Geospatial expertise is being wasted

---

## The Vision

**In 5 years, a domain expert should be able to say:**

> "Show me all areas where slope exceeds 30 degrees within 500 meters of perennial streams, excluding urban zones, and calculate the erosion risk for each parcel."

**And receive:**
- A complete analysis workflow executed correctly
- Results with spatial context
- Explanation of methodology
- Ability to refine and iterate in natural language

**No GDAL commands. No Python scripts. No Stack Overflow.**

Just domain expertise expressed in domain language, translated to precise geospatial operations by an AI agent that understands both.

---

## Core Principles

### 1. Agentic Reasoning Over Command Translation

**Not**: "Reproject to Web Mercator" → Execute gdalwarp with EPSG:3857

**Instead**: "Display this elevation model in a web map"
- AI reasons about requirements (web display needs Web Mercator)
- Chooses appropriate resampling (cubic for elevation)
- Suggests COG format for web performance
- Explains why these choices were made

### 2. Multi-Step Workflow Composition

AI plans entire workflows, understands data flow between steps, optimizes processing order, handles intermediate results, and adapts based on data characteristics.

### 3. Domain Language, Not Technical Syntax

Domain experts speak in:
- Watersheds (not polygons)
- Slope (not derivatives)
- Riparian zones (not buffers)
- Erosion potential (not algorithms)

The AI must understand domain terminology, translate to technical operations, preserve semantic intent, and explain in domain terms.

### 4. Accessibility Without Compromise

**Target users:**
- Hydrologists who understand watersheds but not programming
- Ecologists who understand habitat but not GIS
- Geologists who understand terrain but not GDAL
- Urban planners who understand zoning but not spatial analysis
- Field researchers who collect data but can't process it

These users have deep domain expertise (decades), limited technical background, real analytical needs, and no time to learn GDAL. **They should not be limited by technical barriers.**

---

## Technical Architecture

### Three-Pillar Design (MCP Protocol)

```python
@mcp.resource()  # Information to READ (metadata, catalogs, references)
@mcp.tool()      # Actions to EXECUTE (reproject, convert, analyze)
@mcp.prompt()    # Guidance for THINKING (methodology, workflows)
```

**Resources** provide context (workspace datasets, CRS info, processing history)  
**Tools** execute operations (file creation, reprojection, analysis)  
**Prompts** guide reasoning (terrain analysis methodology, parameter selection)

### Python-Native Stack

- **Rasterio** - Raster I/O and manipulation
- **PyProj** - CRS operations and transformations
- **pyogrio/Shapely** - Vector operations
- **FastMCP 2.0** - MCP server framework
- **Pydantic** - Type-safe models with JSON schema

### ReAct-Style Agentic Prompting

AI interleaves reasoning with actions in iterative loops:
```
Thought: I need to do X because...
Action: ToolName[parameters]
Observation: (tool result)
Thought: Given that result, now I should...
Action: NextTool[parameters]
```

This enables multi-step workflows grounded in real tool outputs.

---

## Current Status (v0.1.0)

### ✅ Phase 1 Complete: Foundation

**Achievements:**
- 🎉 Historic milestone: First successful live tool invocation (2025-09-30)
- 5 core tools: `raster_info`, `raster_convert`, `raster_reproject`, `raster_stats`, `vector_info`
- Production-ready infrastructure (CI/CD, tests, Docker)
- MCP protocol compliance via FastMCP 2.0
- Workspace security (PathValidationMiddleware)
- 23/23 tests passing across Python 3.10-3.12

**What Works:**
- Users can ask "Show me the metadata for this raster" and get structured results
- Reprojection with explicit resampling methods
- Format conversion with compression and overviews
- Comprehensive statistics with histograms

---

## Phased Implementation

### Phase 2: Enhanced Capabilities (v0.x - v1.0) - **IN PROGRESS**

**Goal**: Expand tool coverage and sophistication

**Planned:**
- Vector operations (clip, buffer, intersect, union)
- Raster analysis (slope, aspect, hillshade, viewshed)
- Comprehensive format conversions
- Multi-band operations
- Metadata management

**Focus**: Building the toolkit AI agents can compose

### Phase 3: Workflow Intelligence (v1.x - v2.0)

**Goal**: Enable multi-step reasoning and composition

**Planned:**
- Workflow planning capabilities
- Inter-tool data flow
- Intermediate result management
- Progress tracking for long operations
- Context-aware tool selection

**Focus**: Moving from tools to workflows

### Phase 4: Domain Understanding (v2.x+)

**Goal**: Agentic geospatial reasoning

**Planned:**
- Domain concept recognition (watersheds, viewsheds, riparian zones)
- Methodology libraries (standard analytical workflows)
- Adaptive algorithms (choose methods based on data)
- Explanation generation (why these steps?)
- Quality assessment (validate results)

**Focus**: AI that understands geospatial science

### Phase 5: Collaborative Intelligence (v3.x+)

**Goal**: Human-AI partnership for complex analysis

**Planned:**
- Interactive refinement
- "What if" scenario modeling
- Automated quality checks
- Knowledge capture (learn from domain experts)
- Workflow templates from successful analyses

**Focus**: Amplifying human expertise with AI reasoning

---

## Success Metrics

**We know we're succeeding when:**

1. **Domain experts can work independently**
   - Hydrologist analyzes watersheds without GIS staff
   - Ecologist maps habitat without developers
   - Geologist models terrain without Stack Overflow

2. **Complex analyses become conversations**
   - Multi-step workflows described in sentences
   - Iterative refinement through dialogue
   - No manual scripting required

3. **Quality increases**
   - AI chooses appropriate methods
   - Spatial relationships preserved
   - Results are reproducible
   - Methodology is documented

4. **Knowledge is captured**
   - Expert workflows become templates
   - Best practices encoded
   - Institutional knowledge preserved

---

## What This Is NOT

❌ **QGIS in chat form** - We're enabling reasoning, not replicating GUIs  
❌ **GDAL command generator** - We're composing workflows, not translating syntax  
❌ **Black-box magic** - We're making expertise accessible, not hiding complexity  
❌ **Replacement for domain knowledge** - We're amplifying expertise, not replacing it

---

## What This IS

✅ **A bridge** between domain expertise and technical implementation  
✅ **An amplifier** for geospatial knowledge that's currently trapped  
✅ **A foundation** for AI that understands spatial reasoning  
✅ **A democratizer** making powerful analysis accessible to experts

---

## Development Approach

### Guiding Questions

When evaluating features, ask:

1. **Does this enable reasoning or just execution?**
   - Good: "AI can understand why this operation is needed"
   - Bad: "AI can execute this command faster"

2. **Does this help domain experts or technical users?**
   - Good: "A hydrologist can express this in domain terms"
   - Bad: "A developer can write this command easier"

3. **Does this compose or isolate?**
   - Good: "This tool connects to other operations naturally"
   - Bad: "This tool only works in isolation"

4. **Does this explain or obscure?**
   - Good: "Users understand what happened and why"
   - Bad: "It works but users don't know how"

### Design Implications

1. **Tool Design** - Tools must be composable, metadata must flow through pipelines, operations must be explainable
2. **API Design** - Expose capabilities (not commands), support workflow description, enable reasoning about data
3. **Architecture** - Plan for stateful workflows, support async operations, enable intermediate result inspection
4. **Documentation** - Emphasize *when* and *why*, provide domain-oriented examples, guide AI reasoning

---

## Personal Story

This project was born from personal experience. As a geospatial analyst, I felt inadequate every time I opened GDAL documentation or tried to parse ASPRS LAS specs. Not because I wasn't smart enough, but because these tools weren't built for people like me.

I went back to school for software engineering, but I never forgot what that feeling of inadequacy felt like.

**This is for everyone who's felt the same.**

For the hydrologists who understand watersheds but struggle with syntax. For the ecologists who understand habitat but can't write Python. For the geologists who understand terrain but get lost in Stack Overflow.

**This is the beginning of making geospatial analysis accessible to those who understand the domain, regardless of their technical background.**

---

## Call to Action

**This vision will take years to realize.** It requires:

- Incremental, thoughtful development
- Partnership with domain experts
- Commitment to accessibility
- Patience with complexity
- Community collaboration

**But the destination is worth it:**

A world where geospatial expertise is no longer limited by technical barriers. Where domain experts can analyze, model, and understand their world through natural conversation with AI that speaks their language.

**That's the vision. That's what we're building.**

---

## Quick Links

- **Repository**: https://github.com/JordanGunn/gdal-mcp
- **Documentation**: [docs/](docs/)
- **Vision**: [docs/design/VISION.md](docs/design/VISION.md)
- **Architecture**: [docs/design/ARCHITECTURE.md](docs/design/ARCHITECTURE.md)
- **Prompting Strategy**: [docs/design/PROMPTING.md](docs/design/PROMPTING.md)
- **Decorator Guide**: [docs/fastmcp/DECORATORS.md](docs/fastmcp/DECORATORS.md)

---

**License**: MIT  
**Status**: MVP Ready for Public Release 🚀  
**Built with ❤️ for the geospatial AI community**

---

*"The best way to predict the future is to invent it." - Alan Kay*

*We're inventing a future where geospatial expertise is democratized.*

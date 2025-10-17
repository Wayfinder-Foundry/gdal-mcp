# FastMCP Prompts Deep Dive

**Status**: Technical Guide  
**Last Updated**: 2025-10-07  
**Purpose**: Understand `@mcp.prompt()` and its role in agentic geospatial reasoning

---

## Table of Contents

1. [What Are MCP Prompts?](#what-are-mcp-prompts)
2. [Why Prompts Are Crucial](#why-prompts-are-crucial)
3. [Tools vs Prompts](#tools-vs-prompts)
4. [How Prompts Enable Our Vision](#how-prompts-enable-our-vision)
5. [Basic Usage](#basic-usage)
6. [Advanced Patterns](#advanced-patterns)
7. [Geospatial Examples](#geospatial-examples)
8. [Best Practices](#best-practices)

---

## What Are MCP Prompts?

### Definition

**MCP Prompts are reusable message templates that guide AI agents in reasoning about tasks.**

Think of them as **conversation starters** that help the AI understand:
- What kind of problem it's solving
- What context is relevant
- What approach to take
- What information to gather first

### Key Concept

```
Tools = Actions the AI can execute
Prompts = Guidance on how to think about problems
```

**Tools answer "what can I do?"**  
**Prompts answer "how should I think about this?"**

---

## Why Prompts Are Crucial

### The Problem Without Prompts

Without prompts, the AI has to figure out from scratch:
- What methodology to use
- What sequence of operations makes sense
- What information is missing
- How to interpret results

**Result**: Inconsistent reasoning, poor workflows, missed edge cases

### The Power of Prompts

With well-designed prompts, you can:

1. **Guide Methodology**: "When analyzing watersheds, always consider..."
2. **Establish Workflows**: "To perform terrain analysis, first verify..."
3. **Encode Domain Knowledge**: "In geospatial analysis, coordinate systems..."
4. **Ensure Best Practices**: "Before reprojection, check..."

**Result**: Consistent, domain-aware reasoning that scales

---

## Tools vs Prompts

### Tools (`@mcp.tool()`)

```python
@mcp.tool()
async def raster_info(input_path: str) -> RasterInfo:
    """Get metadata about a raster file."""
    # Executes an action
    with rasterio.open(input_path) as src:
        return RasterInfo(...)
```

**What it does**: Performs a specific operation  
**When used**: AI has already decided what to do  
**Returns**: Concrete results (metadata, file, data)

### Prompts (`@mcp.prompt()`)

```python
@mcp.prompt()
def analyze_terrain_methodology(
    elevation_file: str,
    analysis_goal: str
) -> str:
    """Guide the AI in terrain analysis methodology."""
    return f"""
    You are analyzing terrain data for: {analysis_goal}
    
    Available elevation data: {elevation_file}
    
    Before proceeding:
    1. Verify the data quality and coordinate system
    2. Consider the appropriate resolution for {analysis_goal}
    3. Determine which terrain derivatives are needed (slope, aspect, etc.)
    4. Plan the workflow sequence
    5. Identify potential edge cases
    
    What is your analysis plan?
    """
```

**What it does**: Guides thinking and planning  
**When used**: Before AI decides what tools to use  
**Returns**: Message that helps AI reason

---

## How Prompts Enable Our Vision

### Recall: The Vision

From `VISION.md`:
> Enable AI agents to **reason about geospatial problems**, not just execute geospatial commands.

### How Prompts Achieve This

#### 1. **Multi-Step Workflow Composition**

**Without Prompts:**
```
User: "Find landslide zones"
AI: → Calls raster_info
    → Gets confused about next step
    → Asks user for guidance
```

**With Prompts:**
```
User: "Find landslide zones"
AI: → Uses landslide_analysis_prompt
    → Understands methodology: slope + hydrology + soil
    → Plans workflow: extract slope → distance to streams → overlay soil
    → Executes tool sequence with proper parameters
    → Returns results with methodology explanation
```

#### 2. **Domain Language Understanding**

**Without Prompts:**
```python
# AI doesn't understand "riparian zone" means buffer + water proximity
User: "Identify riparian zones"
AI: ??? "I don't have a 'riparian_zone' tool"
```

**With Prompts:**
```python
@mcp.prompt()
def riparian_zone_analysis_prompt(stream_file: str, buffer_distance: int) -> str:
    return f"""
    A riparian zone is the interface between land and water bodies.
    
    To identify riparian zones:
    1. Buffer the stream network by {buffer_distance}m
    2. Consider floodplain boundaries
    3. Check vegetation indices if available
    4. Account for elevation changes near streams
    
    Available data: {stream_file}
    Plan your approach.
    """
```

Now AI understands the domain concept and can compose the workflow.

#### 3. **Methodology Encoding**

**Example: Watershed Delineation**

```python
@mcp.prompt()
def watershed_delineation_methodology(
    dem_path: str,
    pour_point: tuple[float, float]
) -> str:
    """Encode watershed delineation best practices."""
    return f"""
    You are performing watershed delineation from a DEM.
    
    DEM: {dem_path}
    Pour point: {pour_point}
    
    Standard methodology:
    1. Fill sinks in DEM (crucial for flow routing)
    2. Calculate flow direction (D8 or D-infinity)
    3. Calculate flow accumulation
    4. Identify drainage network (threshold: >1000 cells)
    5. Delineate watershed from pour point
    6. Validate: watershed should be contiguous, downslope
    
    IMPORTANT CHECKS:
    - DEM resolution appropriate for watershed size?
    - Pour point actually on stream network?
    - Edge artifacts near boundaries?
    
    Plan your workflow with these considerations.
    """
```

Now the AI has domain expertise encoded, not just tools.

#### 4. **Adaptive Reasoning**

```python
@mcp.prompt()
def choose_resampling_method(
    data_type: str,
    source_resolution: float,
    target_resolution: float
) -> str:
    """Help AI choose appropriate resampling."""
    return f"""
    You need to resample {data_type} data.
    Source: {source_resolution}m → Target: {target_resolution}m
    
    Resampling method selection:
    
    - Categorical data (land cover, soil type): Use NEAREST
      → Preserves discrete values
      
    - Continuous data (elevation, temperature): 
      * Upsampling: Use CUBIC or BILINEAR
      * Downsampling: Use AVERAGE or CUBIC
      
    - Elevation models specifically:
      * CUBIC for terrain analysis
      * AVERAGE for general visualization
      
    Consider: {data_type}
    Recommend a method and explain why.
    """
```

AI can now reason about technical choices, not just execute.

---

## Basic Usage

### 1. Simple String Prompt

```python
from fastmcp import FastMCP

mcp = FastMCP("GDAL MCP")

@mcp.prompt()
def ask_about_projection(crs_code: str) -> str:
    """Ask about a coordinate system."""
    return f"Explain the {crs_code} coordinate system and when to use it."
```

**Returns**: Simple string converted to user message

### 2. Prompt with Parameters

```python
@mcp.prompt()
def analyze_raster_quality(
    file_path: str,
    expected_resolution: float,
    expected_crs: str
) -> str:
    """Guide quality assessment of raster data."""
    return f"""
    Assess the quality of: {file_path}
    
    Expected specs:
    - Resolution: {expected_resolution}m
    - CRS: {expected_crs}
    
    Check:
    1. Actual resolution vs expected
    2. CRS matches expectation
    3. No data values present?
    4. Compression artifacts?
    5. Coverage complete?
    
    Report findings and recommend next steps.
    """
```

**Parameters**: Required and optional (with defaults)

### 3. Multi-Message Prompt

```python
from fastmcp.prompts.prompt import Message, PromptResult

@mcp.prompt()
def terrain_analysis_conversation(analysis_type: str) -> PromptResult:
    """Start a terrain analysis conversation."""
    return [
        Message(f"I need to perform {analysis_type} analysis on terrain data."),
        Message("I understand. Let's start by verifying the elevation data. Do you have a DEM file?", role="assistant"),
        Message("Yes, here is the DEM: <file_path>"),
    ]
```

**Returns**: Multi-turn conversation template

---

## Advanced Patterns

### 1. Context Injection

```python
from fastmcp import Context

@mcp.prompt()
async def guided_analysis(
    dataset: str,
    ctx: Context
) -> str:
    """Prompt with access to server context."""
    await ctx.info(f"Generating analysis prompt for {dataset}")
    
    return f"""
    Analyze dataset: {dataset}
    
    You have access to tools for raster and vector analysis.
    Plan a comprehensive workflow.
    """
```

**Use case**: Logging, progress tracking, dynamic content

### 2. Conditional Logic in Prompts

```python
@mcp.prompt()
def adaptive_analysis_prompt(
    data_type: str,
    data_size_gb: float,
    has_gpu: bool = False
) -> str:
    """Adapt prompt based on conditions."""
    
    prompt = f"Analyze {data_type} data ({data_size_gb}GB)\n\n"
    
    if data_size_gb > 10:
        prompt += """
        LARGE DATASET CONSIDERATIONS:
        - Process in tiles/chunks
        - Monitor memory usage
        - Consider downsampling for preview
        """
    
    if has_gpu and data_type == "raster":
        prompt += """
        GPU ACCELERATION AVAILABLE:
        - Use GPU-accelerated operations where possible
        - Batch processing recommended
        """
    
    return prompt
```

**Use case**: Different guidance based on data characteristics

### 3. Metadata-Rich Prompts

```python
@mcp.prompt(
    name="watershed_analysis",
    description="Guide watershed delineation analysis",
    tags={"hydrology", "terrain"},
    meta={"methodology": "standard_hydro", "version": "1.0"}
)
def watershed_prompt(dem: str, pour_point: str) -> str:
    """Watershed analysis methodology."""
    return f"Delineate watershed from {dem} at point {pour_point}"
```

**Use case**: Categorization, versioning, discovery

### 4. Disableable Prompts

```python
@mcp.prompt(enabled=False)
def experimental_analysis() -> str:
    """Experimental methodology - not ready for production."""
    return "Experimental analysis prompt"

# Enable later
experimental_analysis.enable()
```

**Use case**: Feature flags, A/B testing, staged rollouts

---

## Geospatial Examples

### Example 1: Slope Analysis Methodology

```python
@mcp.prompt()
def slope_analysis_methodology(
    dem_path: str,
    analysis_goal: str,
    output_unit: str = "degrees"
) -> str:
    """Guide slope analysis with geospatial best practices."""
    return f"""
    SLOPE ANALYSIS TASK
    
    Input DEM: {dem_path}
    Goal: {analysis_goal}
    Output unit: {output_unit}
    
    METHODOLOGY:
    
    1. Data Verification
       - Check DEM resolution (appropriate for analysis scale?)
       - Verify CRS is projected (not geographic)
       - Check for voids/no-data values
    
    2. Pre-processing
       - Fill small voids if present
       - Consider smoothing for noisy data (optional)
    
    3. Slope Calculation
       - Algorithm: Horn (3x3) or Evans-Young (recommended)
       - Edge handling: Use valid neighbors only
       - Unit: {output_unit}
    
    4. Post-processing
       - Classify if needed (gentle/moderate/steep/very steep)
       - Statistics: mean, std, percentiles
       - Identify areas of interest
    
    5. Quality Check
       - Slope range reasonable? (0-90° for degrees, 0-∞ for percent)
       - No artifacts at tile boundaries?
       - Results match visual inspection?
    
    TOOLS AVAILABLE:
    - raster_info: Check DEM properties
    - raster_stats: Compute slope statistics
    - raster_convert: Save classified output
    
    Plan your workflow considering these steps.
    """
```

**How AI uses this:**
1. Reads methodology
2. Checks data with `raster_info`
3. Plans preprocessing if needed
4. Executes slope calculation
5. Validates results
6. Returns analyzed output with explanation

### Example 2: Multi-Criteria Suitability Analysis

```python
@mcp.prompt()
def suitability_analysis_prompt(
    criteria: list[str],
    weights: dict[str, float],
    goal: str
) -> str:
    """Guide multi-criteria suitability analysis."""
    criteria_str = ", ".join(criteria)
    weights_str = "\n".join(f"  - {k}: {v}" for k, v in weights.items())
    
    return f"""
    MULTI-CRITERIA SUITABILITY ANALYSIS
    
    Goal: {goal}
    
    Criteria to evaluate:
    {criteria_str}
    
    Weights:
    {weights_str}
    
    STANDARD WORKFLOW:
    
    1. Data Preparation
       - Ensure all criteria rasters have same:
         * CRS
         * Resolution
         * Extent
       - Resample/reproject if needed
    
    2. Normalization
       - Standardize each criterion to 0-1 scale
       - Consider: Min-Max normalization or Z-score
       - Direction: Higher values = more suitable?
    
    3. Weighting
       - Apply weights to normalized criteria
       - Verify weights sum to 1.0
    
    4. Combination
       - Weighted sum: Σ(criterion_i × weight_i)
       - Alternative: Weighted product for multiplicative effects
    
    5. Classification
       - Divide into suitability classes (e.g., High/Med/Low)
       - Consider natural breaks or equal intervals
    
    6. Validation
       - Do results match domain expectations?
       - Sensitivity analysis: how stable with different weights?
    
    TOOLS NEEDED:
    - raster_info: Verify consistency
    - raster_reproject: Align spatial properties
    - raster_stats: Compute for normalization
    
    Plan your analysis considering all criteria and their interactions.
    """
```

### Example 3: Stream Network Analysis

```python
@mcp.prompt()
def stream_network_analysis(
    dem_path: str,
    analysis_type: str,
    stream_threshold: int = 1000
) -> str:
    """Guide stream network extraction and analysis."""
    return f"""
    STREAM NETWORK ANALYSIS
    
    DEM: {dem_path}
    Analysis: {analysis_type}
    Flow accumulation threshold: {stream_threshold} cells
    
    HYDROLOGIC WORKFLOW:
    
    Phase 1: Flow Routing
    1. Sink filling
       - Fill depressions to ensure continuous flow
       - Preserve actual sinks if they're real features
    
    2. Flow direction
       - D8: Simple, fast (8 directions)
       - D-infinity: More accurate (continuous direction)
       - Consider data resolution and purpose
    
    3. Flow accumulation
       - Count upslope contributing cells
       - Higher values = more water accumulation
    
    Phase 2: Stream Definition
    4. Threshold flow accumulation
       - Threshold: {stream_threshold} cells
       - Rule: cells above threshold = stream
       - Adjust threshold based on resolution
    
    5. Stream vectorization
       - Convert raster stream to vector
       - Assign stream order (Strahler/Shreve)
       - Calculate length, sinuosity
    
    Phase 3: Network Analysis
    Depending on "{analysis_type}":
    
    - If "extraction": Stop at step 5
    - If "characterization": Add stream order, length, gradient
    - If "watershed": Delineate contributing areas per stream segment
    - If "connectivity": Analyze network topology, confluences
    
    VALIDATION CHECKS:
    - Streams follow topography (flow downhill)?
    - Network is connected (no isolated segments)?
    - Matches known water features?
    
    Plan your workflow for {analysis_type} analysis.
    """
```

### Example 4: Change Detection

```python
@mcp.prompt()
def change_detection_methodology(
    before_image: str,
    after_image: str,
    change_type: str
) -> str:
    """Guide temporal change detection analysis."""
    return f"""
    CHANGE DETECTION ANALYSIS
    
    Before: {before_image}
    After: {after_image}
    Detecting: {change_type}
    
    CHANGE DETECTION WORKFLOW:
    
    Phase 1: Data Alignment
    1. Verify temporal consistency
       - Same season/conditions when possible
       - Account for phenology if vegetation
    
    2. Geometric alignment
       - Must have identical:
         * CRS
         * Resolution
         * Extent
         * Grid alignment (pixel-to-pixel registration)
       - Co-register if needed
    
    3. Radiometric normalization
       - Correct for atmospheric differences
       - Normalize to same scale/range
    
    Phase 2: Change Detection
    
    Method selection for "{change_type}":
    
    - Land cover change:
      * Post-classification comparison
      * Confusion matrix for accuracy
    
    - Vegetation change:
      * NDVI differencing
      * Threshold significant changes
    
    - Urban growth:
      * Built-up index differencing
      * Identify new impervious surfaces
    
    - Disaster damage:
      * Band differencing (specific to disaster type)
      * Classify change magnitude
    
    Phase 3: Analysis
    4. Calculate change magnitude
       - Difference image: After - Before
       - Change percentage: (After-Before)/Before × 100
    
    5. Classify changes
       - Threshold: What magnitude = "significant"?
       - Direction: Increase vs decrease
       - Spatial patterns: clustering, hotspots
    
    6. Quantification
       - Area changed (hectares/km²)
       - Rate of change (per year)
       - Statistical summary
    
    VALIDATION:
    - Do changes match known events?
    - Edge effects minimized?
    - False positives from shadows, clouds?
    
    Plan your change detection workflow.
    """
```

---

## Best Practices

### 1. **Start with Methodology, Not Operations**

❌ **Bad**:
```python
@mcp.prompt()
def quick_analysis(file: str) -> str:
    return f"Run raster_info on {file}"
```

✅ **Good**:
```python
@mcp.prompt()
def guide_data_assessment(file: str, intended_use: str) -> str:
    return f"""
    Before using {file} for {intended_use}:
    
    1. Verify data quality (resolution, coverage, CRS)
    2. Check compatibility with analysis requirements
    3. Identify preprocessing needs
    4. Plan workflow sequence
    
    Start by examining the metadata.
    """
```

### 2. **Encode Domain Knowledge**

Include geospatial expertise that the AI wouldn't know:

```python
@mcp.prompt()
def coastal_elevation_analysis(dem: str) -> str:
    return """
    COASTAL ELEVATION SPECIAL CONSIDERATIONS:
    
    1. Vertical datum critical
       - NAVD88 vs MLLW vs MSL
       - Ensure datum matches tidal reference
    
    2. Accuracy requirements
       - Sea level rise analysis: ±10cm
       - Flood modeling: ±25cm
       - General mapping: ±1m
    
    3. Horizontal resolution
       - Must resolve shoreline features
       - Minimum 1m for detailed analysis
    
    4. Edge effects
       - Land-water boundary smoothing
       - Handle tidal zones appropriately
    
    Plan with these coastal-specific considerations.
    """
```

### 3. **Provide Decision Trees**

Help AI make choices:

```python
@mcp.prompt()
def choose_interpolation(
    data_type: str,
    point_density: str,
    output_use: str
) -> str:
    return f"""
    INTERPOLATION METHOD SELECTION
    
    Data: {data_type}
    Density: {point_density}
    Use: {output_use}
    
    DECISION TREE:
    
    If data_type == "elevation":
        If point_density == "dense":
            → IDW or Natural Neighbor (fast, accurate)
        Else:
            → Kriging (better for sparse data)
    
    If data_type == "temperature/rainfall":
        If spatial_correlation == "strong":
            → Kriging (accounts for spatial structure)
        Else:
            → Spline (smooth surface)
    
    If data_type == "categorical":
        → Natural Neighbor only (preserves values)
    
    If output_use == "analysis":
        → Higher accuracy methods (Kriging)
    If output_use == "visualization":
        → Faster methods acceptable (IDW)
    
    Recommend a method and justify based on these factors.
    """
```

### 4. **Include Validation Steps**

Always guide the AI to validate results:

```python
@mcp.prompt()
def with_validation(operation: str) -> str:
    return f"""
    Operation: {operation}
    
    After completing the operation:
    
    VALIDATION CHECKLIST:
    [ ] Output file exists and is readable
    [ ] CRS preserved or correctly transformed
    [ ] Spatial extent matches expectation
    [ ] No data values handled appropriately
    [ ] Statistics in reasonable range
    [ ] Visual inspection (if applicable)
    [ ] Metadata complete and accurate
    
    Do not proceed until validation passes.
    """
```

### 5. **Make Prompts Composable**

Design prompts to work together:

```python
@mcp.prompt()
def phase_1_data_prep(files: list[str]) -> str:
    return "Data preparation methodology..."

@mcp.prompt()
def phase_2_analysis(prepared_files: list[str]) -> str:
    return "Analysis methodology (assumes phase 1 complete)..."

@mcp.prompt()
def phase_3_validation(analysis_results: str) -> str:
    return "Validation methodology (assumes analysis complete)..."
```

### 6. **Document Prompt Purpose**

Use docstrings to explain when to use each prompt:

```python
@mcp.prompt()
def complex_terrain_analysis(dem: str, analysis_goal: str) -> str:
    """
    Use this prompt for multi-step terrain analysis workflows.
    
    When to use:
    - Analysis requires multiple terrain derivatives
    - Domain expertise needed for parameter selection
    - Results must follow established methodology
    
    When NOT to use:
    - Simple single-step operations
    - Parameters are already known
    - Custom/experimental workflows
    """
    return "Methodology..."
```

---

## How This Changes gdal-mcp Development

### Current State (v0.1.0)

We have **tools** but no **prompts**:
- `raster_info` - executes an operation
- `raster_convert` - executes an operation
- `raster_reproject` - executes an operation

**Result**: AI can execute, but can't reason about methodology

### Next Phase (v0.2.0+)

Add **prompts** to guide reasoning:

```python
# Prompt to guide analysis planning
@mcp.prompt()
def plan_raster_analysis(...)

# Prompt to choose parameters
@mcp.prompt()
def choose_resampling_method(...)

# Prompt to validate results
@mcp.prompt()
def validate_raster_output(...)
```

**Result**: AI can plan workflows, choose methods, validate results

### End Goal (Vision)

Prompts become **domain methodology libraries**:

```python
@mcp.prompt()
def watershed_delineation_complete_workflow(...)

@mcp.prompt()
def multi_criteria_suitability_analysis(...)

@mcp.prompt()
def change_detection_time_series(...)
```

**Result**: AI has geospatial expertise encoded, can reason about complex analyses

---

## Action Items for gdal-mcp

### Immediate (Next Week)

1. **Create first prompt**:
```python
@mcp.prompt()
def analyze_geospatial_data_quality(file_path: str) -> str:
    """Guide data quality assessment before analysis."""
```

2. **Test with Claude Desktop**:
   - See how prompt guides reasoning
   - Iterate on wording
   - Refine methodology

### Short-term (Next Month)

3. **Add methodology prompts**:
   - Terrain analysis methodology
   - Reprojection decision guide
   - Format conversion best practices

4. **Document prompt usage**:
   - When to use prompts vs tools
   - How to compose prompts
   - Examples in QUICKSTART.md

### Long-term (Next Quarter)

5. **Build prompt library**:
   - Cover common workflows
   - Encode domain expertise
   - Version and test

6. **Community contributions**:
   - Accept domain expert input
   - Refine methodologies
   - Expand coverage

---

## References

- **FastMCP Docs**: [Prompts Guide](https://github.com/jlowin/fastmcp/blob/main/docs/servers/prompts.mdx)
- **VISION.md**: Our long-term goals
- **ROADMAP.md**: Implementation plan
- **MCP Spec**: [Prompts Documentation](https://spec.modelcontextprotocol.io/specification/server/prompts/)

---

## Conclusion

**Prompts are how we teach AI agents to reason like geospatial experts.**

Tools give AI hands to work with.  
Prompts give AI a mind to think with.

By encoding domain methodology in prompts, we transform gdal-mcp from a "GDAL command wrapper" into a "geospatial reasoning engine."

**That's the difference between automation and intelligence.**

---

*"The illiterate of the 21st century will not be those who cannot read and write, but those who cannot learn, unlearn, and relearn."* - Alvin Toffler

*We're teaching AI to learn geospatial reasoning. One prompt at a time.*

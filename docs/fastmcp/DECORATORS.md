# FastMCP Decorators Reference

**Purpose**: Quick reference for choosing the right decorator  
**Last Updated**: 2025-10-07

---

## The Three Decorators

```python
@mcp.resource()   # Information to READ
@mcp.tool()       # Actions to EXECUTE
@mcp.prompt()     # Guidance for THINKING
```

---

## Quick Decision Guide

### **Ask These Questions:**

1. **"Does this change anything in the world?"**
   - YES → `@mcp.tool()`
   - NO → Continue to question 2

2. **"Is this information or guidance?"**
   - Information (data, metadata, facts) → `@mcp.resource()`
   - Guidance (methodology, reasoning) → `@mcp.prompt()`

---

## Detailed Comparison

| Aspect | Resource | Tool | Prompt |
|--------|----------|------|--------|
| **Purpose** | Provide information | Execute operations | Guide reasoning |
| **AI Action** | Reads | Executes | Reasons with |
| **Side Effects** | None (read-only) | Yes (writes/changes) | None |
| **Return Type** | Data (dict/str/bytes) | Operation result | Message(s) |
| **User Approval** | Not needed | Required | Not needed |
| **When Called** | During planning | During execution | Before planning |
| **Caching** | Can cache | Don't cache | Can cache |

---

## @mcp.resource() - Information to READ

### **Use When:**
- ✅ Reading data without modification
- ✅ Discovering available files/datasets
- ✅ Getting metadata or properties
- ✅ Providing reference information
- ✅ Checking state or history
- ✅ Computing read-only analysis

### **Don't Use When:**
- ❌ Creating or modifying files
- ❌ Changing configuration
- ❌ Executing external commands
- ❌ Triggering side effects

### **Signature:**
```python
@mcp.resource(uri: str)
def function_name([parameters], [ctx: Context]) -> dict | str | bytes:
    """Docstring describing the resource."""
    return data
```

### **URI Patterns:**
```python
# Static resource
@mcp.resource("reference://crs-guide")

# Dynamic with parameters
@mcp.resource("metadata://{dataset}/info")

# Hierarchical organization
@mcp.resource("workspace://datasets/raster")
```

### **Examples:**

#### Workspace Discovery
```python
@mcp.resource("workspace://datasets")
def list_datasets() -> dict:
    """List all datasets in allowed workspaces."""
    return {
        "datasets": discover_all_geospatial_files(),
        "count": count_datasets()
    }
```

#### File Metadata
```python
@mcp.resource("metadata://{file}/spatial")
def get_spatial_metadata(file: str) -> dict:
    """Get spatial properties of a dataset."""
    with rasterio.open(file) as src:
        return {
            "crs": str(src.crs),
            "bounds": src.bounds,
            "resolution": src.res
        }
```

#### Reference Information
```python
@mcp.resource("reference://resampling-methods")
def get_resampling_guide() -> dict:
    """Guide to resampling method selection."""
    return {
        "nearest": "Categorical data - no interpolation",
        "bilinear": "Continuous data - linear interpolation",
        "cubic": "Elevation - cubic convolution"
    }
```

#### Processing History
```python
@mcp.resource("history://recent-operations")
def get_recent_operations() -> list:
    """Log of recent processing operations."""
    return load_operation_history()
```

---

## @mcp.tool() - Actions to EXECUTE

### **Use When:**
- ✅ Creating or modifying files
- ✅ Deleting or moving data
- ✅ Executing operations with side effects
- ✅ Running external commands
- ✅ Changing system state
- ✅ Making persistent changes

### **Don't Use When:**
- ❌ Just reading or querying data
- ❌ Providing reference information
- ❌ Computing in-memory results without writing

### **Signature:**
```python
@mcp.tool()
async def function_name(
    param1: type,
    param2: type = default,
    ctx: Context | None = None
) -> ResultType:
    """Docstring with USE WHEN, REQUIRES, OUTPUT, SIDE EFFECTS."""
    # Perform operation
    return result
```

### **Examples:**

#### File Creation
```python
@mcp.tool()
async def raster_reproject(
    input_path: str,
    output_path: str,
    target_crs: str,
    resampling: str = "cubic"
) -> dict:
    """
    Reproject a raster to a new coordinate system.
    
    USE WHEN: Need to change CRS of raster data
    REQUIRES: Input raster with valid CRS
    OUTPUT: New reprojected raster file
    SIDE EFFECTS: Creates new file on disk
    """
    with rasterio.open(input_path) as src:
        reproject_raster(src, output_path, target_crs, resampling)
    
    return {"output": output_path, "crs": target_crs}
```

#### File Conversion
```python
@mcp.tool()
async def raster_convert(
    input_path: str,
    output_path: str,
    driver: str = "GTiff",
    compression: str = "DEFLATE"
) -> dict:
    """
    Convert raster to different format.
    
    SIDE EFFECTS: Creates new file
    """
    convert_raster(input_path, output_path, driver, compression)
    return {"output": output_path, "format": driver}
```

#### Computation with File Output
```python
@mcp.tool()
async def raster_compute_slope(
    input_dem: str,
    output_path: str,
    units: str = "degrees"
) -> dict:
    """
    Compute slope from DEM.
    
    SIDE EFFECTS: Creates slope raster file
    """
    compute_slope(input_dem, output_path, units)
    return {"output": output_path}
```

---

## @mcp.prompt() - Guidance for THINKING

### **Use When:**
- ✅ Guiding AI methodology
- ✅ Providing workflow templates
- ✅ Encoding domain knowledge
- ✅ Establishing best practices
- ✅ Helping AI choose approaches
- ✅ Structuring multi-step reasoning

### **Don't Use When:**
- ❌ Executing operations
- ❌ Reading data
- ❌ Providing static facts (use resource instead)

### **Signature:**
```python
@mcp.prompt()
def function_name(
    param1: type,
    param2: type = default
) -> str | PromptMessage | list[PromptMessage]:
    """Docstring describing the prompt's purpose."""
    return message_content
```

### **Examples:**

#### Methodology Guidance
```python
@mcp.prompt()
def terrain_analysis_methodology(
    dem_path: str,
    analysis_goal: str
) -> str:
    """Guide AI through terrain analysis approach."""
    return f"""
    TERRAIN ANALYSIS: {analysis_goal}
    
    Input DEM: {dem_path}
    
    Recommended workflow:
    1. Verify DEM quality (CRS, resolution, voids)
    2. Choose appropriate algorithm for {analysis_goal}
    3. Set parameters based on data characteristics
    4. Execute computation
    5. Validate results
    
    What is your analysis plan?
    """
```

#### Parameter Selection Guide
```python
@mcp.prompt()
def choose_resampling_method(
    data_type: str,
    operation: str
) -> str:
    """Help AI choose appropriate resampling method."""
    return f"""
    RESAMPLING METHOD SELECTION
    
    Data type: {data_type}
    Operation: {operation}
    
    Decision guide:
    - Categorical data (land cover, soil type) → nearest
    - Continuous data (elevation, temperature) → cubic or bilinear
    - Upsampling → cubic (best quality)
    - Downsampling → average (best aggregation)
    
    Recommend a method and explain your reasoning.
    """
```

#### Workflow Planning
```python
@mcp.prompt()
def plan_multi_criteria_analysis(
    criteria: list[str],
    goal: str
) -> str:
    """Guide AI through multi-criteria suitability analysis."""
    return f"""
    MULTI-CRITERIA ANALYSIS: {goal}
    
    Criteria: {", ".join(criteria)}
    
    Standard workflow:
    1. Verify all criteria have same spatial properties
    2. Normalize each criterion to 0-1 scale
    3. Apply weights (ensure sum = 1.0)
    4. Combine with weighted overlay
    5. Classify into suitability classes
    6. Validate results
    
    Plan your analysis considering these steps.
    """
```

---

## Common Patterns

### **Pattern 1: Info as Both Resource and Tool**

When users might want to explicitly request information, provide both:

```python
# Resource: AI can query freely
@mcp.resource("metadata://{file}/info")
def get_file_metadata(file: str) -> dict:
    return extract_metadata(file)

# Tool: User explicitly requests
@mcp.tool()
async def raster_info(input_path: str) -> RasterInfo:
    """Show detailed raster information."""
    return extract_metadata(input_path)
```

### **Pattern 2: Resource + Prompt + Tool**

Complete guidance chain:

```python
# 1. Resource: What data is available
@mcp.resource("workspace://datasets")
def list_datasets() -> dict: ...

# 2. Prompt: How to choose approach
@mcp.prompt()
def choose_processing_method(data_characteristics: dict) -> str: ...

# 3. Tool: Execute the operation
@mcp.tool()
async def process_raster(input_path: str, method: str) -> dict: ...
```

### **Pattern 3: Parametric Resources**

Resources that adapt based on parameters:

```python
@mcp.resource("epsg://{code}/info")
def get_epsg_info(code: str) -> dict:
    """Different content per EPSG code."""
    return lookup_epsg(code)
```

### **Pattern 4: Context Injection**

Access server context in any decorator:

```python
from fastmcp import Context

@mcp.resource("workspace://current-state")
async def get_state(ctx: Context) -> dict:
    await ctx.info("Fetching workspace state")
    return {"state": get_current_state()}
```

---

## Decision Examples

### **Scenario 1: "Get CRS information"**

**Question**: Get details about EPSG:4326

**Answer**: Resource
```python
@mcp.resource("crs://details/{code}")
def get_crs_details(code: str) -> dict:
    # Read-only, no changes
```

**Why**: Just reading information, no side effects

---

### **Scenario 2: "Reproject a raster"**

**Question**: Change raster CRS from 4326 to 3857

**Answer**: Tool
```python
@mcp.tool()
async def raster_reproject(...) -> dict:
    # Creates new file
```

**Why**: Creates new file, changes filesystem

---

### **Scenario 3: "How to choose CRS"**

**Question**: Guide AI in selecting appropriate CRS

**Answer**: Prompt
```python
@mcp.prompt()
def choose_crs_methodology(region: str, use_case: str) -> str:
    # Methodology guidance
```

**Why**: Provides reasoning guidance, not data or action

---

### **Scenario 4: "List available datasets"**

**Question**: What datasets exist in workspace

**Answer**: Resource
```python
@mcp.resource("workspace://datasets")
def list_datasets() -> dict:
    # Read-only discovery
```

**Why**: Just reading directory, no changes

---

### **Scenario 5: "Compute statistics"**

**Question**: Calculate min/max/mean from raster

**If returns computed values only**: Resource
```python
@mcp.resource("stats://{dataset}/summary")
def compute_stats(dataset: str) -> dict:
    # Compute in memory, don't write
```

**If writes statistics to file**: Tool
```python
@mcp.tool()
async def raster_stats(input_path: str, output_stats: str) -> dict:
    # Writes stats file
```

---

### **Scenario 6: "Validate workflow approach"**

**Question**: Is this terrain analysis approach correct?

**Answer**: Prompt
```python
@mcp.prompt()
def validate_terrain_workflow(steps: list[str]) -> str:
    # Validate methodology
```

**Why**: Guides reasoning about approach

---

## URI Scheme Recommendations

### **Resources**

Use descriptive, hierarchical URI schemes:

```
reference://           # Static reference info
├── crs/
├── terrain/
└── glossary/

catalog://            # Dataset catalogs
├── datasets/
└── formats/

metadata://           # File metadata
└── {file}/

workspace://          # Workspace info
├── datasets
└── configuration

history://            # Processing history
└── operations

state://              # Current state
└── session
```

---

## Best Practices

### **For Resources:**

1. **Use clear URI schemes** - `reference://`, `catalog://`, `metadata://`
2. **Keep responses focused** - One concern per resource
3. **Cache expensive operations** - Use `@lru_cache` for repeated calls
4. **Provide rich metadata** - Use `name`, `description`, `tags`
5. **Handle errors gracefully** - Return error objects, not exceptions

### **For Tools:**

1. **Document side effects** - Always note what changes
2. **Use descriptive names** - Action verbs (convert, reproject, compute)
3. **Validate inputs** - Check paths, parameters before execution
4. **Return operation metadata** - Output paths, parameters used
5. **Enable dry-run mode** - When possible, allow previewing changes

### **For Prompts:**

1. **Focus on methodology** - "How to think", not "what to do"
2. **Include decision trees** - Help AI choose between options
3. **Reference resources** - Point to supporting information
4. **Be domain-specific** - Encode expert knowledge
5. **End with questions** - Prompt AI to plan before acting

---

## Anti-Patterns to Avoid

### ❌ **Don't: Use Tool for Read-Only Operations**

```python
# Bad
@mcp.tool()
async def get_file_info(path: str) -> dict:
    # Just reading, no writes
```

### ✅ **Do: Use Resource Instead**

```python
# Good
@mcp.resource("metadata://{file}/info")
def get_file_info(file: str) -> dict:
    # Read-only operation
```

---

### ❌ **Don't: Use Resource for Operations**

```python
# Bad
@mcp.resource("operations://reproject")
def do_reproject(input: str, output: str) -> dict:
    # Creates files!
```

### ✅ **Do: Use Tool Instead**

```python
# Good
@mcp.tool()
async def raster_reproject(input_path: str, output_path: str) -> dict:
    # Properly declared as tool
```

---

### ❌ **Don't: Use Prompt for Facts**

```python
# Bad
@mcp.prompt()
def get_epsg_codes() -> str:
    return "EPSG:4326 is WGS 84..."
```

### ✅ **Do: Use Resource for Facts**

```python
# Good
@mcp.resource("reference://epsg-codes")
def get_epsg_codes() -> dict:
    return {"4326": "WGS 84", ...}
```

---

## Summary

**Think of it as:**

- **Resources** = 📚 Library (information to browse)
- **Tools** = 🔨 Workshop (equipment to use)
- **Prompts** = 📖 Methodology guide (how to think)

**The golden rule:**

> If it changes anything → Tool  
> If it provides information → Resource  
> If it guides thinking → Prompt

---

## Quick Reference Table

| What You're Building | Use This |
|---------------------|----------|
| File/dataset discovery | Resource |
| CRS/format reference | Resource |
| Metadata extraction | Resource |
| Processing history | Resource |
| Workspace state | Resource |
| File creation/modification | Tool |
| Format conversion | Tool |
| Reprojection | Tool |
| Analysis computation (writes file) | Tool |
| Configuration changes | Tool |
| Methodology guidance | Prompt |
| Workflow planning | Prompt |
| Parameter selection guide | Prompt |
| Best practices | Prompt |
| Decision trees | Prompt |

---

**Last Updated**: 2025-10-07  
**Related Docs**: [PROMPTS.md](./PROMPTS.md), [RESOURCES.md](./RESOURCES.md)

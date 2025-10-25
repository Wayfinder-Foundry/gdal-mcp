# Reflection System — Technical Documentation

## Overview

The **Reflection System** is GDAL MCP's core innovation: a middleware-based epistemic governance layer that enforces methodological justification before executing geospatial operations with significant consequences.

**Key principle:** AI agents should not blindly execute operations that require domain expertise. They must demonstrate understanding through structured reasoning.

## Architecture

### Components

```
User Request
    ↓
AI Agent (Claude)
    ↓
MCP Tool Call (e.g., raster_reproject)
    ↓
FastMCP Server
    ↓
ReflectionMiddleware.on_call_tool()
    ├─→ Check cache (.preflight/justifications/{domain}/)
    ├─→ If cached: proceed immediately
    └─→ If missing: raise ToolError → trigger prompt
         ↓
    AI calls prompt (justify_crs_selection)
         ↓
    AI provides structured justification
         ↓
    AI calls store_justification
         ↓
    Justification cached with SHA256 hash
         ↓
    AI retries original tool call
         ↓
    Cache hit → execution proceeds
         ↓
    Tool executes with validated methodology
```

### File Structure

```
src/
├── middleware/
│   ├── reflection_middleware.py      # FastMCP middleware (tool interception)
│   ├── reflection_transform.py       # Cache checking & hash computation
│   ├── reflection_config.py          # Declarative tool→prompt mapping
│   └── reflection_store.py           # Persistent storage (Pydantic models)
├── prompts/
│   ├── crs.py                        # CRS selection reasoning prompt
│   ├── resampling.py                 # Resampling method reasoning prompt
│   └── justification.py              # Shared schema definitions
└── tools/
    └── reflection/
        └── store_justification.py    # Explicit storage tool for AI

.preflight/
└── justifications/
    ├── crs_datum/
    │   └── sha256:abc123...def.json
    └── resampling/
        └── sha256:456789...xyz.json
```

## Reflection Domains

### Current (v1.0.0)

#### `crs_datum` — Coordinate Reference System Selection

**Triggered by:** `raster_reproject(dst_crs=...)`

**Questions enforced:**
- What spatial property must be preserved? (distance, area, shape, angle)
- Why is this CRS appropriate for the analysis intent?
- What alternative projections were considered?
- What distortion tradeoffs are acceptable?

**Example justification:**
```json
{
  "intent": "Preserve area accuracy for land cover classification statistics",
  "alternatives": [
    {
      "crs": "EPSG:4326",
      "why_not": "Geographic CRS distorts area significantly at high latitudes"
    },
    {
      "crs": "EPSG:3857",
      "why_not": "Web Mercator has extreme area distortion away from equator"
    }
  ],
  "choice": {
    "crs": "EPSG:6933",
    "rationale": "Cylindrical Equal Area preserves area globally, critical for accurate hectare calculations in classification stats",
    "tradeoffs": "Shape distortion acceptable since only measuring total area per class"
  },
  "confidence": "high"
}
```

**Cache key includes:** `dst_crs` (source CRS not included to allow flexibility)

#### `resampling` — Interpolation Method Selection

**Triggered by:** `raster_reproject(resampling=...)`

**Questions enforced:**
- What signal property must be preserved? (exact values, smooth gradients, class boundaries)
- Is the data categorical (discrete) or continuous (measurements)?
- What artifacts might this method introduce?
- Why not other resampling methods?

**Example justification:**
```json
{
  "intent": "Preserve exact class values for land cover classification",
  "alternatives": [
    {
      "method": "bilinear",
      "why_not": "Introduces new pixel values between classes, creating invalid categories"
    },
    {
      "method": "cubic",
      "why_not": "Even worse smoothing artifacts, can create negative values for positive-only data"
    }
  ],
  "choice": {
    "method": "nearest",
    "rationale": "Only method that preserves exact input values, essential for categorical data where each integer represents a distinct class",
    "tradeoffs": "Creates blocky appearance at class boundaries, but classification accuracy more important than visual smoothness"
  },
  "confidence": "high"
}
```

**Cache key includes:** `method` parameter only

### Planned (v1.1.0+)

#### `hydrology` — DEM Conditioning & Flow Analysis

**Will trigger on:**
- DEM preprocessing operations (fill sinks, breach depressions)
- Flow direction algorithm selection (D8, D-infinity, MFD)
- Flow accumulation thresholds for stream network delineation

**Questions to enforce:**
- What hydrologic assumption is being made? (D8 vs multi-flow)
- How should depressions be handled? (fill, breach, or preserve)
- What drainage area threshold defines a stream?

#### `aggregation` — Multi-Resolution & Temporal Composition

**Will trigger on:**
- Zonal statistics from different resolution sources
- Temporal compositing (max NDVI, median reflectance)
- Data fusion from multiple sensors

**Questions to enforce:**
- How should resolution differences be reconciled?
- What aggregation function preserves the signal?
- What happens to outliers and nodata?

#### `format_selection` — Output Format Optimization

**Will trigger on:**
- Format conversion with compression choices
- Tiling strategy decisions
- Overview level selection

**Questions to enforce:**
- What access pattern will be used? (sequential, random, cloud)
- Lossless or lossy compression acceptable?
- What zoom levels are needed?

## Cache Mechanism

### Hash Computation

Cache keys are computed using SHA256 of:
1. **Tool name** (e.g., `raster_reproject`)
2. **Normalized prompt arguments** (sorted dict, stable JSON)
3. **Prompt name** (e.g., `justify_crs_selection`)
4. **Domain** (e.g., `crs_datum`)

**Example:**
```python
# Input parameters
tool_name = "raster_reproject"
prompt_args = {"dst_crs": "EPSG:3857"}
prompt_name = "justify_crs_selection"
domain = "crs_datum"

# Normalized for hashing
normalized = json.dumps(prompt_args, sort_keys=True)
# → '{"dst_crs": "EPSG:3857"}'

# Combined hash input
hash_input = f"{tool_name}::{normalized}::{domain}::{prompt_hash}"
# → "raster_reproject::{'dst_crs': 'EPSG:3857'}::crs_datum::sha256:..."

# Final cache key
cache_key = hashlib.sha256(hash_input.encode()).hexdigest()
# → "sha256:abc123def456..."
```

### Cache Storage

**Location:** `.preflight/justifications/{domain}/sha256:{hash}.json`

**Structure:**
```json
{
  "tool_name": "raster_reproject",
  "domain": "crs_datum",
  "prompt_name": "justify_crs_selection",
  "prompt_args": {
    "dst_crs": "EPSG:3857"
  },
  "justification": {
    "intent": "...",
    "alternatives": [...],
    "choice": {...},
    "confidence": "high"
  },
  "timestamp": "2025-10-24T16:30:00Z",
  "cache_key": "sha256:abc123def456..."
}
```

### Cache Behavior

**Cache hit conditions:**
- Same tool + same parameters + same domain → instant execution
- Example: Second `raster_reproject(..., dst_crs="EPSG:3857", resampling="cubic")` with identical parameters

**Cache miss conditions:**
- Different parameter value → new justification required
- Example: Change `dst_crs="EPSG:4326"` → triggers new CRS prompt

**Partial cache:**
- Multiple reflection domains per tool
- Each domain cached independently
- Example: `raster_reproject` requires both CRS and resampling justifications
  - If CRS cached but resampling new → only resampling prompt triggered

## Prompt Structure

All reflection prompts follow a consistent structure:

### Input Template

```python
@mcp.prompt(
    name="justify_*",
    description="Pre-execution micro-guidance for * reasoning.",
)
def justify_something(parameter: str) -> list[Message]:
    content = f"""
Before executing operation with {parameter}:

**Reason through:**
• What property must be preserved?
• Why is this choice appropriate?
• What alternatives were considered?
• What tradeoffs are acceptable?

**Return strict JSON:**
{{
  "intent": "...",
  "alternatives": [
    {{"method": "...", "why_not": "..."}}
  ],
  "choice": {{
    "method": "{parameter}",
    "rationale": "...",
    "tradeoffs": "..."
  }},
  "confidence": "low|medium|high"
}}
"""
    return [UserMessage(content=content)]
```

### Output Schema (Pydantic)

```python
class Alternative(BaseModel):
    """Alternative method considered but rejected."""
    method: str = Field(description="Alternative approach name")
    why_not: str = Field(description="Reason for rejection")

class Choice(BaseModel):
    """Selected method with justification."""
    method: str = Field(description="Chosen approach")
    rationale: str = Field(description="Why this fits the intent")
    tradeoffs: str = Field(description="Known limitations or distortions")

class Justification(BaseModel):
    """Complete epistemic justification."""
    intent: str = Field(description="What property/goal to preserve")
    alternatives: list[Alternative] = Field(description="Rejected options")
    choice: Choice = Field(description="Selected method with reasoning")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence in this methodological choice"
    )
```

## Integration Guide

### Adding Reflection to a New Tool

**Step 1: Create the prompt**

```python
# src/prompts/my_domain.py
from fastmcp import FastMCP
from fastmcp.prompts import UserMessage

def register(mcp: FastMCP) -> None:
    @mcp.prompt(
        name="justify_my_operation",
        description="Reasoning for my operation parameters.",
        tags={"reasoning", "my_domain"},
    )
    def justify_my_operation(param: str) -> list[Message]:
        content = f"""
Before executing with {param}:

**Reason through:**
• Why this parameter value?
• What alternatives exist?
• What are the tradeoffs?

**Return JSON:**
{{
  "intent": "...",
  "alternatives": [{{"method": "...", "why_not": "..."}}],
  "choice": {{"method": "{param}", "rationale": "...", "tradeoffs": "..."}},
  "confidence": "high"
}}
"""
        return [UserMessage(content=content)]
```

**Step 2: Register prompt**

```python
# src/prompts/__init__.py
import src.prompts.my_domain

def register_prompts(mcp: FastMCP) -> None:
    # ... existing prompts ...
    src.prompts.my_domain.register(mcp)
```

**Step 3: Add reflection config**

```python
# src/middleware/reflection_config.py
TOOL_REFLECTIONS: dict[str, list[ReflectionSpec]] = {
    # ... existing tools ...
    "my_new_tool": [
        ReflectionSpec(
            domain="my_domain",
            prompt_name="justify_my_operation",
            args_fn=lambda kwargs: {"param": kwargs["param"]},
        ),
    ],
}
```

**Step 4: Tool executes automatically with reflection**

No decorator needed! Middleware intercepts all tool calls and checks `TOOL_REFLECTIONS` config.

### Testing Reflection Integration

```bash
# Clear cache to force new justifications
rm -rf .preflight/justifications/my_domain/

# Trigger the tool via Claude
# Should see prompt, provide justification, then execute

# Verify cache created
ls .preflight/justifications/my_domain/

# Second invocation should cache hit (no prompt)
```

## Debugging

### Enable debug logging

```python
# In tool or middleware
logger.setLevel(logging.DEBUG)
```

**Outputs:**
```
DEBUG: Reflection middleware intercepting tool call: raster_reproject
DEBUG: Checking cache for domain: crs_datum (hash=sha256:abc123...)
INFO: Reflection cache miss for raster_reproject: crs_datum
DEBUG: Checking cache for domain: resampling (hash=sha256:def456...)
INFO: Reflection cache hit for raster_reproject: resampling
```

### Inspect cache

```bash
# List all cached justifications
find .preflight/justifications -type f -name "*.json"

# View specific justification
cat .preflight/justifications/crs_datum/sha256:abc123*.json | jq .

# Count cache entries by domain
find .preflight/justifications -type f | awk -F'/' '{print $(NF-1)}' | sort | uniq -c
```

### Bypass cache (for testing)

```bash
# Temporary: rename cache directory
mv .preflight/justifications .preflight/justifications.backup

# All operations will now trigger prompts

# Restore
mv .preflight/justifications.backup .preflight/justifications
```

## Best Practices

### For AI Agents

1. **Provide specific reasoning** — Don't just restate the parameter
   - ❌ "Using EPSG:3857 because user requested it"
   - ✅ "Using EPSG:3857 to preserve angular relationships for web tile rendering, accepting area distortion as visualization-only use case"

2. **Consider real alternatives** — Show domain understanding
   - ❌ Single alternative that's obviously wrong
   - ✅ Multiple plausible alternatives with specific technical reasons for rejection

3. **Acknowledge tradeoffs** — Demonstrate awareness of limitations
   - ❌ "No tradeoffs, perfect choice"
   - ✅ "Distance/area distortion increases with latitude, acceptable within ±45° bounds of this dataset"

4. **Match confidence to certainty**
   - `high` — Standard methodology, well-understood consequences
   - `medium` — Reasonable choice but alternatives viable
   - `low` — Uncertain about best approach, would benefit from expert review

### For Developers

1. **Keep prompts focused** — One methodological choice per prompt
   - Each reflection domain should address a single decision axis
   - Avoid combining CRS + resampling in one prompt

2. **Make cache keys precise** — Include only decision-relevant parameters
   - CRS justification doesn't need source CRS (only destination matters)
   - Resampling justification doesn't need CRS at all

3. **Design for composition** — Reflection prompts should chain well
   - Hydrology workflow: condition → flow direction → accumulation
   - Each step can reference previous justifications

4. **Test cache behavior** — Verify hit/miss logic
   - See [test/REFLECTION_TESTING.md](../test/REFLECTION_TESTING.md)
   - Test same parameters, different parameters, partial changes

## Performance Considerations

### Latency

**First invocation (cache miss):**
- Prompt generation: ~50ms
- LLM reasoning: ~10-30 seconds (depends on model)
- Storage: ~10ms
- Total: **~10-30 seconds**

**Subsequent invocations (cache hit):**
- Hash computation: ~1ms
- Cache lookup: ~5ms
- Total: **~6ms** (negligible)

**Optimization:** Cache hit rate > 80% in typical workflows

### Storage

**Cache size:**
- ~1-2KB per justification (JSON text)
- 100 unique operations = ~200KB
- 1000 unique operations = ~2MB

**Cleanup:** Justifications persist across sessions. Manual cleanup:
```bash
# Remove old justifications (older than 30 days)
find .preflight/justifications -type f -mtime +30 -delete

# Clear all cache
rm -rf .preflight/justifications/*
```

## Security Considerations

### Workspace Isolation

Justification cache is workspace-specific (`.preflight/` in project root). Different projects maintain separate caches.

### Justification Integrity

Cache files are:
- **Content-addressed** — SHA256 hash prevents tampering
- **Structured** — Pydantic validation on read
- **Auditable** — Plain JSON for inspection

### No Automatic Execution

Middleware **prevents** execution without justification. AI cannot bypass by:
- Calling tool directly (middleware intercepts)
- Providing empty justification (Pydantic validation)
- Reusing wrong justification (hash mismatch)

## Future Enhancements

### v1.1.0
- [ ] Justification chaining (link related operations)
- [ ] Provenance export (markdown reports)
- [ ] Confidence thresholds (require review if < medium)

### v1.2.0
- [ ] Alternative workflow suggestions
- [ ] Quality assessment prompts
- [ ] Shared team justification libraries

### v2.0.0
- [ ] Uncertainty propagation through chains
- [ ] Multi-agent collaboration on justifications
- [ ] Automated workflow discovery

---

**See also:**
- [test/REFLECTION_TESTING.md](../test/REFLECTION_TESTING.md) — Comprehensive testing guide
- [docs/ADR/0026-prompting-and-epistemic-governance.md](ADR/0026-prompting-and-epistemic-governance.md) — Design rationale
- [README.md](../README.md#-reflection-system-v100) — User-facing overview

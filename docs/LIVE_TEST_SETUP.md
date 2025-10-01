# Live MCP Testing with Claude Desktop

This guide walks through testing the GDAL MCP server with Claude Desktop for the first time.

## Prerequisites

- Claude Desktop installed
- Test data in an accessible directory
- Production wheel built: `dist/gdal_mcp-0.0.1-py3-none-any.whl`

## Step 1: Configure Claude Desktop

Edit Claude Desktop's MCP configuration file:

**Location:** `~/.config/Claude/claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "gdal-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "/home/jgodau/work/personal/gdal-mcp/dist/gdal_mcp-0.0.1-py3-none-any.whl",
        "gdal-mcp"
      ],
      "env": {
        "GDAL_MCP_WORKSPACES": "/home/jgodau/work/personal/gdal-mcp/test/data"
      }
    }
  }
}
```

**Key Points:**
- `command`: Uses `uvx` to run the wheel in an isolated environment
- `args`: Points to the local wheel file (absolute path)
- `env.GDAL_MCP_WORKSPACES`: Restricts access to test data directory only

## Step 2: Restart Claude Desktop

After editing the config:
1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. Check that the MCP server appears in the available tools

## Step 3: Live Test Scenarios

### Scenario 1: Raster Info (Read-Only)

**Prompt to Claude:**
```
Use the raster.info tool to inspect test/data/tiny_raster_gtiff.tif 
and tell me:
1. What CRS is it in?
2. What are the dimensions (width x height)?
3. How many bands does it have?
4. What's the pixel size?
```

**Expected:**
- ✅ Tool executes successfully
- ✅ Returns structured metadata
- ✅ Context logging appears (if supported by Claude UI)
- ✅ LLM can interpret and explain the results

### Scenario 2: Raster Statistics

**Prompt to Claude:**
```
Calculate statistics for test/data/tiny_raster_gtiff.tif including:
- Min, max, mean, stddev for each band
- Generate a histogram with 10 bins
```

**Expected:**
- ✅ Tool executes with progress reporting
- ✅ Returns per-band statistics
- ✅ Histogram data included
- ✅ LLM can summarize findings

### Scenario 3: Raster Conversion

**Prompt to Claude:**
```
Convert test/data/tiny_raster_gtiff.tif to Cloud-Optimized GeoTIFF (COG) format.
Save as test/data/output_cog.tif with LZW compression.
```

**Expected:**
- ✅ Tool creates output file
- ✅ File is within workspace (validated by middleware)
- ✅ Returns ResourceRef with file size, metadata
- ✅ LLM confirms successful conversion

### Scenario 4: Workspace Security Test (Should FAIL)

**Prompt to Claude:**
```
Try to read the file at /etc/passwd using raster.info
```

**Expected:**
- ❌ Tool execution denied by PathValidationMiddleware
- ❌ ToolError: "Access denied: '/etc/passwd' outside allowed workspaces"
- ✅ LLM explains that access was denied for security reasons
- ✅ Tool never executes (middleware blocks it)

### Scenario 5: Vector Info

**Prompt to Claude:**
```
Inspect test/data/tiny_vector.geojson and tell me:
1. What driver is it using?
2. What CRS?
3. What geometry types are present?
4. What fields/attributes does it have?
```

**Expected:**
- ✅ Tool executes successfully
- ✅ Returns structured vector metadata
- ✅ LLM can explain the vector dataset structure

### Scenario 6: Multi-Step Workflow

**Prompt to Claude:**
```
I need to:
1. Check the CRS of test/data/tiny_raster_gtiff.tif
2. If it's not in Web Mercator (EPSG:3857), reproject it to Web Mercator
3. Save the result as test/data/webmercator_output.tif
4. Calculate statistics on the reprojected file
```

**Expected:**
- ✅ Claude chains multiple tool calls
- ✅ Each tool provides context to inform next step
- ✅ All paths validated by middleware
- ✅ LLM provides coherent workflow summary

## Step 4: Validation Checklist

After running test scenarios, verify:

**MCP Server:**
- [ ] Server starts without errors
- [ ] All 5 tools are available (raster.info, convert, reproject, stats, vector.info)
- [ ] Workspace scoping is active (GDAL_MCP_WORKSPACES env var loaded)

**Tool Execution:**
- [ ] Read-only tools work (info, stats)
- [ ] Write tools work (convert, reproject)
- [ ] Output files are created in workspace
- [ ] Structured outputs (Pydantic models) are returned

**Security:**
- [ ] Paths outside workspace are denied
- [ ] Error messages are helpful and user-friendly
- [ ] Middleware logs validation checks (if logging enabled)
- [ ] No way to bypass workspace boundaries

**LLM Integration:**
- [ ] Claude can call tools successfully
- [ ] Claude can interpret structured outputs
- [ ] Claude can chain multiple tool calls
- [ ] Claude explains results in natural language

**Context & Progress:**
- [ ] Context logging appears (ctx.info, ctx.debug) - if Claude UI supports
- [ ] Progress reporting works for long operations - if Claude UI supports
- [ ] Error messages are LLM-friendly (ToolError format)

## Step 5: Troubleshooting

### Server Won't Start

**Check:**
```bash
# Verify wheel exists
ls -lh /home/jgodau/work/personal/gdal-mcp/dist/gdal_mcp-0.0.1-py3-none-any.whl

# Test server manually
uvx --from /home/jgodau/work/personal/gdal-mcp/dist/gdal_mcp-0.0.1-py3-none-any.whl gdal-mcp --help
```

### Tools Not Appearing

**Check Claude Desktop logs:**
- Look for MCP server initialization errors
- Verify config file syntax (valid JSON)
- Restart Claude Desktop completely

### Workspace Validation Errors

**Check:**
```bash
# Verify test data exists
ls -R /home/jgodau/work/personal/gdal-mcp/test/data/

# Check GDAL_MCP_WORKSPACES is set correctly
# Should be absolute path to test data directory
```

### Tool Execution Fails

**Check:**
- File paths are absolute or relative to workspace
- Test data files are readable
- Output directory has write permissions
- Rasterio/pyogrio dependencies are installed (should be automatic via uvx)

## Expected Outcomes

**Success Indicators:**
- ✅ All 5 tools execute successfully
- ✅ Workspace scoping blocks unauthorized access
- ✅ Claude can interpret and chain tool calls
- ✅ Error messages are helpful and actionable
- ✅ Structured outputs work (Pydantic → JSON → LLM)

**This is a HISTORIC milestone:**
- First production-ready Python-native GDAL MCP server
- FastMCP best practices (Context, middleware, native config)
- Security-first design (workspace scoping)
- LLM-optimized descriptions
- Comprehensive test coverage (23/23 tests)

## Next Steps After Live Testing

1. **Document findings** - Note any issues or improvements
2. **Iterate if needed** - Fix any bugs discovered
3. **Performance testing** - Test with larger datasets
4. **Docker deployment** - Create Dockerfile for production
5. **PyPI publishing** - Release to public registry
6. **Documentation** - Update README with live test results

---

**Good luck with the first live test! 🚀**

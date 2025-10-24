# Manual Testing Guide - Reflection Preflight System

This guide provides step-by-step instructions for manually testing the reflection preflight system with Claude Desktop.

## Prerequisites

- Claude Desktop installed and configured
- gdal-mcp-dev server configured in MCP settings
- Test data available at `test/data/sample.tif`

## MCP Configuration

Ensure your Claude Desktop config includes:

```json
{
  "mcpServers": {
    "gdal-mcp-dev": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/jgodau/work/personal/gdal-mcp",
        "gdal",
        "--transport",
        "stdio"
      ],
      "env": {
        "GDAL_CACHEMAX": "512",
        "GDAL_WORKSPACE": "/home/jgodau/work/personal/gdal-mcp/test/data"
      }
    }
  }
}
```

## Test 1: Trigger CRS Selection Reflection

### Objective
Verify that the CRS selection reflection prompt is triggered and justification is stored.

### Steps

1. **Ask Claude Desktop:**
   ```
   Use gdal-mcp-dev to get info about test/data/sample.tif, then reproject it 
   to EPSG:3857 (Web Mercator) using cubic resampling. Save the output as 
   test/data/sample_webmercator.tif
   ```

2. **Expected Behavior:**
   - Claude will first call `raster_info` to inspect the source file
   - The `raster_reproject` tool will be invoked with the specified parameters
   - The `@requires_reflection` decorator will intercept the call
   - Two reflection prompts will be sent to Claude:
     - **CRS Selection Prompt**: Reasoning about EPSG:3857 choice
     - **Resampling Method Prompt**: Reasoning about cubic resampling

3. **Watch For:**
   - Claude reasoning through CRS properties (distance/area/shape preservation)
   - Claude considering alternatives (other EPSG codes)
   - Claude justifying the cubic resampling choice
   - Claude explaining tradeoffs

4. **Verify Success:**
   ```bash
   # Check that output file was created
   ls -lh test/data/sample_webmercator.tif
   
   # Check that justifications were stored
   find .preflight/justifications -type f -name "*.json" -newer test/data/sample.tif
   ```

5. **Expected Output:**
   - New file: `test/data/sample_webmercator.tif`
   - New justification files in `.preflight/justifications/crs_datum/` and `.preflight/justifications/resampling/`

### Success Criteria
- ✅ Reflection prompts appeared in Claude's reasoning
- ✅ Claude provided domain-aware justifications
- ✅ Output file created successfully
- ✅ Justification JSON files stored in `.preflight/justifications/`

---

## Test 2: Verify Cache Hit (No Re-prompting)

### Objective
Verify that cached justifications are reused for identical operations.

### Steps

1. **Ask Claude Desktop:**
   ```
   Use gdal-mcp-dev to reproject test/data/sample.tif to EPSG:3857 
   with cubic resampling again, but save it as test/data/sample_webmercator2.tif
   ```

2. **Expected Behavior:**
   - The `raster_reproject` tool will be invoked
   - The reflection middleware will check the cache
   - **No reflection prompts should appear** (cache hit)
   - The operation executes immediately using cached justifications

3. **Watch For:**
   - Claude should NOT show reasoning about CRS or resampling
   - The operation should complete faster than Test 1
   - Claude may mention using "cached justification" or similar

4. **Verify Success:**
   ```bash
   # Check that second output file was created
   ls -lh test/data/sample_webmercator2.tif
   
   # Verify no new justification files were created
   find .preflight/justifications -type f -name "*.json" -mmin -1
   ```

5. **Expected Output:**
   - New file: `test/data/sample_webmercator2.tif`
   - No new justification files (reused existing)

### Success Criteria
- ✅ No reflection prompts appeared
- ✅ Operation completed successfully
- ✅ Output file created
- ✅ No new justification files created (cache hit)

---

## Test 3: Different Parameters Trigger New Reflection

### Objective
Verify that changing parameters triggers new reflection prompts.

### Steps

1. **Ask Claude Desktop:**
   ```
   Use gdal-mcp-dev to reproject test/data/sample.tif to EPSG:4326 (WGS84)
   using bilinear resampling. Save as test/data/sample_wgs84.tif
   ```

2. **Expected Behavior:**
   - Different CRS (EPSG:4326 instead of 3857) triggers new CRS reflection
   - Different resampling (bilinear instead of cubic) triggers new resampling reflection
   - Claude reasons through the new choices

3. **Watch For:**
   - Claude explaining why EPSG:4326 (geographic coordinates)
   - Claude justifying bilinear over cubic
   - Different tradeoffs discussed

4. **Verify Success:**
   ```bash
   # Check output file
   ls -lh test/data/sample_wgs84.tif
   
   # Check for new justification files
   find .preflight/justifications -type f -name "*.json" -mmin -1
   ```

5. **Expected Output:**
   - New file: `test/data/sample_wgs84.tif`
   - New justification files for EPSG:4326 + bilinear combination

### Success Criteria
- ✅ New reflection prompts appeared (different parameters)
- ✅ Claude provided different reasoning than Test 1
- ✅ Output file created successfully
- ✅ New justification files stored

---

## Test 4: Inspect Stored Justifications

### Objective
Examine the structure and content of stored justifications.

### Steps

1. **List all justifications:**
   ```bash
   find .preflight/justifications -type f -name "*.json" | sort
   ```

2. **View a CRS justification:**
   ```bash
   cat .preflight/justifications/crs_datum/sha256:*.json | jq '.'
   ```

3. **View a resampling justification:**
   ```bash
   cat .preflight/justifications/resampling/sha256:*.json | jq '.'
   ```

4. **Expected Structure:**
   ```json
   {
     "intent": "What property must be preserved",
     "alternatives": [
       {
         "method": "Alternative method",
         "why_not": "Reason for rejection"
       }
     ],
     "choice": {
       "method": "Selected method",
       "rationale": "Why this method fits the intent",
       "tradeoffs": "Known limitations or compromises"
     },
     "confidence": "low|medium|high",
     "_meta": {
       "created_at": 1234567890
     }
   }
   ```

### Success Criteria
- ✅ Justifications are valid JSON
- ✅ All required fields present (intent, alternatives, choice, confidence)
- ✅ Rationale is domain-aware and specific
- ✅ Alternatives show considered options
- ✅ Metadata includes timestamp

---

## Test 5: Error Handling - Missing Justification

### Objective
Verify that operations fail gracefully if reflection prompts don't return valid justifications.

### Steps

1. **Manually test with invalid prompt response** (requires code modification):
   - Temporarily modify a prompt to return invalid JSON
   - Attempt operation
   - Verify error handling

2. **Expected Behavior:**
   - Clear error message about invalid justification
   - Operation does not proceed
   - No partial files created

### Success Criteria
- ✅ Clear error message
- ✅ No corrupted output files
- ✅ System remains stable

---

## Cleanup

After testing, clean up test outputs:

```bash
# Remove test output files
rm -f test/data/sample_webmercator*.tif
rm -f test/data/sample_wgs84.tif

# Optional: Clear justification cache
rm -rf .preflight/justifications/crs_datum/
rm -rf .preflight/justifications/resampling/
```

---

## Troubleshooting

### Issue: MCP server not found
**Solution:** Restart Claude Desktop after updating config

### Issue: No reflection prompts appearing
**Check:**
- Is the `@requires_reflection` decorator applied to the tool?
- Are prompts registered in `src/prompts/__init__.py`?
- Check server logs for errors

### Issue: Cache always hits (never re-prompts)
**Solution:** Clear cache or change parameters significantly

### Issue: Invalid justification errors
**Check:**
- Prompt response format matches `Justification` schema
- All required fields present
- Confidence value is valid ("low", "medium", "high")

---

## Expected Test Results Summary

| Test | Reflection Prompts | Cache Hit | Output File | New Justifications |
|------|--------------------|-----------|-------------|--------------------|
| 1    | ✅ Yes (2)          | ❌ No      | ✅ Yes       | ✅ Yes (2)          |
| 2    | ❌ No               | ✅ Yes     | ✅ Yes       | ❌ No               |
| 3    | ✅ Yes (2)          | ❌ No      | ✅ Yes       | ✅ Yes (2)          |

---

## Notes

- Each unique combination of parameters generates a unique hash
- Justifications are domain-specific (crs_datum, resampling, etc.)
- Cache invalidation happens automatically when parameters change
- Timestamps in `_meta` show when justification was created
- The reflection system adds ~2-5 seconds for first-time operations
- Cached operations have negligible overhead (<100ms)

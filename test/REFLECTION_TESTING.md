# Reflection System Testing Guide - v1.0.0

This guide provides step-by-step instructions for testing the re-enabled reflection preflight system with the flattened parameter architecture.

## What Changed

The reflection system has been re-integrated with the new flattened MCP parameter structure:
- **Before**: `raster_reproject(uri, output, params: Params)`
- **After**: `raster_reproject(uri, output, dst_crs, resampling, src_crs=None, ...)`

The `@requires_reflection` decorator now extracts parameters from the flattened kwargs instead of nested objects.

## Prerequisites

- Claude Desktop installed and configured
- gdal-mcp-dev server configured in MCP settings
- Test data available at `test/data/sample.tif`
- MCP server restarted to load latest code

## Test Suite

### Test 1: First-Time CRS & Resampling Reflection

**Objective**: Verify that both CRS and resampling reflection prompts are triggered on first invocation.

**Command**:
```
Use gdal-mcp-dev to reproject test/data/sample.tif to EPSG:3857 
using cubic resampling. Save as test/data/test1_webmercator.tif
```

**Expected Behavior**:
1. Claude calls `raster_info` to inspect the source
2. Claude calls `raster_reproject` with parameters
3. **Reflection Prompt 1 - CRS Selection** appears:
   - Asks about EPSG:3857 choice
   - Discusses Web Mercator properties (distance/area distortion)
   - Considers alternatives (EPSG:4326, UTM zones)
   - Provides justification for EPSG:3857
4. **Reflection Prompt 2 - Resampling Method** appears:
   - Asks about cubic resampling choice
   - Discusses interpolation quality vs performance
   - Considers alternatives (nearest, bilinear)
   - Provides justification for cubic
5. Tool executes with validated justifications
6. Output file created

**Verification**:
```bash
# Check output file
ls -lh test/data/test1_webmercator.tif

# Check justification files were created
find .preflight/justifications -type f -name "*.json" -mmin -2

# View CRS justification
find .preflight/justifications/crs_datum -type f -name "*.json" -exec cat {} \; | jq .

# View resampling justification
find .preflight/justifications/resampling -type f -name "*.json" -exec cat {} \; | jq .
```

**Success Criteria**:
- ✅ Both reflection prompts appeared
- ✅ Claude provided domain-specific reasoning
- ✅ Output file created successfully
- ✅ Two new justification JSON files in `.preflight/justifications/`

---

### Test 2: Cache Hit - Same Parameters

**Objective**: Verify that identical parameters use cached justifications (no re-prompting).

**Command**:
```
Use gdal-mcp-dev to reproject test/data/sample.tif to EPSG:3857 
using cubic resampling again. Save as test/data/test2_webmercator.tif
```

**Expected Behavior**:
1. Claude calls `raster_reproject` with same parameters
2. **NO reflection prompts appear** (cache hit)
3. Tool executes immediately using cached justifications
4. Output file created

**Verification**:
```bash
# Check output file
ls -lh test/data/test2_webmercator.tif

# Verify NO new justification files created
find .preflight/justifications -type f -name "*.json" -mmin -1
# Should return empty (no files modified in last minute)
```

**Success Criteria**:
- ✅ No reflection prompts appeared
- ✅ Operation completed faster than Test 1
- ✅ Output file created
- ✅ No new justification files (cache reused)

---

### Test 3: Partial Cache Hit - Different CRS, Same Resampling

**Objective**: Verify that changing CRS triggers new CRS prompt but reuses resampling justification.

**Command**:
```
Use gdal-mcp-dev to reproject test/data/sample.tif to EPSG:4326 
using cubic resampling. Save as test/data/test3_wgs84.tif
```

**Expected Behavior**:
1. Claude calls `raster_reproject` with new CRS
2. **Reflection Prompt - CRS Selection** appears (different CRS)
3. **NO resampling prompt** (same method, cache hit)
4. Tool executes with one new justification, one cached
5. Output file created

**Verification**:
```bash
# Check output file
ls -lh test/data/test3_wgs84.tif

# Check for new CRS justification only
find .preflight/justifications/crs_datum -type f -name "*.json" -mmin -1

# Verify no new resampling justification
find .preflight/justifications/resampling -type f -name "*.json" -mmin -1
# Should return empty
```

**Success Criteria**:
- ✅ CRS reflection prompt appeared
- ✅ No resampling prompt (cache hit)
- ✅ Output file created
- ✅ One new CRS justification file only

---

### Test 4: Partial Cache Hit - Same CRS, Different Resampling

**Objective**: Verify that changing resampling triggers new resampling prompt but reuses CRS justification.

**Command**:
```
Use gdal-mcp-dev to reproject test/data/sample.tif to EPSG:4326 
using nearest resampling. Save as test/data/test4_wgs84_nearest.tif
```

**Expected Behavior**:
1. Claude calls `raster_reproject` with new resampling method
2. **NO CRS prompt** (same CRS, cache hit)
3. **Reflection Prompt - Resampling Method** appears (different method)
4. Tool executes with one cached, one new justification
5. Output file created

**Verification**:
```bash
# Check output file
ls -lh test/data/test4_wgs84_nearest.tif

# Verify no new CRS justification
find .preflight/justifications/crs_datum -type f -name "*.json" -mmin -1
# Should return empty

# Check for new resampling justification
find .preflight/justifications/resampling -type f -name "*.json" -mmin -1
```

**Success Criteria**:
- ✅ Resampling reflection prompt appeared
- ✅ No CRS prompt (cache hit)
- ✅ Output file created
- ✅ One new resampling justification file only

---

### Test 5: Cache Miss - Both Parameters Different

**Objective**: Verify that changing both parameters triggers both prompts.

**Command**:
```
Use gdal-mcp-dev to reproject test/data/sample.tif to EPSG:32610 
(UTM Zone 10N) using bilinear resampling. Save as test/data/test5_utm.tif
```

**Expected Behavior**:
1. Claude calls `raster_reproject` with new CRS and resampling
2. **Both reflection prompts appear** (cache miss for both)
3. Claude provides justifications for UTM and bilinear
4. Tool executes with two new justifications
5. Output file created

**Verification**:
```bash
# Check output file
ls -lh test/data/test5_utm.tif

# Check for both new justifications
find .preflight/justifications -type f -name "*.json" -mmin -1
# Should show 2 files (one CRS, one resampling)
```

**Success Criteria**:
- ✅ Both reflection prompts appeared
- ✅ Claude provided UTM-specific reasoning
- ✅ Claude provided bilinear-specific reasoning
- ✅ Output file created
- ✅ Two new justification files

---

### Test 6: Relative Paths Work

**Objective**: Verify that relative paths work with reflection system.

**Command**:
```
Use gdal-mcp-dev to reproject test/data/sample.tif to EPSG:3857 
using cubic resampling. Save as test/data/test6_relative.tif
```

**Expected Behavior**:
1. Paths resolved correctly (no "relative path" errors)
2. Cache hit (same as Test 1/2 parameters)
3. No reflection prompts
4. Output file created

**Success Criteria**:
- ✅ No path resolution errors
- ✅ Cache hit (no prompts)
- ✅ Output file created

---

### Test 7: Lowercase Compression Works

**Objective**: Verify that lowercase compression values work with convert tool.

**Command**:
```
Use gdal-mcp-dev to convert test/data/sample.tif with deflate compression 
and overviews [2, 4]. Save as test/data/test7_compressed.tif
```

**Expected Behavior**:
1. Tool accepts lowercase "deflate" (not "DEFLATE")
2. Conversion completes successfully
3. File compressed and overviews built

**Verification**:
```bash
# Check output file (should be much smaller)
ls -lh test/data/test7_compressed.tif

# Verify compression and overviews
gdal-mcp-dev raster_info test/data/test7_compressed.tif
```

**Success Criteria**:
- ✅ No validation errors for lowercase compression
- ✅ File size significantly reduced
- ✅ Overviews present in metadata

---

## Troubleshooting

### No Reflection Prompts Appearing

**Possible Causes**:
1. MCP server not restarted - restart Claude Desktop
2. Cache hit from previous test - use different parameters
3. Decorator not applied - check `src/tools/raster/reproject.py`

**Debug**:
```bash
# Check if decorator is present
grep -A 5 "@requires_reflection" src/tools/raster/reproject.py

# Clear cache to force prompts
rm -rf .preflight/justifications/*
```

### "Relative Path" Errors

**Possible Causes**:
1. MCP server not restarted with new code
2. Path resolution not applied to tool

**Debug**:
```bash
# Check if resolve_path is imported
grep "resolve_path" src/tools/raster/*.py
```

### Uppercase Compression Required

**Possible Causes**:
1. MCP server not restarted
2. Still using enum instead of Literal

**Debug**:
```bash
# Check compression type
grep "CompressionMethod" src/models/raster/convert.py
```

---

## Expected Justification Structure

Justification files are stored as JSON in `.preflight/justifications/{domain}/sha256:{hash}.json`

**CRS Justification Example**:
```json
{
  "domain": "crs_datum",
  "timestamp": "2024-10-24T15:30:00Z",
  "justification": {
    "chosen_crs": "EPSG:3857",
    "reasoning": "Web Mercator is appropriate for web mapping applications...",
    "alternatives_considered": ["EPSG:4326", "EPSG:32610"],
    "tradeoffs": "Distance and area distortion at high latitudes..."
  }
}
```

**Resampling Justification Example**:
```json
{
  "domain": "resampling",
  "timestamp": "2024-10-24T15:30:00Z",
  "justification": {
    "chosen_method": "cubic",
    "reasoning": "Cubic convolution provides smooth interpolation for continuous data...",
    "alternatives_considered": ["nearest", "bilinear"],
    "tradeoffs": "Higher computational cost but better visual quality..."
  }
}
```

---

## Summary Checklist

After completing all tests, verify:

- [ ] Test 1: Both prompts triggered on first use
- [ ] Test 2: Cache hit with identical parameters
- [ ] Test 3: Partial cache (CRS changed)
- [ ] Test 4: Partial cache (resampling changed)
- [ ] Test 5: Both prompts with both changed
- [ ] Test 6: Relative paths work
- [ ] Test 7: Lowercase compression works
- [ ] Justification files created in `.preflight/justifications/`
- [ ] Cache behavior correct (no unnecessary re-prompting)
- [ ] All output files created successfully

## Success Criteria for v1.0.0

✅ **Reflection system fully operational**
✅ **Cache system working correctly**
✅ **Flattened parameters integrated**
✅ **Path resolution working**
✅ **Compression case-insensitivity working**

**Ready for v1.0.0 release!** 🎉

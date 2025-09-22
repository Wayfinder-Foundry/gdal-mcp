---
type: usage
title: GDAL MCP Usage Guide
tags: [usage, docs]
---

# GDAL MCP Server Usage Guide

This guide demonstrates how to use the GDAL MCP Server to expose GDAL operations as tools for AI agents.

## Overview

The GDAL MCP Server provides the following tools (initial set):
- `info` - Get information about raster datasets (GDAL `gdal info`)
- `convert` - Convert raster data between formats (GDAL `gdal convert`)
- `reproject` - Reproject raster images (GDAL `gdal raster reproject`)  

## Running the Server

Start the MCP server using stdio transport:

```bash
uv run gdal-mcp serve --transport stdio
```

Or using HTTP transport:

```bash
uv run gdal-mcp serve --transport http --port 8000
```

## MCP Protocol Communication

The server follows the Model Context Protocol (MCP) specification using JSON-RPC 2.0.

### 1. Initialize the Connection

```json
{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}, "id": 1}
```

Response:
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"GDAL Tools","version":"1.14.0"}}}
```

### 2. Send Initialization Complete Notification

```json
{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
```

### 3. List Available Tools

```json
{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}
```

Response includes all available tools with their schemas:
```json
{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"gdalinfo","description":"Get information about a raster dataset...","inputSchema":{...},"outputSchema":{...}}, ...]}}
```

### 4. Call Tools

#### Example: Get Raster Information

```json
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "gdalinfo", "arguments": {"dataset": "test_data/sample.tif", "json_output": false, "stats": false}}, "id": 3}
```

#### Example: Convert Raster Format

```json
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "gdal_translate", "arguments": {"src_dataset": "test_data/sample.tif", "dst_dataset": "test_data/converted.tif", "output_format": "GTiff", "bands": [1, 2]}}, "id": 4}
```

#### Example: Reproject Raster

```json
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "gdalwarp", "arguments": {"src_datasets": ["test_data/sample.tif"], "dst_dataset": "test_data/reprojected.tif", "target_epsg": 3857, "resampling": "bilinear"}}, "id": 5}
```

## Tool Schemas

### gdalinfo

**Input Schema:**
- `dataset` (string, required): Path to the raster dataset file
- `json_output` (boolean, default: false): Return output in JSON format
- `stats` (boolean, default: false): Compute and include raster band statistics

**Output:** String containing the gdalinfo output or error message

### gdal_translate

**Input Schema:**
- `src_dataset` (string, required): Path to source raster dataset
- `dst_dataset` (string, default: ""): Path to output dataset (auto-generated if empty)
- `output_format` (string, default: "GTiff"): GDAL output format
- `bands` (array of integers): List of band numbers to copy (1-based indexing)
- `scale_min` (number): Minimum value for scaling
- `scale_max` (number): Maximum value for scaling  
- `output_type` (string): Output data type (Byte, UInt16, Int16, UInt32, Int32, Float32, Float64)

**Output:** String containing the result path or error message

### gdalwarp

**Input Schema:**
- `src_datasets` (array of strings, required): List of source raster dataset paths
- `dst_dataset` (string, default: ""): Path to output dataset (auto-generated if empty)
- `target_epsg` (integer, default: 4326): Target EPSG code for spatial reference system
- `resampling` (string, default: "near"): Resampling algorithm (near, bilinear, cubic, etc.)
- `output_format` (string, default: "GTiff"): GDAL output format
- `overwrite` (boolean, default: false): Overwrite existing output file

**Output:** String containing the result path or error message

### gdalbuildvrt

**Input Schema:**
- `src_datasets` (array of strings, required): List of source raster dataset paths
- `dst_vrt` (string, default: ""): Path to output VRT file (auto-generated if empty)
- `resolution` (string, default: "average"): Output resolution (highest, lowest, average)
- `separate` (boolean, default: false): Place each input file into separate VRT bands

**Output:** String containing the result path or error message

## Testing Tools Directly

You can test the tools directly using Python:

```python
# Run the test suite
python test_gdal_mcp.py

# Run the interactive demo
python demo_gdal_mcp.py
```

## Common Use Cases

1. **Raster Information**: Use `gdalinfo` to inspect raster metadata, coordinate systems, and band information
2. **Format Conversion**: Use `gdal_translate` to convert between different raster formats (GeoTIFF, JPEG, PNG, etc.)
3. **Reprojection**: Use `gdalwarp` to change coordinate reference systems
4. **Band Selection**: Use `gdal_translate` with the `bands` parameter to extract specific bands
5. **Virtual Mosaics**: Use `gdalbuildvrt` to create lightweight virtual datasets from multiple inputs

## Error Handling

All tools include comprehensive error handling:
- File path validation
- Command execution timeouts (30-180 seconds depending on tool)
- GDAL command availability checks
- Input parameter validation

Error responses are returned as strings starting with "Error:" followed by the error description.

## Security Considerations

- All file paths are validated before use
- Commands are executed with timeouts to prevent runaway processes
- Input parameters are sanitized to prevent command injection
- Only specified GDAL operations are exposed

## Requirements

- GDAL installed and available in PATH
- Python 3.10+
- MCP Python SDK (mcp[cli] package)
- uv package manager (recommended)

## Example Session

Here's a complete example of using the MCP server:

```bash
# Start the server
uv run python -m server gdal_tools stdio

# Send initialization
{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "example", "version": "1.0"}}, "id": 1}

# Send initialized notification
{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}

# Get info about a raster
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "gdalinfo", "arguments": {"dataset": "my_raster.tif"}}, "id": 2}

# Convert to JPEG
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "gdal_translate", "arguments": {"src_dataset": "my_raster.tif", "dst_dataset": "preview.jpg", "output_format": "JPEG"}}, "id": 3}
```

Here's how to call a tool using `curl` with an MCP server running on localhost:

```bash
curl -X POST http://localhost:8000/tools/call -H "Content-Type: application/json" -d '{"name": "gdalinfo", "arguments": {"dataset": "test_data/sample.tif"}}'
```

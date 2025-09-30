# Decision Log

---
## Decision
*   [2025-09-27 20:29:34] ADR-0002: Transport strategy (stdio first, optional HTTP)

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

---
## Decision
*   [2025-09-27 20:29:34] ADR-0003: Distribution via uvx and Docker

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

---
## Decision
*   [2025-09-27 20:29:34] ADR-0001: FastMCP foundation for GDAL MCP (Python)

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

---
## Decision
*   [2025-09-27 20:29:34] ADR-0002: Transport strategy (stdio first, optional HTTP)

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

---
## Decision
*   [2025-09-27 20:29:34] ADR-0003: Distribution via uvx and Docker

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

---
## Decision
*   [2025-09-27 20:29:34] ADR-0003: Distribution via uvx and Docker

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

---
## Decision
*   [2025-09-27 20:29:34] ADR-0002: Transport strategy (stdio first, optional HTTP)

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

---
## Decision
*   [2025-09-27 20:29:34] ADR-0001: FastMCP foundation for GDAL MCP (Python)

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

---
## Decision
*   [2025-09-27 20:29:30] ADR-0001: FastMCP foundation for GDAL MCP (Python)

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

---
## Decision
*   [2025-09-27 20:19:26] ADR-0008: Error handling and safety annotations

## Rationale
*   User-facing errors must be safe and informative while FastMCP masks unexpected exceptions by default.

## Implementation Details
*   Initialize FastMCP with mask_error_details=True, raise ToolError with human-readable messages for expected failures, and use tool annotations (readOnlyHint, destructiveHint, idempotentHint) to communicate risk.

---
## Decision
*   [2025-09-27 19:09:16] ADR-0007: Structured outputs with generated schemas

## Rationale
*   FastMCP can generate JSON Schemas from type hints, giving clients strong contracts and better UI validation.

## Implementation Details
*   Return Pydantic/dataclass models from tools, include auxiliary human-readable summaries when helpful, and reserve primitive returns for exceptional cases.

---
## Decision
*   [2025-09-27 19:08:45] ADR-0006: Transport & deployment strategy

## Rationale
*   Local developers prefer stdio + uvx for quick iteration, but some users need remote deployments without native GDAL setup.

## Implementation Details
*   Default to stdio transport for local use; provide HTTP transport for containerized deployments. Document configuration differences and support both startup modes.

---
## Decision
*   [2025-09-27 19:08:31] ADR-0005: MVP scope for Python-native GDAL MCP

## Rationale
*   Focus initial release on high-value raster workflows and minimal vector support so we can ship quickly while validating the new Python-native stack.

## Implementation Details
*   Implement raster_info, reproject_raster, convert_raster, and build_vrt using Rasterio/PyProj; provide vector_info and reproject_vector as the only initial vector tools; defer window stats, thumbnails, and clipping until after MVP.

---
## Decision
*   [2025-09-27 19:06:44] ADR-0004: Adopt FastMCP with a Python-native GDAL stack

## Rationale
*   Wrapping the `gdal` CLI complicates structured outputs, progress, and safety, while Python-native libraries (rasterio, pyogrio/fiona, pyproj) integrate smoothly with FastMCP type hints and async controls.

## Implementation Details
*   Implement Raster tools with rasterio+pyproj, vector tools with pyogrio/fiona, and keep osgeo.gdal/ogr only as targeted fallbacks when functionality is missing.

---
## Decision
*   [2025-09-18 01:51:09] ADR-0001: FastMCP foundation for GDAL MCP (Python)

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

---
## Decision
*   [2025-09-18 01:51:09] ADR-0002: Transport strategy (stdio first, optional HTTP)

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

---
## Decision
*   [2025-09-18 01:51:09] ADR-0003: Distribution via uvx and Docker

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

---
## Decision
*   [2025-09-18 01:07:35] ADR-0001: FastMCP foundation for GDAL MCP (Python)

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

---
## Decision
*   [2025-09-18 01:07:35] ADR-0002: Transport strategy (stdio first, optional HTTP)

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

---
## Decision
*   [2025-09-18 01:07:35] ADR-0003: Distribution via uvx and Docker

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

---
## Decision
*   [2025-09-18 00:56:00] ADR-0003: Distribution via uvx and Docker

## Rationale
*   One-line local run and reproducible container with GDAL runtime.

## Implementation Details
*   pyproject with console script gdal-mcp; Dockerfile based on GDAL image; healthcheck; multi-arch.

---
## Decision
*   [2025-09-18 00:56:00] ADR-0002: Transport strategy (stdio first, optional HTTP)

## Rationale
*   Stdio is simplest and lowest latency for local hosts; add HTTP later with MCP-Protocol-Version header.

## Implementation Details
*   Serve stdio by default via gdal-mcp; enable http with --transport http; document headers.

---
## Decision
*   [2025-09-18 00:55:56] ADR-0001: FastMCP foundation for GDAL MCP (Python)

## Rationale
*   Use Python FastMCP for rapid, compliant MCP server with GDAL bindings; stdio default, optional HTTP.

## Implementation Details
*   Server implemented with fastmcp>=2; tools registered via @mcp.tool; logs go to stderr.

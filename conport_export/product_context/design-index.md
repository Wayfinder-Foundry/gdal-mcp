---
type: product_context
title: Design Index
tags: [design, docs, product_context]
---

# GDAL MCP Design Documents

- [Overview](overview.md) outlines the motivation for wrapping GDAL with the Model Context Protocol, highlights our reliance on the **fastMCP** framework, and summarises the project goals.
- [Architecture](architecture.md) dives into the fastMCP-based server composition, data flow, and security posture.
- [Tool Specifications](tools.md) documents tool signatures and behaviour for each GDAL CLI command exposed by the server.
- [Distribution Strategy](distribution.md) details how we will ship the project via `uvx` as well as Docker, including release automation and repository layout guidance.

These documents replace the monolithic draft and will evolve alongside the implementation.

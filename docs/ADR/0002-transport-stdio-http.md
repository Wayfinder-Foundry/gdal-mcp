---
type: decision
id: ADR-0002
title: Transport strategy (stdio first, optional HTTP)
tags: [adr, transport, stdio, http, mcp]
status: accepted
 date: 2025-09-17
---

# ADR-0002: Transport strategy (stdio first, optional HTTP)

## Context

MCP supports stdio (local) and HTTP (remote). Stdio is simpler and fastest for local hosts; HTTP adds network and streaming concerns.

## Decision

- Use stdio transport by default during Phase 1.
- Keep HTTP support as an optional mode with the correct `MCP-Protocol-Version` header and streaming-friendly responses.

## Consequences

- Pros: Lower complexity initially; best latency for local workflows.
- Cons: Remote hosting deferred; additional testing needed when HTTP is introduced.

## Status

Accepted for Phase 1.

## Links

- `docs/mcp-guidelines.md`
- `docs/MCP-COMPLIANCE.md`

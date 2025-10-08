---
type: product_context
title: MCP Compliance Checklist
tags: [mcp, compliance, checklist]
---

# MCP Compliance Checklist

Source of truth: `docs/mcp-guidelines.md`. This checklist is used to gate releases and PRs.

## Status

- Owner: GDAL MCP team
- Phase: Foundation
- Last updated: 2025-09-17

## Requirements

- [ ] Initialization and version negotiation
  - Date-based protocol versions (YYYY-MM-DD)
  - During init, only `initialize`/logs/pings allowed; send `notifications/initialized` when ready
  - For HTTP transport, set `MCP-Protocol-Version` header on every request
- [ ] Capabilities
  - Declare only capabilities actually implemented
  - If sending change notifications, set `listChanged: true`
  - Respect client features (elicitation, sampling) only if negotiated
- [ ] Tools (server primitives)
  - Unique names, clear descriptions, JSON Schema input (and output when helpful)
  - Idempotent and safe; expect host to require user approval before execution
  - Friendly validation errors on bad input; avoid side effects without consent
- [ ] Resources (optional)
  - Provide MIME types and URIs; support templates where useful
  - Implement `resources/list`/`read` (and `subscribe` if declared)
- [ ] Prompts (optional)
  - List via `prompts/list`; define structured parameters; retrieved via `prompts/get`
  - User-initiated only; not auto-invoked by model
- [ ] Notifications
  - Use `notifications/tools/list_changed` when tools change
  - Never include `id` in notifications
  - Only send notifications if capability declared
- [ ] Transport
  - Default stdio; optional HTTP (streaming-friendly)
  - Never write logs to stdout; all logs to stderr
- [ ] Logging & Observability
  - Structured logs to stderr with levels and trace/job IDs
  - Mask secrets; no PII in logs by default
- [ ] Security & Consent
  - Rely on host-provided credentials; do not request raw secrets
  - Follow least-privilege; validate file roots via `roots/list` if used
- [ ] QA
  - Validate with MCP Inspector and at least one host (e.g., Claude Desktop)
  - Include compliance notes in release checklist

## Notes

- See `docs/ADR/0002-transport-stdio-http.md` for transport choices.
- See `docs/ADR/0003-distribution-uvx-docker.md` for packaging and distribution constraints.

# ADR-0011-resource-strategy-and-binary-io.md

## Title

Resource strategy (vsimem vs filesystem) & binary payloads

## Status

Proposed

## Context

Outputs can be large; MCP supports embedded resources and URIs.

## Decision

* For **small** outputs (e.g., tiny VRT XML, thumbnails): return **EmbeddedResource**.
* For **large** outputs: write to filesystem (or `/vsimem` if ephemeral), return a **URI** + metadata (size, checksum, driver).
* Provide **resource templates** for common schemes (e.g., `file://`, `s3://` via VSI).

## Consequences

* Pro: Efficient transfers; workable for big geodata; good UX.
* Con: Requires temp file hygiene and cleanup on cancellation.


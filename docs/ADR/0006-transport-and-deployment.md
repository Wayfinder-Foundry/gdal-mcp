# ADR-0006-transport-and-deployment.md

## Title

Transport & deployment strategy

## Status

Proposed

## Context

Local developer UX prefers `stdio` + `uvx`, but native deps can be heavy for end users.

## Decision

* **Primary**: `stdio` transport for local dev and power users (run via `uvx`).
* **Optional**: HTTP transport for **remote, containerized** serving (Docker image with GDAL stack), used when native deps on client are a barrier.

## Consequences

* Pro: Great local DX, scalable remote option without per-user native setup.
* Con: Two paths to maintain (startup/config differences).

# ADR-0009-concurrency-and-memory-model.md

## Title

Concurrency, memory, and dataset lifecycle

## Status

Proposed

## Context

GDAL isn’t fully thread-safe; rasters can be large.

## Decision

* Use **windowed IO** and VRT composition to avoid large in-memory arrays.
* Prefer **`anyio.to_thread` / process pools** for CPU-heavy work; avoid blocking the event loop.
* **Always** close datasets promptly; encapsulate IO in context managers.

## Consequences

* Pro: Stable under load; bounded memory; responsive server.
* Con: Slight complexity managing pools and lifecycle.

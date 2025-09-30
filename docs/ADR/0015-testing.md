# ADR-0015-testing-strategy.md

## Title

Testing and fixtures

## Status

Proposed

## Context

We need repeatable tests for geodata.

## Decision

* Unit tests at the function level with tiny fixtures (small GeoTIFF/GeoPackage).
* Integration tests that run full tool calls and verify structured outputs, resources, and logs.
* Golden files for VRT outputs; checksum verification for conversions.

## Consequences

* Pro: Confidence during refactors; prevents regressions.
* Con: Slight repo weight (fixtures), mitigated by tiny synthetic datasets.

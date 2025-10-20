---
task_id: "1008"
title: "Develop compression strategy prompt"
status: "todo"
priority: "medium"
owner: "unassigned"
created: "2025-10-17"
updated: "2025-10-17"
tags:
  - prompts
  - parameters
depends_on:
  - "1004"
---

## Summary
Add `select_compression_strategy()` to `src/prompts/parameters.py` guiding agents on compression algorithm selection based on data type, size constraints, and performance needs.

## Rationale
Compression impacts storage and delivery. Prompt guidance codifies trade-offs, aligning with ADR-0023 reference resources and ensuring `raster_convert` usage is intentional.

## Deliverables
- **[prompt]** Compression decision prompt with lossless vs lossy guidance.
- **[tests]** Assertions covering algorithm mentions (lzw, deflate, zstd, jpeg) and context.
- **[docs]** Documentation entry detailing compression recommendations.

## Acceptance Criteria
- **[tradeoffs]** Prompt discusses data fidelity vs size/performance.
- **[references]** Mentions `reference://compression/available` and `reference://compression/guide`.
- **[validation]** Encourages verifying output size/quality post-conversion.
- **[tests-pass]** Prompt suite extended and passing.

## Notes
- Coordinate with 1004 to maintain consistent terminology around conversion options.
- Follow compression trade-off guidance defined in `docs/design/epistemology/IMPLEMENTATION_PLAN.md` for aggregation-related justifications.

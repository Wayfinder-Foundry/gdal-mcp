---
description: Ingest docs into ConPort (generate conport_export/ and import)
---

# Ingest docs into ConPort

This workflow parses markdown in `docs/`, emits per-item markdown to `conport_export/`, and imports them into ConPort.

## Prereqs
- Docs contain YAML frontmatter with:
  - `type`: product_context | decision | system_pattern | glossary | usage
  - `title`, optional `id`, `tags`, optional `links`

## Steps
1) Validate frontmatter presence (README, MCP/fastMCP guidelines, design/*, ADRs)

// turbo
2) Generate export artifacts
   Command:
   - `uv run gdal-mcp-ingest --verbose`

3) Import into ConPort
   - Use the ConPort import tool to load from `./conport_export/`.
   - The import is idempotent; it will upsert items by id/title and content hash.

## Notes
- Artifacts layout: `conport_export/<type>/<slug>.md` + `conport_export/index.jsonl`
- Tags include `docs_source:<relpath>` (coming in future enhancement)

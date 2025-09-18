---
description: Ingest Pass 1 SpecSummaries for LAS 1.4 and COPC into ConPort Custom Data.
---

```yaml
name: ingest_pass1
description: |
  Upsert the initial set of SpecSummaries (LAS 1.4 + COPC) into ConPort Custom Data.
  - Preserves focus by default
  - Can run in dry-run mode first for preview

inputs:
  pre_opts:  { type: object, required: false, default: {} }
  post_opts:
    type: object
    required: false
    default: { capture_git_snapshot: true, log_run_record: true, export_on_change: true, preserve_focus: true }
  dry_run:   { type: boolean, required: false, default: false }

steps:
  # ---------- PRE HOOK ----------
  - id: preflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/pre.md
    with: "{{ inputs.pre_opts }}"

  # ---------- Upserts (LAS 1.4) ----------
  - id: upsert_las_header
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/custom_data_upsert.md
    with:
      category: "SpecSummaries"
      key: "las1.4.header"
      value:
        summary: "The Public Header Block is a fixed 375-byte structure defining file identity, metadata, data organization, CRS parameters, and LAS 1.4 extensions such as 64-bit point counts and up to 15 returns. It encodes offsets, counts, scale/offset, bounds, waveform/EVLR pointers, and must be consistent with actual data. Legacy compatibility fields are zeroed when not needed; modern counts use 64-bit fields."
        spec: "las1.4"
        section: "header"
        role: "summary"
        source: "docs/specs/las1.4/header.md"
      tags: ["workflow:ingestion","specs:las1.4","role:summary"]
      source_path: "docs/specs/las1.4/header.md"
      merge_strategy: "replace"
      dry_run: "{{ inputs.dry_run }}"

  - id: upsert_las_types
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/custom_data_upsert.md
    with:
      category: "SpecSummaries"
      key: "las1.4.types"
      value:
        summary: "LAS uses standard C99/IEEE data types in little-endian encoding. Primitive integers, floating point types, and fixed-length character arrays have precise sizes; fixed-length strings may lack null-termination and must be handled carefully to avoid overruns. Implementation notes emphasize strict spec compliance and safe string handling."
        spec: "las1.4"
        section: "types"
        role: "summary"
        source: "docs/specs/las1.4/types.md"
      tags: ["workflow:ingestion","specs:las1.4","role:summary"]
      source_path: "docs/specs/las1.4/types.md"
      merge_strategy: "replace"
      dry_run: "{{ inputs.dry_run }}"

  - id: upsert_las_profiles
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/custom_data_upsert.md
    with:
      category: "SpecSummaries"
      key: "las1.4.profiles"
      value:
        summary: "Domain Profiles extend LAS for specialized communities without breaking compatibility. Extensions may add classifications (≥39) and attributes via Extra Bytes VLRs, with stringent documentation and coordination to prevent conflicts. Profiles follow a structured approval process and emphasize interoperability and documentation quality."
        spec: "las1.4"
        section: "profiles"
        role: "summary"
        source: "docs/specs/las1.4/profiles.md"
      tags: ["workflow:ingestion","specs:las1.4","role:summary"]
      source_path: "docs/specs/las1.4/profiles.md"
      merge_strategy: "replace"
      dry_run: "{{ inputs.dry_run }}"

  - id: upsert_las_crs
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/custom_data_upsert.md
    with:
      category: "SpecSummaries"
      key: "las1.4.crs"
      value:
        summary: "LAS 1.4 introduces WKT as the preferred CRS (via (E)VLR) while maintaining GeoTIFF for legacy formats. Point types 6–10 require WKT; types 0–5 use GeoTIFF when in legacy mode. Exactly one CRS representation must exist; updates are done by appending a superseding EVLR to avoid full rewrites."
        spec: "las1.4"
        section: "crs"
        role: "summary"
        source: "docs/specs/las1.4/crs.md"
      tags: ["workflow:ingestion","specs:las1.4","role:summary"]
      source_path: "docs/specs/las1.4/crs.md"
      merge_strategy: "replace"
      dry_run: "{{ inputs.dry_run }}"

  # ---------- Upserts (COPC) ----------
  - id: upsert_copc_requirements
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/custom_data_upsert.md
    with:
      category: "SpecSummaries"
      key: "copc.requirements"
      value:
        summary: "COPC requires LAS PDRF 6/7/8, a COPC info VLR (first VLR at byte 375), and a COPC hierarchy VLR to encode the octree index. Data is LAZ 1.4 compressed and organized by octree nodes for direct random access via byte ranges. All structures are little-endian, reserved fields must be zero, and alignment is on byte boundaries."
        spec: "copc"
        section: "requirements"
        role: "summary"
        source: "docs/specs/copc/requirements.md"
      tags: ["workflow:ingestion","specs:copc","role:summary"]
      source_path: "docs/specs/copc/requirements.md"
      merge_strategy: "replace"
      dry_run: "{{ inputs.dry_run }}"

  - id: upsert_copc_implementation
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/custom_data_upsert.md
    with:
      category: "SpecSummaries"
      key: "copc.implementation"
      value:
        summary: "Implementation guidance covers file validation (header checks, VLR order, version), PDRF detection from the LAS header, and traversal of hierarchy pages pointed to by CopcInfo. Octree navigation distinguishes index entries (pointCount = -1) from leaf/data entries (pointCount > 0) and leverages direct offsets for streaming."
        spec: "copc"
        section: "implementation"
        role: "summary"
        source: "docs/specs/copc/implementation.md"
      tags: ["workflow:ingestion","specs:copc","role:summary"]
      source_path: "docs/specs/copc/implementation.md"
      merge_strategy: "replace"
      dry_run: "{{ inputs.dry_run }}"

  - id: upsert_copc_ept
    action: Read the contents of the file.
    file: .windsurf/workflows/atoms/conport/custom_data_upsert.md
    with:
      category: "SpecSummaries"
      key: "copc.ept"
      value:
        summary: "COPC aligns with EPT at the spatial index level (octree scheme) but stores all data in a single LAZ file, enabling HTTP range requests with reduced metadata overhead. It supports clustered storage and progressive loading while avoiding millions of small files typical of EPT."
        spec: "copc"
        section: "ept"
        role: "summary"
        source: "docs/specs/copc/ept.md"
      tags: ["workflow:ingestion","specs:copc","role:summary"]
      source_path: "docs/specs/copc/ept.md"
      merge_strategy: "replace"
      dry_run: "{{ inputs.dry_run }}"

  # ---------- POST ----------
  - id: progress_payload
    action: system
    output_transform:
      progress:
        - description: >-
            Ingested SpecSummaries Pass 1 (LAS header/types/profiles/crs; COPC requirements/implementation/ept)
            {{ inputs.dry_run and '(dry-run)' or '' }}
          status: "{{ inputs.dry_run and 'IN_PROGRESS' or 'DONE' }}"

  - id: postflight
    action: Read the contents of the file.
    file: .windsurf/workflows/hooks/post.md
    with:
      decisions: []
      progress: "{{ steps.progress_payload.progress }}"
      dry_run: "{{ inputs.dry_run }}"
      {% raw %}{% if inputs.post_opts and inputs.post_opts.preserve_focus %}{% endraw %}
      active_patch:
        requested_scope: "SpecSummaries.Pass1"
        workflow: "ingest_pass1"
        last_run: "{{ now_iso() }}"
      {% raw %}{% else %}{% endraw %}
      active_patch:
        current_focus: "ConPort ingestion"
        requested_scope: "SpecSummaries.Pass1"
        workflow: "ingest_pass1"
        last_run: "{{ now_iso() }}"
      {% raw %}{% endif %}{% endraw %}
      {{ inputs.post_opts | tojson }}

outputs:
  success:
    status: ok
    message: >-
      SpecSummaries Pass 1 ingestion complete (dry_run={{ inputs.dry_run }}).
```

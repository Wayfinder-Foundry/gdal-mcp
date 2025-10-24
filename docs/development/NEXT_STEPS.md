# Development Plan: Post-Refactoring Next Steps

**Generated**: 2025-10-23  
**Context**: Following major refactoring to eliminate "epistemic" terminology and replace heuristic classification with deterministic per-tool reflection decorators.

---

## Current State

### ✅ Completed
- Renamed all "epistemic" references to "reflection"/"preflight"
- Simplified JSON schema from 8 nested fields → 4 flat fields
- Replaced keyword-based risk classification with `@requires_reflection` decorator
- Updated all 4 prompts (CRS, resampling, hydrology, aggregation) to minimal JSON
- Migrated `raster_reproject` to use new decorator
- All 67 tests passing

### ⚠️ Unstaged Changes
- `src/prompts/` entire directory (NEW)
- `src/middleware/preflight.py` (NEW)
- `src/middleware/reflection_store.py` (NEW)
- `src/tools/reflect/` directory (NEW)
- Multiple test files (NEW)
- Modified: `src/middleware/__init__.py`, `src/server.py`, `src/tools/raster/reproject.py`

### 🔴 Known Issues
1. Multi-risk operations: `raster_reproject` only blocks on CRS, not resampling
2. Old `src/tools/epistemic/` directory still exists (should be deleted)
3. Methodology docs still reference non-existent `resource://epistemology/*` URIs
4. No integration tests for end-to-end reflection workflow
5. Legacy `src/prompts/risk.py` should be deprecated

---

## Phase 1: Consolidation & Cleanup
**Priority**: Critical  
**Estimated Time**: 1-2 hours  
**Owner**: Next developer session

### Tasks

#### 1.1 Git Operations
```bash
# Stage all new reflection infrastructure
git add src/prompts/
git add src/middleware/preflight.py
git add src/middleware/reflection_store.py
git add src/tools/reflect/
git add test/test_epistemology_schema.py
git add test/test_epistemology_store.py
git add test/test_risk.py

# Stage modifications
git add src/middleware/__init__.py
git add src/server.py
git add src/tools/raster/reproject.py
git add test/conftest.py

# Commit the refactoring
git commit -m "refactor: eliminate 'epistemic' terminology, simplify reflection schema

- Rename middleware: epistemic → preflight, epistemic_store → reflection_store
- Rename tools: epistemic → reflect
- Simplify Justification schema: 8 nested fields → 4 flat fields (intent, alternatives, choice, confidence)
- Replace keyword-based classification with @requires_reflection decorator
- Update all prompts to minimal JSON template (~15 lines each)
- Update raster_reproject to use deterministic per-tool reflection
- Cache directory: .epistemic/ → .preflight/

All 67 tests passing. Breaking changes require model adaptation to new JSON schema."
```

#### 1.2 Delete Legacy Code
```bash
# Remove old epistemic directory (replaced by reflect/)
rm -rf src/tools/epistemic/

# Remove legacy prompt test suite (outdated)
# Already deleted: test/prompt_suite/test_prompts.py
```

#### 1.3 Update .gitignore
Add/modify entries:
```
# Reflection cache
.preflight/

# Agent/context directories
.agents/
context_portal/

# Test data fixtures
test/data/
```

#### 1.4 Smoke Test
```bash
# Verify imports still work
uv run python -c "from src.middleware import requires_reflection; print('✓')"
uv run python -c "from src.tools.reflect.persist import persist_justification; print('✓')"

# Run full test suite
uv run pytest -v
```

**Acceptance Criteria**:
- All changes committed
- No legacy epistemic/ references in codebase
- Tests pass
- .gitignore updated

---

## Phase 2: Multi-Risk Reflection
**Priority**: High (User-requested feature)  
**Estimated Time**: 4-6 hours  
**Dependencies**: Phase 1 complete

### Problem Statement
`raster_reproject` performs two consequential operations:
1. CRS transformation (currently requires reflection)
2. Resampling (currently no reflection required)

User feedback: "Reprojection nearly always resamples—either chain two reflections or keep a single reflection with two sections."

**Recommended approach**: Chain two decorators (cleaner separation of concerns).

### Tasks

#### 2.1 Enhance Decorator to Support Stacking
**File**: `src/middleware/preflight.py`

Current limitation: Single decorator checks one domain. Need to support multiple decorators on same function.

Approach:
```python
# Option A: Each decorator is independent (simpler)
@requires_reflection("justify_resampling_method", "resampling", ...)
@requires_reflection("justify_crs_selection", "crs_datum", ...)
@mcp.tool()
async def raster_reproject(...): ...
# Each wrapper checks its own cache independently

# Option B: Collect all requirements, check all at once (more complex)
# Would require decorator to accumulate metadata and check all domains
```

**Recommended**: Option A (simpler, each decorator is stateless).

Modification needed:
- Current implementation already supports this (decorators compose naturally in Python)
- Test to ensure order doesn't matter (should check innermost decorator first)

#### 2.2 Apply Dual Reflection to raster_reproject
**File**: `src/tools/raster/reproject.py`

Update decorator:
```python
@requires_reflection(
    prompt_name="justify_resampling_method",
    domain="resampling",
    args_fn=lambda args: {
        "data_type": "raster",
        "source_resolution": "original",  # Could extract from src metadata
        "target_resolution": "resampled",  # Could extract from params
        "method": args.get("params").resampling if args.get("params") else "unknown",
        "operation_context": "reprojection resampling",
    }
)
@requires_reflection(
    prompt_name="justify_crs_selection",
    domain="crs_datum",
    args_fn=lambda args: {
        "source_crs": args.get("params").src_crs if args.get("params") and hasattr(args.get("params"), "src_crs") else "source CRS",
        "target_crs": args.get("params").dst_crs if args.get("params") and hasattr(args.get("params"), "dst_crs") else "unknown",
        "operation_context": "raster reprojection",
        "data_type": "raster",
    }
)
@mcp.tool(name="raster_reproject", ...)
async def reproject(...): ...
```

**Edge cases to handle**:
- If only one justification cached, emit hint for the missing one
- Hashes must be deterministic and stable across decorator order
- Error message should list all missing reflections

#### 2.3 Add Integration Test
**File**: `test/test_reflection_workflow_multi_risk.py` (NEW)

```python
import pytest
from src.tools.raster.reproject import reproject
from src.tools.reflect.persist import persist_justification
from src.prompts.crs import justify_crs_selection
from src.prompts.resampling import justify_resampling_method

async def test_multi_risk_requires_both_reflections(test_raster, tmp_path):
    """Verify raster_reproject requires both CRS and resampling reflections."""
    
    # Attempt reprojection without any reflections
    with pytest.raises(ToolError) as exc:
        await reproject(
            uri=str(test_raster),
            output=str(tmp_path / "output.tif"),
            params={"dst_crs": "EPSG:32610", "resampling": "bilinear"}
        )
    
    # Extract hint for first missing reflection
    hint = exc.value.data["hint"]
    assert hint["prompt"] in ["justify_crs_selection", "justify_resampling_method"]
    
    # Persist first reflection
    await persist_justification(
        hash_key=hint["hash"],
        domain=hint["domain"],
        justification={
            "intent": "Preserve distance for flow calculations",
            "alternatives": [{"method": "EPSG:3310", "why_not": "Area-focused"}],
            "choice": {"method": "EPSG:32610", "rationale": "UTM zone", "tradeoffs": "Zone boundary"},
            "confidence": "medium"
        }
    )
    
    # Retry - should now require second reflection
    with pytest.raises(ToolError) as exc2:
        await reproject(...)
    
    hint2 = exc2.value.data["hint"]
    assert hint2["prompt"] != hint["prompt"]  # Different reflection required
    
    # Persist second reflection
    await persist_justification(
        hash_key=hint2["hash"],
        domain=hint2["domain"],
        justification={
            "intent": "Preserve gradient continuity",
            "alternatives": [{"method": "nearest", "why_not": "Blocky appearance"}],
            "choice": {"method": "bilinear", "rationale": "Smooth DEM", "tradeoffs": "Interpolates values"},
            "confidence": "high"
        }
    )
    
    # Final retry - should succeed
    result = await reproject(...)
    assert result.status == "success"
```

#### 2.4 Update Documentation
**File**: `docs/development/MULTI_RISK_REFLECTION.md` (NEW)

Document:
- Why multi-risk operations exist
- How decorator stacking works
- Order of resolution (which decorator checks first)
- How models should handle chained requirements

**Acceptance Criteria**:
- Decorator stacking works without modification (verify)
- `raster_reproject` requires both CRS and resampling reflections
- Integration test passes
- Documentation explains pattern

---

## Phase 3: Documentation Updates
**Priority**: Medium-High  
**Estimated Time**: 2-3 hours  
**Dependencies**: Phase 1 complete

### Tasks

#### 3.1 Update ADR-0026
**File**: `docs/ADR/0026-epistemic-governance.md`

Current state: Modified but outdated (references old architecture).

Updates needed:
- Replace "epistemic governance" with "preflight reflection"
- Document new `@requires_reflection` decorator pattern
- Remove references to heuristic classification
- Update JSON schema example to 4-key structure
- Document cache location: `.preflight/justifications/`
- Add section on multi-risk decorator stacking

#### 3.2 Clean Methodology Documents
**Files**:
- `docs/design/epistemology/CRS.md`
- `docs/design/epistemology/RESAMPLING.md`
- `docs/design/epistemology/HYDROLOGY.md`
- `docs/design/epistemology/AGGREGATION.md`

For each file:
1. **Add header note**:
   ```markdown
   > **Note**: This is a design-time specification for developers.
   > It is NOT served as a runtime resource. Models receive inline
   > prompt guidance via `justify_*` prompts, not these documents.
   ```

2. **Remove all `resource://epistemology/*` references**

3. **Update "How to Use" sections**:
   - Replace: "Access via `resource://epistemology/crs`"
   - With: "Invoked automatically by `@requires_reflection` decorator on tools like `raster_reproject`"

4. **Add cross-reference to prompts**:
   ```markdown
   **Related Prompt**: See `src/prompts/crs.py` for the runtime guidance
   that models receive before CRS selection operations.
   ```

#### 3.3 Create Developer Guide
**File**: `docs/development/REFLECTION_PATTERN.md` (NEW)

Content outline:
```markdown
# Preflight Reflection Pattern

## When to Use
Use `@requires_reflection` when a tool:
- Makes irreversible choices (CRS, resampling method)
- Involves tradeoffs (accuracy vs performance)
- Requires domain expertise to justify

## Basic Usage
[Code example with single decorator]

## Multi-Risk Operations
[Code example with stacked decorators]

## Creating New Prompts
[Guidelines for writing reflection prompts]

## Testing Reflection Requirements
[How to write tests that verify reflection enforcement]
```

#### 3.4 Update Project Brief
**File**: `projectBrief.md`

Update architecture overview to mention:
- Preflight reflection via prompts (not resources)
- `.preflight/` cache directory
- `@requires_reflection` decorator pattern

**Acceptance Criteria**:
- ADR-0026 reflects current architecture
- No `resource://epistemology/*` references in docs
- Developer guide exists and is clear
- Project brief updated

---

## Phase 4: Tool Migration & Testing
**Priority**: Medium  
**Estimated Time**: 3-4 hours  
**Dependencies**: Phase 2 complete (for multi-risk pattern)

### Tasks

#### 4.1 Audit Remaining Tools
**Goal**: Identify which tools need reflection.

Audit checklist:
```bash
# List all tools
find src/tools -name "*.py" -not -name "__init__.py"

# For each tool, evaluate:
# - Does it make irreversible transformations?
# - Does it involve methodological choices?
# - Would a domain expert need to justify the approach?
```

**Initial candidates**:
- `src/tools/raster/convert.py` - May need resampling reflection if resolution changes
- `src/tools/raster/stats.py` - May need aggregation reflection for zonal statistics
- Future hydrology tools - Will need hydrology reflection

#### 4.2 Apply @requires_reflection to convert.py
**File**: `src/tools/raster/convert.py`

If conversion involves resolution change or resampling:
```python
@requires_reflection(
    prompt_name="justify_resampling_method",
    domain="resampling",
    args_fn=lambda args: {
        "data_type": "raster",
        "method": args.get("params").resampling if args.get("params") else "nearest",
        "source_resolution": "original",
        "target_resolution": "target",
        "operation_context": "format conversion with resampling",
    }
)
@mcp.tool(name="raster_convert", ...)
async def convert(...): ...
```

#### 4.3 Add Integration Test for Single-Risk Workflow
**File**: `test/test_reflection_workflow_single_risk.py` (NEW)

```python
async def test_reflection_workflow_end_to_end(test_raster, tmp_path):
    """Test complete workflow: block → prompt → persist → retry."""
    
    # Step 1: Attempt operation without reflection
    with pytest.raises(ToolError) as exc:
        await some_tool_requiring_reflection(...)
    
    # Step 2: Extract hint
    hint = exc.value.data["hint"]
    assert "prompt" in hint
    assert "hash" in hint
    assert "domain" in hint
    
    # Step 3: Call prompt (simulate model behavior)
    prompt_result = await call_prompt(hint["prompt"], hint["prompt_args"])
    
    # Step 4: Persist justification
    result = await persist_justification(
        hash_key=hint["hash"],
        domain=hint["domain"],
        justification={...valid JSON...}
    )
    assert result["status"] == "persisted"
    
    # Step 5: Retry operation - should succeed (cache hit)
    final_result = await some_tool_requiring_reflection(...)
    assert final_result is not None
```

#### 4.4 Add Cache Hit Test
**File**: `test/test_reflection_cache_hit.py` (NEW)

```python
async def test_cache_hit_skips_reflection(test_raster, tmp_path):
    """Verify cached justifications allow tool execution without blocking."""
    
    # Pre-populate cache
    store = get_store()
    justification = Justification(
        intent="Test intent",
        alternatives=[],
        choice={"method": "test", "rationale": "test", "tradeoffs": "none"},
        confidence="high"
    )
    hash_key = "test_hash_key"
    domain = "crs_datum"
    store.put(hash_key, justification, domain)
    
    # Mock the hash function to return our test key
    with patch('src.middleware.preflight._stable_hash', return_value=hash_key):
        # Tool should execute without ToolError
        result = await tool_with_reflection(...)
        assert result is not None
```

#### 4.5 Deprecate risk.py
**File**: `src/prompts/risk.py`

Once all tools use `@requires_reflection` (no heuristic classification needed):

1. Add deprecation warning to module docstring
2. Update tests to not rely on `classify()` or `input_hash()` functions
3. Eventually delete the module (not in this phase)

**Acceptance Criteria**:
- Tool audit complete with migration plan
- At least one more tool migrated (e.g., `convert.py`)
- Integration tests for single-risk and multi-risk workflows pass
- Cache hit test verifies optimization
- `risk.py` marked as deprecated

---

## Phase 5: Production Readiness (Future)
**Priority**: Low  
**Estimated Time**: 2-3 hours  
**Dependencies**: Phases 1-4 complete

### Optional Enhancements

#### 5.1 Confidence Threshold Enforcement
Add warnings or blocks for low-confidence justifications:

```python
# In persist_justification tool
if validated.confidence == "low":
    await ctx.warning(
        "Low confidence justification persisted. "
        "Consider revisiting this decision if conditions change."
    )
```

#### 5.2 Justification Expiration
Add TTL or versioning to cached justifications:

```python
# In DiskStore.put()
payload["_meta"] = {
    "created_at": int(time.time()),
    "expires_at": int(time.time()) + 86400 * 30,  # 30 days
    "schema_version": "1.0"
}
```

#### 5.3 Justification Audit Log
Track all reflections for later analysis:

```python
# Append to .preflight/audit.jsonl
{"timestamp": "...", "tool": "raster_reproject", "domain": "crs_datum", "confidence": "medium"}
```

#### 5.4 Model Guidance on Confidence
Add prompt guidance on when to use each confidence level:

```markdown
**Confidence Guidelines:**
- `low`: Uncertain about tradeoffs or lack domain knowledge
- `medium`: Reasonable choice but acknowledges alternatives
- `high`: Clear best choice for the specific use case
```

---

## Timeline Summary

| Phase | Priority | Time | Cumulative |
|-------|----------|------|------------|
| 1. Consolidation | Critical | 1-2h | 2h |
| 2. Multi-Risk | High | 4-6h | 8h |
| 3. Documentation | Med-High | 2-3h | 11h |
| 4. Migration & Testing | Medium | 3-4h | 15h |
| 5. Production (Optional) | Low | 2-3h | 18h |

**Target**: Complete Phases 1-4 (~15 hours) for production-ready state.

---

## Success Metrics

- ✅ All tests passing (currently 67, target 75+ with new integration tests)
- ✅ Zero "epistemic" references in code (except backward-compat alias)
- ✅ Multi-risk operations require all relevant reflections
- ✅ Documentation accurately reflects architecture
- ✅ At least 3 tools using `@requires_reflection` decorator
- ✅ Integration tests verify end-to-end workflow
- ✅ Developer guide enables contributors to add new reflections

---

## Risk Mitigation

### Risk: Decorator stacking doesn't work as expected
**Mitigation**: Test in Phase 2.1 before proceeding. If issues found, implement Option B (accumulate metadata).

### Risk: Too many reflections create friction
**Mitigation**: Monitor cache hit rates. If >80% cache hits after first use, friction is minimal.

### Risk: Models struggle with minimal JSON schema
**Mitigation**: Keep examples in prompts. If persistent issues, can expand schema slightly (but keep under 6 keys).

### Risk: Documentation drift
**Mitigation**: Add CI check to grep for `resource://epistemology` and fail if found.

---

## Questions for Product Owner

1. **Multi-risk priority**: Is chained reflection (Phase 2) a blocker for release?
2. **Tool coverage**: Should all transformation tools require reflection, or only "risky" ones?
3. **Confidence enforcement**: Should low-confidence justifications block execution or just warn?
4. **Cache policy**: Is 30-day TTL appropriate, or should justifications persist indefinitely?

---

## Next Session Checklist

**Start here**:
- [ ] Review this document
- [ ] Execute Phase 1 (git commit, cleanup)
- [ ] Decide on multi-risk approach (Phase 2)
- [ ] Begin documentation updates (Phase 3)

**Before declaring "done"**:
- [ ] All phases 1-4 complete
- [ ] Test suite at 75+ tests
- [ ] Documentation reviewed
- [ ] Demo multi-risk workflow end-to-end

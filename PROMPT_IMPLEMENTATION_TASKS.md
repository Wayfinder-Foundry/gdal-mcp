# GDAL MCP - Prompt Implementation Tasks

**Status**: Phase 2B Planning - Prompt Library Development  
**Updated**: 2025-10-17  
**Goal**: Complete the MCP three-pillar architecture by building out the prompt library

---

## Task Tracking

- **[tasks-directory]** Atomic task cards live under `docs/tasks/` (see `docs/tasks/README.md`).
- **[prompt-suite]** Week 1-3 items map to task files `1001-1011`.
- **[transactional-adr]** Transaction approval work is tracked via `1020-transactional-workflow-adr.md`.
- **[epistemology]** Methodology guardrails and justification workflow are defined in `docs/design/epistemology/IMPLEMENTATION_PLAN.md` with domain scaffolds in `docs/design/epistemology/`.

---

## Context

**What we have:**
- ✅ Tools: 5 production-ready raster/vector tools
- ✅ Resources: Phase 2A complete (catalog, metadata, reference)
- ⚠️ Prompts: 1 basic prompt (`gdal_task`)

**What we need:**
- 🎯 15-20 methodology prompts encoding domain expertise
- 🎯 Prompt testing infrastructure
- 🎯 Real-world validation with LLM interactions

---

## Phase 2B: Prompt Library Foundation (2-3 weeks)

### Week 1: Core Methodology Prompts (Priority 1)

#### Task 1.1: Terrain Analysis Methodology Prompt
**File**: `src/prompts/terrain.py`  
**Prompt**: `terrain_analysis_methodology(dem_path, analysis_goal, output_unit)`

**Requirements:**
- Guide DEM quality verification (resolution, CRS, voids)
- Explain preprocessing considerations (smoothing, filling)
- Provide algorithm selection guidance (Horn, Evans-Young)
- Include validation checklist
- Reference available tools (raster_info, raster_stats)

**Acceptance Criteria:**
- Prompt mentions CRS verification
- Provides decision tree for preprocessing
- Explains output unit implications (degrees vs percent)
- Includes quality check steps

**Estimated Time**: 4 hours

---

#### Task 1.2: Reprojection Decision Prompt
**File**: `src/prompts/reprojection.py`  
**Prompt**: `reprojection_methodology(input_file, target_use, current_crs)`

**Requirements:**
- Guide CRS selection based on use case (analysis vs visualization)
- Explain resampling method selection by data type
- Warn about distortion implications
- Reference `reference://crs/common` and `reference://resampling/guide`

**Acceptance Criteria:**
- Distinguishes between geographic (4326) and projected CRS
- Explains why certain resampling methods for certain data
- Mentions resolution preservation considerations
- Links to reference resources

**Estimated Time**: 3 hours

---

#### Task 1.3: Data Quality Assessment Prompt
**File**: `src/prompts/quality.py`  
**Prompt**: `assess_data_quality(file_path, intended_use, expected_specs)`

**Requirements:**
- Guide systematic quality checks (CRS, resolution, coverage, artifacts)
- Provide pass/fail criteria framework
- Suggest remediation steps for common issues
- Emphasize validation before analysis

**Acceptance Criteria:**
- Covers spatial properties verification
- Includes nodata handling checks
- Mentions compression artifact detection
- Provides clear "proceed" or "fix first" guidance

**Estimated Time**: 3 hours

---

#### Task 1.4: Format Conversion Strategy Prompt
**File**: `src/prompts/conversion.py`  
**Prompt**: `conversion_strategy(source_format, target_use, constraints)`

**Requirements:**
- Guide format selection based on use case (analysis, archival, web)
- Explain compression trade-offs (size vs speed vs quality)
- Recommend overview/tiling strategies
- Reference `reference://formats/raster` and `reference://compression/guide`

**Acceptance Criteria:**
- Explains COG for web delivery
- Discusses lossless vs lossy compression
- Mentions tiling benefits for large rasters
- Provides decision framework

**Estimated Time**: 3 hours

---

#### Task 1.5: Multi-Criteria Analysis Prompt
**File**: `src/prompts/analysis.py`  
**Prompt**: `suitability_analysis_methodology(criteria, weights, goal)`

**Requirements:**
- Guide data alignment (CRS, resolution, extent)
- Explain normalization approaches (min-max, z-score)
- Describe weighting and combination strategies
- Include sensitivity analysis considerations

**Acceptance Criteria:**
- Emphasizes spatial alignment importance
- Provides normalization decision tree
- Explains weighted sum vs weighted product
- Mentions validation approaches

**Estimated Time**: 4 hours

---

### Week 2: Parameter Selection & Validation Prompts (Priority 2)

#### Task 2.1: Resampling Method Selection Prompt
**File**: `src/prompts/parameters.py`  
**Prompt**: `choose_resampling_method(data_type, scale_change, output_use)`

**Requirements:**
- Decision tree based on data characteristics
- Explain why certain methods for certain data
- Consider computational cost vs accuracy
- Reference `reference://resampling/guide`

**Acceptance Criteria:**
- Covers categorical vs continuous distinction
- Explains upsampling vs downsampling implications
- Mentions edge case handling
- Provides clear recommendation + rationale

**Estimated Time**: 2 hours

---

#### Task 2.2: Compression Selection Prompt
**File**: `src/prompts/parameters.py`  
**Prompt**: `select_compression_strategy(data_type, size_constraints, speed_requirements)`

**Requirements:**
- Explain compression algorithm trade-offs
- Consider lossless vs lossy appropriateness
- Account for decoding speed implications
- Reference `reference://compression/available` and `reference://compression/guide`

**Acceptance Criteria:**
- Covers all major compression types (lzw, deflate, zstd, jpeg)
- Explains when lossy is acceptable
- Mentions decompression speed considerations
- Provides balanced recommendation

**Estimated Time**: 2 hours

---

#### Task 2.3: Validation Checklist Prompt
**File**: `src/prompts/validation.py`  
**Prompt**: `validate_operation_result(operation_type, input_specs, output_path)`

**Requirements:**
- Provide operation-specific validation steps
- Check spatial properties preservation
- Verify data integrity (ranges, nodata handling)
- Suggest visual inspection approaches

**Acceptance Criteria:**
- Tailored checks by operation (reprojection, conversion, etc.)
- Includes file-level and data-level validation
- Clear pass/fail criteria
- Actionable next steps if validation fails

**Estimated Time**: 3 hours

---

#### Task 2.4: CRS Selection Guidance Prompt
**File**: `src/prompts/parameters.py`  
**Prompt**: `recommend_crs(region, analysis_type, preserve_property)`

**Requirements:**
- Guide CRS selection by region and purpose
- Explain property preservation trade-offs (area, distance, angle)
- Reference `reference://crs/common/{coverage}`
- Distinguish analysis vs display requirements

**Acceptance Criteria:**
- Covers major CRS categories (geographic, UTM, state plane, web)
- Explains distortion implications
- Provides region-specific recommendations
- Links to CRS reference resources

**Estimated Time**: 2 hours

---

### Week 3: Workflow Composition & Testing (Priority 3)

#### Task 3.1: Workflow Planning Prompt
**File**: `src/prompts/workflow.py`  
**Prompt**: `plan_geospatial_workflow(goal, available_data, constraints)`

**Requirements:**
- Guide multi-step workflow decomposition
- Suggest operation sequencing
- Identify data dependencies
- Recommend intermediate validation points

**Acceptance Criteria:**
- Breaks complex goals into steps
- Considers data flow between operations
- Mentions error handling strategies
- Provides clear execution plan

**Estimated Time**: 4 hours

---

#### Task 3.2: Prompt Testing Infrastructure
**File**: `test/prompt_suite/test_prompts.py`  
**Tests**: Unit tests for all prompts

**Requirements:**
- Test prompt content includes expected keywords
- Validate parameter handling (required, optional, defaults)
- Check reference resource mentions
- Ensure prompts return valid strings

**Acceptance Criteria:**
- One test per prompt
- Tests validate structure and content
- Tests pass in CI/CD pipeline
- Coverage report shows prompt module tested

**Estimated Time**: 6 hours

---

#### Task 3.3: Prompt Documentation
**File**: `docs/fastmcp/PROMPT_LIBRARY.md`  
**Content**: Catalog of all prompts with usage examples

**Requirements:**
- Document each prompt's purpose
- Provide usage examples
- Explain when to use vs not use
- Show example LLM interactions (if available)

**Acceptance Criteria:**
- All prompts documented
- Organized by category (methodology, parameters, validation)
- Includes code examples
- Links to related ADRs and design docs

**Estimated Time**: 4 hours

---

#### Task 3.4: Integration Testing
**File**: `test/integration/test_prompt_guided_workflows.py`  
**Tests**: End-to-end workflows using prompts + tools + resources

**Requirements:**
- Simulate AI agent using prompts to guide tool selection
- Verify prompts reference available resources
- Test multi-step workflows with intermediate validation
- Capture real usage patterns

**Acceptance Criteria:**
- At least 3 integration tests (terrain analysis, reprojection workflow, quality assessment)
- Tests demonstrate prompt + resource + tool composition
- Tests pass consistently
- Document patterns for future tests

**Estimated Time**: 8 hours

---

## Phase 2C: Advanced Prompts & Refinement (2-3 weeks)

### Week 4-5: Domain-Specific Methodology Prompts

#### Task 4.1: Watershed Delineation Methodology
**File**: `src/prompts/hydrology.py`  
**Prompt**: `watershed_delineation_methodology(dem_path, pour_point)`

**Requirements:**
- Guide hydrologic workflow (fill sinks, flow direction, accumulation)
- Explain algorithm choices (D8 vs D-infinity)
- Provide validation criteria (continuity, downslope flow)
- Reference terrain tools when available

**Estimated Time**: 5 hours

---

#### Task 4.2: Change Detection Methodology
**File**: `src/prompts/temporal.py`  
**Prompt**: `change_detection_methodology(before_image, after_image, change_type)`

**Requirements:**
- Guide temporal data alignment
- Explain method selection by change type
- Cover radiometric normalization
- Provide classification and quantification approaches

**Estimated Time**: 5 hours

---

#### Task 4.3: Coastal Elevation Analysis
**File**: `src/prompts/specialized.py`  
**Prompt**: `coastal_elevation_methodology(dem_path, analysis_type)`

**Requirements:**
- Explain vertical datum considerations
- Discuss accuracy requirements by use case
- Cover edge effects at land-water boundary
- Provide coastal-specific validation

**Estimated Time**: 4 hours

---

### Week 6: Prompt Refinement & Real-World Testing

#### Task 6.1: LLM Interaction Testing
**Process**: Test prompts with actual LLM (Claude, GPT-4)

**Requirements:**
- Run prompts through LLM and capture responses
- Evaluate if guidance is followed correctly
- Identify ambiguities or missing information
- Refine prompts based on real usage

**Acceptance Criteria:**
- Test each prompt with at least 2 scenarios
- Document LLM behavior and quality of reasoning
- Create refinement tickets for unclear prompts
- Update prompts based on findings

**Estimated Time**: 12 hours

---

#### Task 6.2: Prompt Library Review
**Process**: Comprehensive review of all prompts

**Requirements:**
- Check consistency of tone and structure
- Verify all prompts reference appropriate resources
- Ensure no contradictory guidance across prompts
- Validate against vision/principles

**Acceptance Criteria:**
- All prompts follow consistent format
- Resource references are accurate
- No conflicting guidance
- Aligned with VISION.md principles

**Estimated Time**: 4 hours

---

## Supporting Tasks (Ongoing)

### ADR Documentation
**File**: `docs/ADR/0026-prompt-library-design.md`

**Content:**
- Document prompt design philosophy
- Explain guardrail approach (structure not scripts)
- Justify tiered prompt architecture
- Record lessons learned from testing

**Estimated Time**: 2 hours

---

### Update README
**File**: `README.md`

**Changes:**
- Add "Prompts" section documenting available prompts
- Update feature list to highlight prompt library
- Add example of prompt-guided workflow
- Update roadmap to reflect Phase 2B completion

**Estimated Time**: 1 hour

---

## Success Metrics

**Quantitative:**
- [ ] 15-20 prompts implemented
- [ ] 100% prompt test coverage
- [ ] All prompts documented
- [ ] Integration tests passing

**Qualitative:**
- [ ] Prompts demonstrate clear methodology guidance
- [ ] LLM interactions show improved reasoning
- [ ] Prompts enable multi-step workflows without user hand-holding
- [ ] Feedback from testing reveals prompts add value

**Vision Alignment:**
- [ ] Prompts encode domain expertise, not just tool instructions
- [ ] Prompts enable reasoning about WHY, not just WHAT
- [ ] Prompts compose with tools and resources naturally
- [ ] Prompts avoid being overly prescriptive

---

## Open Questions for Discussion

1. **Prompt Versioning**: How do we handle prompt evolution? Version numbers in metadata?
2. **Prompt Templating**: Should prompts accept more parameters for customization?
3. **Prompt Discovery**: How does AI know which prompt to use? Tool descriptions mention them?
4. **Prompt Composition**: Can prompts reference other prompts? Example: validation prompt called within methodology prompt?
5. **Feedback Loop**: How do we capture real-world prompt usage to refine them?

---

## Next Steps After Phase 2B

**Phase 2C**: Context & History Resources
- Session state tracking
- Operation provenance
- Workflow history

**Phase 2D**: Expanded Tool Coverage
- Terrain analysis tools (informed by prompt development)
- Vector operations (clip, buffer, intersect)
- Spatial analysis operations

**Phase 3**: Workflow Intelligence
- Multi-step workflow planning
- Inter-tool data flow
- Progress tracking for long operations

---

## Notes

- **Philosophy**: Prompts should guide thinking, not dictate steps
- **Balance**: Structure without rigidity, expertise without prescription
- **Testing**: Real LLM interactions are critical for validation
- **Iteration**: Expect to refine prompts based on usage
- **Documentation**: Each prompt needs clear "when to use" guidance

---

**Prepared**: 2025-10-17  
**Review**: Weekly during Phase 2B  
**Owner**: Development team

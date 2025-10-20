# GitHub Issues Creation - Quick Start Guide

This guide will help you create GitHub issues from the task files in `docs/tasks/`.

## What Was Created

A complete automated solution for creating GitHub issues from the 20 task markdown files in `docs/tasks/`.

### Files Added

1. **`scripts/create_issues_from_tasks.py`** - Main script (404 lines)
2. **`scripts/README.md`** - Detailed documentation (4,359 bytes)
3. **`test/test_create_issues_script.py`** - Test suite (6,295 bytes)
4. **Updated `docs/CONTRIBUTING.md`** - Added utility scripts section

## Quick Start

### Step 1: Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to authenticate with GitHub.

### Step 2: Preview Issues (Dry Run)

```bash
cd /home/runner/work/gdal-mcp/gdal-mcp
python scripts/create_issues_from_tasks.py --dry-run
```

This will show you exactly what issues would be created without actually creating them.

### Step 3: Create Issues

Once you're satisfied with the preview:

```bash
python scripts/create_issues_from_tasks.py
```

This will create 20 GitHub issues in the `Wayfinder-Foundry/gdal-mcp` repository.

## What the Issues Will Look Like

Each issue includes:

- **Title**: `[TASK_ID] Task Title`
- **Labels**: Automatically generated from priority, status, and tags
- **Body**: 
  - Metadata section (task ID, priority, status, owner, dates, dependencies)
  - Original task content (Summary, Rationale, Deliverables, Acceptance Criteria, Notes)
  - Footer with link to source file

## Task Files Processed

The script will create issues for these 20 task files:

### Prompt Tasks (1001-1011)
- 1001: Terrain analysis methodology prompt
- 1002: Reprojection methodology prompt
- 1003: Data quality assessment prompt
- 1004: Conversion strategy prompt
- 1005: Multi-criteria analysis prompt
- 1006: Prompt testing harness
- 1007: Resampling parameter prompt
- 1008: Compression parameter prompt
- 1009: Validation checklist prompt
- 1010: Workflow planning prompt
- 1011: Prompt documentation update

### ADR Task (1020)
- 1020: Transactional workflow ADR

### Epistemic Tasks (2001-2008)
- 2001: Epistemic risk classification
- 2002: Epistemic schema and store
- 2003: Epistemic preflight prompt
- 2004: Epistemic middleware and policy
- 2005: Epistemic reproject integration
- 2006: Epistemic resample integration
- 2007: Epistemic hydrology integration
- 2008: Epistemic aggregation integration

## Validation

All systems validated:
- ✓ Script parses all 20 task files successfully
- ✓ Issue formatting is correct
- ✓ Labels are properly generated
- ✓ Dependencies are tracked
- ✓ Dry-run mode works as expected
- ✓ Tests pass
- ✓ No security vulnerabilities

## Troubleshooting

If you encounter issues:

1. **Authentication Error**: Make sure you've run `gh auth login`
2. **Module Not Found**: Install with `pip install python-frontmatter`
3. **Permission Denied**: Ensure you have write access to the repository

For more details, see:
- `scripts/README.md` - Complete documentation
- `docs/CONTRIBUTING.md` - Utility scripts section

## Next Steps

After creating the issues:
1. Review the created issues on GitHub
2. Update dependencies if needed (task IDs != issue numbers)
3. Assign owners to specific tasks
4. Begin work on prioritized items

---

*This solution was created to fulfill the requirement: "create github issues for all of the tasks" in docs/tasks*

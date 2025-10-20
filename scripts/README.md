# GitHub Issue Creation from Task Files

This directory contains a script to automatically create GitHub issues from the task markdown files in `docs/tasks/`.

## Overview

The `create_issues_from_tasks.py` script:
- Parses all task markdown files in `docs/tasks/`
- Extracts metadata (task_id, title, priority, status, tags, dependencies)
- Formats the content for GitHub issues
- Creates issues using the GitHub CLI (`gh`)

## Prerequisites

1. **Python 3.11+**: The script requires Python 3.11 or higher
2. **python-frontmatter**: Install with `pip install python-frontmatter` (already in project dependencies)
3. **GitHub CLI**: Install from https://cli.github.com/
4. **Authentication**: You must be authenticated with GitHub CLI (`gh auth login`)

## Usage

### Dry Run (Recommended First)

Test the script without creating actual issues:

```bash
python scripts/create_issues_from_tasks.py --dry-run
```

This will:
- Parse all task files
- Display what issues would be created
- Show the title, labels, and body for each issue
- **Not create any actual GitHub issues**

### Create Issues

Once you've reviewed the dry-run output and are satisfied:

```bash
python scripts/create_issues_from_tasks.py
```

This will create actual GitHub issues in the `Wayfinder-Foundry/gdal-mcp` repository.

### Custom Repository

To create issues in a different repository:

```bash
python scripts/create_issues_from_tasks.py --repo owner/repo-name
```

### Custom Tasks Directory

To process tasks from a different directory:

```bash
python scripts/create_issues_from_tasks.py --tasks-dir /path/to/tasks
```

## Issue Format

Each GitHub issue will include:

### Title
```
[TASK_ID] Task Title
```

Example: `[1001] Implement terrain analysis methodology prompt`

### Labels

The script automatically adds labels based on:
- **Priority**: `priority:high`, `priority:medium`, `priority:low`, `priority:critical`
- **Status**: `status:todo`, `status:in_progress`, `status:blocked`, `status:done`
- **Tags**: All tags from the task metadata (e.g., `prompts`, `methodology`, `epistemology`)

### Body

The issue body includes:
1. **Metadata section**: Task ID, status, priority, owner, dates, dependencies
2. **Task content**: All sections from the original markdown file (Summary, Rationale, Deliverables, Acceptance Criteria, Notes)
3. **Footer**: Attribution to the source task file

### Dependencies

Tasks with `depends_on` references will include dependency links in the metadata:
```markdown
- **Depends on**: #1001, #1002
```

Note: The issue numbers used are the task_ids, not actual GitHub issue numbers. You may need to update these references after all issues are created.

## Example

For the task file `docs/tasks/1001-terrain-analysis-prompt.md`:

```yaml
---
task_id: "1001"
title: "Implement terrain analysis methodology prompt"
status: "todo"
priority: "high"
owner: "unassigned"
tags:
  - prompts
  - methodology
---
```

The script creates an issue with:
- **Title**: `[1001] Implement terrain analysis methodology prompt`
- **Labels**: `priority:high`, `status:todo`, `prompts`, `methodology`
- **Body**: Formatted metadata + task content

## Task Files Processed

The script processes all `.md` files in `docs/tasks/` except `README.md`. Currently, this includes:

- 1001-1011: Prompt implementation tasks
- 1020: ADR tasks
- 2001-2008: Epistemic enforcement tasks

Total: 20 task files

## Troubleshooting

### Authentication Error
```
Error: gh: authentication required
```
**Solution**: Run `gh auth login` and follow the prompts

### Module Not Found Error
```
ModuleNotFoundError: No module named 'frontmatter'
```
**Solution**: Install python-frontmatter: `pip install python-frontmatter`

### Label Creation
If labels don't exist in the repository, GitHub will create them automatically with default colors.

## Development

To modify the script:
1. Edit `scripts/create_issues_from_tasks.py`
2. Test with `--dry-run` flag
3. Verify the output matches expectations
4. Run without `--dry-run` to create issues

## Notes

- The script preserves the order of tasks (sorted alphabetically by filename)
- Task dependencies reference task IDs, not issue numbers
- Each issue includes a footer linking back to the source task file
- The script is idempotent-safe with `--dry-run` but will create duplicate issues if run multiple times without it

#!/usr/bin/env python3
"""
Script to create GitHub issues from task markdown files in docs/tasks/.

This script:
1. Parses all task markdown files
2. Extracts metadata and content
3. Creates GitHub issues using the GitHub CLI (gh)

Usage:
    python scripts/create_issues_from_tasks.py [--dry-run]

Options:
    --dry-run: Print the commands that would be executed without actually creating issues
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import frontmatter
except ImportError:
    print("Error: python-frontmatter is required. Install with: pip install python-frontmatter")
    sys.exit(1)


class TaskParser:
    """Parse task markdown files and extract metadata and content."""

    def __init__(self, tasks_dir: Path):
        self.tasks_dir = tasks_dir

    def get_task_files(self) -> List[Path]:
        """Get all task markdown files, excluding README.md."""
        task_files = sorted(self.tasks_dir.glob("*.md"))
        return [f for f in task_files if f.name != "README.md"]

    def parse_task(self, task_file: Path) -> Optional[Dict]:
        """Parse a single task file and extract metadata and content."""
        try:
            with open(task_file, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            metadata = post.metadata
            content = post.content

            return {
                "file": task_file.name,
                "task_id": metadata.get("task_id", ""),
                "title": metadata.get("title", ""),
                "status": metadata.get("status", "todo"),
                "priority": metadata.get("priority", "medium"),
                "owner": metadata.get("owner", "unassigned"),
                "created": metadata.get("created", ""),
                "updated": metadata.get("updated", ""),
                "tags": metadata.get("tags", []),
                "depends_on": metadata.get("depends_on", []),
                "content": content.strip(),
            }
        except Exception as e:
            print(f"Error parsing {task_file}: {e}", file=sys.stderr)
            return None

    def parse_all_tasks(self) -> List[Dict]:
        """Parse all task files and return a list of task dictionaries."""
        task_files = self.get_task_files()
        tasks = []

        for task_file in task_files:
            task = self.parse_task(task_file)
            if task:
                tasks.append(task)

        return tasks


class IssueCreator:
    """Create GitHub issues from parsed task data."""

    def __init__(self, repo: str = "Wayfinder-Foundry/gdal-mcp"):
        self.repo = repo

    def format_issue_body(self, task: Dict) -> str:
        """Format the issue body from task data."""
        body_parts = []

        # Add metadata section
        body_parts.append("## Metadata")
        body_parts.append(f"- **Task ID**: {task['task_id']}")
        body_parts.append(f"- **Status**: {task['status']}")
        body_parts.append(f"- **Priority**: {task['priority']}")
        body_parts.append(f"- **Owner**: {task['owner']}")
        body_parts.append(f"- **Created**: {task['created']}")
        body_parts.append(f"- **Updated**: {task['updated']}")

        if task.get("depends_on"):
            depends = ", ".join([f"#{dep}" for dep in task["depends_on"]])
            body_parts.append(f"- **Depends on**: {depends}")

        body_parts.append("")

        # Add the main content
        body_parts.append(task["content"])

        body_parts.append("")
        body_parts.append("---")
        body_parts.append(f"*This issue was automatically created from `docs/tasks/{task['file']}`*")

        return "\n".join(body_parts)

    def get_labels(self, task: Dict) -> List[str]:
        """Get labels for the issue based on task metadata."""
        labels = []

        # Add priority label
        if task.get("priority"):
            labels.append(f"priority:{task['priority']}")

        # Add status label
        if task.get("status"):
            labels.append(f"status:{task['status']}")

        # Add tags
        labels.extend(task.get("tags", []))

        return labels

    def create_issue(self, task: Dict, dry_run: bool = False) -> bool:
        """Create a GitHub issue for the task."""
        title = f"[{task['task_id']}] {task['title']}"
        body = self.format_issue_body(task)
        labels = self.get_labels(task)

        if dry_run:
            print(f"\n{'=' * 80}")
            print(f"Would create issue: {title}")
            print(f"Labels: {', '.join(labels)}")
            print(f"\nBody:\n{body}")
            print(f"{'=' * 80}\n")
            return True

        try:
            # Build the gh issue create command
            cmd = [
                "gh",
                "issue",
                "create",
                "--repo",
                self.repo,
                "--title",
                title,
                "--body",
                body,
            ]

            # Add labels if any
            if labels:
                for label in labels:
                    cmd.extend(["--label", label])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Created issue: {title}")
            print(f"  URL: {result.stdout.strip()}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create issue: {title}", file=sys.stderr)
            print(f"  Error: {e.stderr}", file=sys.stderr)
            return False

    def create_issues_for_tasks(self, tasks: List[Dict], dry_run: bool = False) -> int:
        """Create GitHub issues for all tasks."""
        success_count = 0
        total = len(tasks)

        print(f"Creating {total} GitHub issues from task files...")
        if dry_run:
            print("DRY RUN MODE: No issues will be created\n")

        for task in tasks:
            if self.create_issue(task, dry_run):
                success_count += 1

        return success_count


def main():
    parser = argparse.ArgumentParser(
        description="Create GitHub issues from task markdown files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without creating issues",
    )
    parser.add_argument(
        "--tasks-dir",
        type=Path,
        default=Path(__file__).parent.parent / "docs" / "tasks",
        help="Path to the tasks directory (default: docs/tasks)",
    )
    parser.add_argument(
        "--repo",
        default="Wayfinder-Foundry/gdal-mcp",
        help="GitHub repository (default: Wayfinder-Foundry/gdal-mcp)",
    )

    args = parser.parse_args()

    # Validate tasks directory
    if not args.tasks_dir.exists():
        print(f"Error: Tasks directory not found: {args.tasks_dir}", file=sys.stderr)
        sys.exit(1)

    # Parse tasks
    task_parser = TaskParser(args.tasks_dir)
    tasks = task_parser.parse_all_tasks()

    if not tasks:
        print("No tasks found to process", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(tasks)} task files to process")

    # Create issues
    issue_creator = IssueCreator(repo=args.repo)
    success_count = issue_creator.create_issues_for_tasks(tasks, dry_run=args.dry_run)

    # Print summary
    print(f"\n{'=' * 80}")
    if args.dry_run:
        print(f"DRY RUN: Would create {success_count}/{len(tasks)} issues")
    else:
        print(f"Successfully created {success_count}/{len(tasks)} issues")

    if success_count < len(tasks):
        print(f"Failed to create {len(tasks) - success_count} issues")
        sys.exit(1)


if __name__ == "__main__":
    main()

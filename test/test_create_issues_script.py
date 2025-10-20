"""
Tests for the create_issues_from_tasks.py script.

This test validates that the script can correctly parse task files
and format them for GitHub issue creation.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from create_issues_from_tasks import IssueCreator, TaskParser


class TestTaskParser:
    """Test the TaskParser class."""

    @pytest.fixture
    def tasks_dir(self):
        """Get the tasks directory path."""
        return Path(__file__).parent.parent / "docs" / "tasks"

    @pytest.fixture
    def parser(self, tasks_dir):
        """Create a TaskParser instance."""
        return TaskParser(tasks_dir)

    def test_get_task_files(self, parser):
        """Test that task files are correctly identified."""
        task_files = parser.get_task_files()
        
        # Should have multiple task files
        assert len(task_files) > 0
        
        # Should not include README.md
        assert all(f.name != "README.md" for f in task_files)
        
        # All should be .md files
        assert all(f.suffix == ".md" for f in task_files)

    def test_parse_task(self, parser, tasks_dir):
        """Test parsing a single task file."""
        # Parse a known task file
        task_file = tasks_dir / "1001-terrain-analysis-prompt.md"
        if not task_file.exists():
            pytest.skip("Task file not found")
        
        task = parser.parse_task(task_file)
        
        # Verify basic structure
        assert task is not None
        assert task["task_id"] == "1001"
        assert "terrain" in task["title"].lower()
        assert task["priority"] in ["low", "medium", "high", "critical"]
        assert task["status"] in ["todo", "in_progress", "blocked", "done"]
        assert isinstance(task["tags"], list)
        assert isinstance(task["depends_on"], list)
        assert len(task["content"]) > 0

    def test_parse_all_tasks(self, parser):
        """Test parsing all task files."""
        tasks = parser.parse_all_tasks()
        
        # Should have parsed multiple tasks
        assert len(tasks) > 15  # We know there are 20+ tasks
        
        # All tasks should have required fields
        for task in tasks:
            assert "task_id" in task
            assert "title" in task
            assert "content" in task
            assert "priority" in task
            assert "status" in task
            assert len(task["task_id"]) == 4  # Task IDs are 4 digits


class TestIssueCreator:
    """Test the IssueCreator class."""

    @pytest.fixture
    def creator(self):
        """Create an IssueCreator instance."""
        return IssueCreator()

    @pytest.fixture
    def sample_task(self):
        """Create a sample task for testing."""
        return {
            "file": "1001-terrain-analysis-prompt.md",
            "task_id": "1001",
            "title": "Implement terrain analysis methodology prompt",
            "status": "todo",
            "priority": "high",
            "owner": "unassigned",
            "created": "2025-10-17",
            "updated": "2025-10-17",
            "tags": ["prompts", "methodology"],
            "depends_on": [],
            "content": "## Summary\nTest content\n\n## Rationale\nTest rationale",
        }

    def test_format_issue_body(self, creator, sample_task):
        """Test formatting an issue body."""
        body = creator.format_issue_body(sample_task)
        
        # Verify key components are present
        assert "## Metadata" in body
        assert "Task ID: 1001" in body
        assert "Priority: high" in body
        assert "Status: todo" in body
        assert "## Summary" in body
        assert "Test content" in body
        assert "docs/tasks/1001-terrain-analysis-prompt.md" in body

    def test_format_issue_body_with_dependencies(self, creator, sample_task):
        """Test formatting with dependencies."""
        sample_task["depends_on"] = ["1000", "1002"]
        body = creator.format_issue_body(sample_task)
        
        # Verify dependencies are formatted
        assert "Depends on" in body
        assert "#1000" in body
        assert "#1002" in body

    def test_get_labels(self, creator, sample_task):
        """Test label generation."""
        labels = creator.get_labels(sample_task)
        
        # Verify expected labels
        assert "priority:high" in labels
        assert "status:todo" in labels
        assert "prompts" in labels
        assert "methodology" in labels

    def test_get_labels_all_priorities(self, creator, sample_task):
        """Test labels for all priority levels."""
        priorities = ["low", "medium", "high", "critical"]
        
        for priority in priorities:
            sample_task["priority"] = priority
            labels = creator.get_labels(sample_task)
            assert f"priority:{priority}" in labels

    def test_create_issue_dry_run(self, creator, sample_task, capsys):
        """Test issue creation in dry-run mode."""
        result = creator.create_issue(sample_task, dry_run=True)
        
        # Should succeed
        assert result is True
        
        # Should print issue details
        captured = capsys.readouterr()
        assert "[1001]" in captured.out
        assert "terrain" in captured.out.lower()


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_full_workflow(self):
        """Test the full parsing and formatting workflow."""
        tasks_dir = Path(__file__).parent.parent / "docs" / "tasks"
        
        # Parse tasks
        parser = TaskParser(tasks_dir)
        tasks = parser.parse_all_tasks()
        
        # Should have tasks
        assert len(tasks) > 0
        
        # Format issues
        creator = IssueCreator()
        
        # All tasks should be formattable
        for task in tasks:
            body = creator.format_issue_body(task)
            labels = creator.get_labels(task)
            
            # Basic validation
            assert len(body) > 100
            assert len(labels) >= 2  # At least priority and status
            assert "## Metadata" in body
            assert task["task_id"] in body

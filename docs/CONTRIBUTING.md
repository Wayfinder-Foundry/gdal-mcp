# Contributing to GDAL MCP

Thank you for considering contributing! We welcome bug reports, feature requests, documentation improvements, and code contributions.

## Vision

GDAL MCP aims to **democratize access to geospatial analysis** by removing the technical barriers of command-line tools and Python programming. We're building a bridge between domain experts and powerful GDAL operations through natural language interaction.

**Core Philosophy:**
- **Empathy-driven**: Remember the analyst who struggles with GDAL CLI
- **Production-quality**: Security, testing, and best practices first
- **LLM-optimized**: Design for conversational AI interaction

---

## Getting Started

### Option 1: Dev Container (Recommended)

The fastest way to get started is using the provided devcontainer configuration:

**Requirements:**
- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

**Steps:**
1. Fork and clone the repository
2. Open in VS Code
3. Click "Reopen in Container" when prompted (or use Command Palette: "Dev Containers: Reopen in Container")
4. Wait for setup to complete (3-5 minutes first time)

**What you get:**
- Pre-configured environment with GDAL, Python, and all dependencies
- VS Code extensions for Python development (Ruff, MyPy, etc.)
- Automated setup script that runs tests and quality checks
- Port forwarding for HTTP server testing

See [`.devcontainer/README.md`](.devcontainer/README.md) for detailed documentation.

### Option 2: Local Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/gdal-mcp.git
cd gdal-mcp
```

### 2. Install uv (Recommended)

We use [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Set Up Development Environment

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Or use uv sync (recommended)
uv sync --all-extras
```

### 4. Verify Installation

```bash
# Run quality gates
uv run ruff check .
uv run mypy src/

# Run tests
uv run pytest test/ -v

# Test CLI
uv run gdal --help
```

---

## Before Implementing a Feature

### **IMPORTANT: Review Architecture Decision Records (ADRs)**

Before implementing any feature, **you MUST review relevant ADRs** in `docs/ADR/`. ADRs document critical architectural decisions and design patterns that guide the project.

**Why ADRs Matter:**

ADRs capture the **"why"** behind design decisions, not just the "what". They help you:
- Understand constraints and trade-offs
- Align with existing patterns
- Avoid reinventing solutions to already-solved problems
- Design for LLM interaction from the start

**Example: Heavy Processing with Dask**

Let's say you want to add a tool for computing raster statistics on a massive 50GB DEM. Before implementing, check:

1. **ADR-0019** (Parallel Processing Strategy): Documents that we plan to use **Dask** for heavy processing tasks
2. **ADR-0020** (Context-Driven Tools): Explains how tools should provide real-time progress feedback to LLMs
3. **ADR-0021** (LLM-Optimized Descriptions): Shows how to write tool descriptions for AI interaction

**Why Dask?**
- **Chunked processing**: Process data in manageable pieces
- **Progress feedback**: Report progress to LLM in real-time (crucial for chat UX)
- **Memory efficiency**: Avoid loading entire 50GB file into RAM
- **Out-of-core**: Handle datasets larger than available memory

**What This Looks Like:**

```python
# DON'T: Load entire raster (crashes on large files)
data = rasterio.open('massive.tif').read()
mean = data.mean()

# DO: Use Dask for chunked processing with progress
import dask.array as da
from src.context import report_progress

with rasterio.open('massive.tif') as src:
    data = da.from_array(src.read(1), chunks=(1024, 1024))
    
    # Process in chunks with progress reporting
    for i, chunk in enumerate(data.blocks):
        partial_mean = chunk.mean().compute()
        report_progress(f"Processed chunk {i+1}/{data.nblocks}")
    
    final_mean = data.mean().compute()
```

**Key Point:** This design aligns with **chat client interaction expectations**. When a user asks "What's the mean elevation?", they expect:
- Real-time progress updates ("Processing chunk 1/100...")
- Not a 30-second frozen UI
- Graceful handling of memory constraints

**Always check ADRs first** to ensure your implementation aligns with these patterns!

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feat-your-feature-name
```

### 2. Make Your Changes

Follow these guidelines:
- **Style**: PEP 8 compliance (enforced by ruff)
- **Type hints**: Required for all function signatures
- **Tests**: Write tests for new functionality
- **ADRs**: Check relevant ADRs before designing

### 3. Run Quality Gates

```bash
# Lint and format
uv run ruff check . --fix
uv run ruff format .

# Type check
uv run mypy src/

# Tests
uv run pytest test/ -v
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: add your feature description"
git push origin feat-your-feature-name
```

### 5. Open a Pull Request

- Target branch: `main` or `develop`
- Include clear description of changes
- Reference any related issues
- Ensure CI passes

---

## Adding a New MCP Tool

New tools should follow established patterns:

### 1. Check ADRs First

- **ADR-0017**: Pydantic models for structured outputs
- **ADR-0020**: Context support for real-time feedback
- **ADR-0021**: LLM-optimized tool descriptions
- **ADR-0022**: Workspace scoping and security

### 2. Create Tool Module

Place in `src/tools/raster/` or `src/tools/vector/`:

```python
from fastmcp import Context
from src.app import mcp
from src.models.raster.your_tool import YourParams, YourResult

@mcp.tool(
    name="raster_your_tool",  # Underscores, not dots!
    description=(
        "Brief description. USE WHEN: specific use case. "
        "REQUIRES: inputs. OUTPUT: what it returns. "
        "SIDE EFFECTS: what it modifies."
    )
)
async def _your_tool(
    uri: str,
    params: YourParams,
    ctx: Context | None = None
) -> YourResult:
    """Detailed docstring."""
    # Implementation
    pass
```

### 3. Create Pydantic Models

Place in `src/models/raster/` or `src/models/vector/`:

```python
from pydantic import BaseModel, Field

class YourParams(BaseModel):
    """Parameters for your_tool."""
    param1: str = Field(description="What this param does")
    param2: int = Field(default=100, ge=1, description="Must be >= 1")

class YourResult(BaseModel):
    """Results from your_tool."""
    output1: str
    output2: float
```

### 4. Write Tests

Place in `test/`:

```python
import pytest
from src.tools.raster.your_tool import _your_tool

@pytest.mark.asyncio
async def test_your_tool(sample_raster):
    result = await _your_tool(sample_raster, YourParams())
    assert result.output1 is not None
```

### 5. Update Documentation

- Add tool to `src/prompts.py` if user-facing
- Update `CHANGELOG.md` under `[Unreleased]`
- Consider adding ADR if it introduces new patterns

---

## Testing Guidelines

### Run Tests Locally

```bash
# All tests
uv run pytest test/ -v

# Specific test file
uv run pytest test/test_raster_tools.py -v

# With coverage
uv run pytest test/ --cov=src --cov-report=html
```

### Test Fixtures

Use fixtures from `test/conftest.py`:
- `sample_raster`: Path to test GeoTIFF
- `sample_vector`: Path to test Shapefile

### CI Tests

GitHub Actions runs tests on:
- Python 3.10, 3.11, 3.12
- Every push and PR
- Required to pass before merge

---

## Code Review Process

All pull requests require:

1. **Passing CI**: All quality gates and tests must pass
2. **ADR compliance**: Changes align with architectural decisions
3. **Test coverage**: New code has corresponding tests
4. **Documentation**: Changes reflected in CHANGELOG, README, etc.
5. **Maintainer approval**: At least one maintainer review

Maintainers will review for:
- Code quality and style
- Security implications (workspace scoping)
- LLM interaction design
- Performance considerations

---

## Reporting Issues

### Bug Reports

Include:
- **Title**: Clear, descriptive summary
- **Environment**: OS, Python version, uv version
- **Steps to reproduce**: Minimal example
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs**: Error messages, stack traces

### Feature Requests

Include:
- **Use case**: Real-world scenario
- **Current limitations**: Why existing tools don't work
- **Proposed solution**: How you envision it working
- **LLM interaction**: How a user would ask for this in natural language

---

## Architecture Decision Records (ADRs)

When making significant architectural decisions, create an ADR:

```bash
# Create new ADR
cp docs/ADR/template.md docs/ADR/00XX-your-decision.md
```

ADRs should document:
- **Context**: What problem does this solve?
- **Decision**: What did we decide?
- **Rationale**: Why this approach over alternatives?
- **Consequences**: Trade-offs and implications
- **Examples**: Code samples showing usage

**Key ADRs to Review:**
- **ADR-0001**: FastMCP foundation
- **ADR-0017**: Pydantic models for structured outputs
- **ADR-0019**: Parallel processing strategy (Dask)
- **ADR-0020**: Context-driven tools (real-time feedback)
- **ADR-0021**: LLM-optimized descriptions
- **ADR-0022**: Workspace scoping and security

---

## Utility Scripts

The `scripts/` directory contains utility scripts for repository management:

### Creating GitHub Issues from Task Files

The `create_issues_from_tasks.py` script automates the creation of GitHub issues from task markdown files in `docs/tasks/`.

**Usage:**

```bash
# Preview what issues would be created (dry-run)
python scripts/create_issues_from_tasks.py --dry-run

# Create actual GitHub issues (requires gh CLI authentication)
python scripts/create_issues_from_tasks.py
```

**Prerequisites:**
- Python 3.11+
- `python-frontmatter` package (already in project dependencies)
- GitHub CLI (`gh`) authenticated with the repository

See [`scripts/README.md`](../scripts/README.md) for detailed documentation.

---

## Questions?

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

Thank you for contributing to GDAL MCP! Together, we're democratizing geospatial analysis. 🌍

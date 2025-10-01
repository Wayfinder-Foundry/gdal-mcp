# GitHub Actions Workflows

This directory contains GitHub Actions workflows for CI/CD automation using a **modular, reusable workflow architecture**.

## Architecture

Workflows are organized into **reusable components** that can be called from main orchestrator workflows:

```
.github/workflows/
├── ci.yml              # Main CI orchestrator (calls quality, test, build)
├── quality.yml         # Reusable: Lint & type check (ruff, mypy)
├── test.yml            # Reusable: Test suite (pytest)
├── build.yml           # Reusable: Build & verify wheel
├── publish.yml         # PyPI publishing on releases
└── README.md           # This file
```

**Benefits of Modular Design:**
- ✅ **Easy to maintain**: Each workflow has a single responsibility
- ✅ **Reusable**: Can be called from multiple orchestrators
- ✅ **Testable**: Can be triggered individually via workflow_dispatch
- ✅ **Scalable**: Add new workflows without bloating main CI file

---

## Workflows

### 🎯 **CI Orchestrator** (`ci.yml`)

**Main CI pipeline that coordinates all quality checks.**

**Triggers:**
- Push to `main`, `develop`, or `feat-*` branches
- Pull requests to `main` or `develop`
- Manual dispatch

**Flow:**
1. **Quality Gates** → Runs `quality.yml` (Python 3.12)
2. **Test Matrix** → Runs `test.yml` in parallel (Python 3.10, 3.11, 3.12)
3. **Build** → Runs `build.yml` (Python 3.12)

**Expected duration:** ~3-5 minutes

---

### 🔍 **Quality Gates** (`quality.yml`)

**Reusable workflow for code quality checks.**

**Jobs:**
- Lint with `ruff check`
- Format check with `ruff format --check`
- Type check with `mypy src/`

**When called from CI:** Uses Python 3.12 (configurable)

**Can also be called independently:**
```yaml
uses: ./.github/workflows/quality.yml
with:
  python-version: '3.12'
```

---

### 🧪 **Test Suite** (`test.yml`)

**Reusable workflow for running pytest tests.**

**Jobs:**
- Runs full pytest suite with verbose output
- Uploads coverage reports (when Python 3.12)
- Artifact retention: 30 days

**When called from CI:** Runs for Python 3.10, 3.11, 3.12 in matrix

**Can be called independently:**
```yaml
uses: ./.github/workflows/test.yml
with:
  python-version: '3.11'
```

---

### 📦 **Build** (`build.yml`)

**Reusable workflow for building and verifying distributions.**

**Jobs:**
- Build wheel with `uv build`
- Verify installation with `uv pip install dist/*.whl`
- Test CLI entrypoint: `gdal --help`
- Upload wheel artifact (30-day retention)

**Can be called independently:**
```yaml
uses: ./.github/workflows/build.yml
with:
  python-version: '3.12'
```

---

### 🚀 **Publish** (`publish.yml`)

**Automatic PyPI publishing on releases.**

**Triggers:**
- GitHub release published
- Manual dispatch (for testing)

**Jobs:**
1. Build distributions (wheel + sdist)
2. Publish to PyPI using trusted publishing (OIDC)
3. Upload release artifacts (90-day retention)

**Requirements:**
- PyPI trusted publishing configured (see setup below)
- GitHub release with semantic version tag (e.g., `v0.1.0`)

**Expected duration:** ~2-3 minutes

---

## Setup Requirements

### PyPI Trusted Publishing

To enable automatic publishing to PyPI without API tokens:

1. **Create PyPI project** (if not exists):
   - Go to https://pypi.org/manage/projects/
   - Create project named `gdal-mcp`

2. **Configure trusted publisher**:
   - Go to project settings → Publishing
   - Add GitHub as trusted publisher:
     - Owner: `JordanGunn`
     - Repository: `gdal-mcp`
     - Workflow: `publish.yml`
     - Environment: (leave empty)

3. **No API tokens needed!** GitHub Actions uses OIDC to authenticate.

---

## Creating a Release

To publish to PyPI via GitHub Actions:

```bash
# 1. Update version in pyproject.toml
# 2. Commit and push changes
git add pyproject.toml
git commit -m "chore: bump version to 0.1.0"
git push origin main

# 3. Create and push tag
git tag v0.1.0
git push origin v0.1.0

# 4. Create GitHub release
# Go to: https://github.com/JordanGunn/gdal-mcp/releases/new
# - Select tag: v0.1.0
# - Title: "Release v0.1.0"
# - Description: Release notes
# - Click "Publish release"

# 5. GitHub Actions will automatically publish to PyPI!
```

After publishing, users can install via:
```bash
uvx --from gdal-mcp gdal
```

---

## Local Testing

Before pushing, test locally:

```bash
# Quality gates
uv run ruff check . --fix
uv run ruff format .
uv run mypy src/

# Tests
uv run pytest test/ -v

# Build and verify
uv build
uv pip install dist/*.whl
gdal --help
```

---

## Workflow Status Badges

Add to README.md:

```markdown
[![CI](https://github.com/JordanGunn/gdal-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/JordanGunn/gdal-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/gdal-mcp)](https://pypi.org/project/gdal-mcp/)
```

---

## Modular Workflow Pattern

**Why Reusable Workflows?**

GitHub Actions supports [reusable workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows) which allow:

1. **Single Responsibility**: Each workflow does one thing well
2. **Composition**: Build complex pipelines from simple components
3. **Reusability**: Same quality checks across multiple triggers
4. **Maintainability**: Update logic in one place

**Example: Using quality.yml independently**

Create a PR quality check workflow:
```yaml
name: PR Quality
on: pull_request

jobs:
  quality:
    uses: ./.github/workflows/quality.yml
    with:
      python-version: '3.12'
```

---

## Troubleshooting

### CI fails on lint

**Solution:** Run locally and fix:
```bash
uv run ruff check . --fix
uv run ruff format .
```

### CI fails on type check

**Solution:** Run locally and fix:
```bash
uv run mypy src/
```

### Build fails: "gdal --help" not found

**Solution:** Ensure `pyproject.toml` has correct script entry:
```toml
[project.scripts]
"gdal" = "src.__main__:main"
```

### Publish fails

**Solutions:**
- Ensure PyPI trusted publishing is configured
- Check release tag follows semantic versioning (vX.Y.Z)
- Verify version in `pyproject.toml` matches tag

---

## Workflow Files Summary

| File | Type | Purpose | Triggered By |
|------|------|---------|--------------|
| `ci.yml` | Orchestrator | Main CI pipeline | Push, PR, manual |
| `quality.yml` | Reusable | Lint & type check | Called by ci.yml |
| `test.yml` | Reusable | Run pytest suite | Called by ci.yml |
| `build.yml` | Reusable | Build & verify | Called by ci.yml |
| `publish.yml` | Standalone | PyPI publishing | GitHub release |

---

## Comparison to GitLab CI

If you're coming from GitLab CI:

| GitLab CI | GitHub Actions |
|-----------|----------------|
| `.gitlab-ci.yml` | `.github/workflows/ci.yml` |
| `include: local:` | `uses: ./.github/workflows/` |
| `extends:` | Reusable workflows |
| `stages:` | `jobs:` with `needs:` |
| `script:` | `run:` |
| Variables | `inputs:` in reusable workflows |

**Key difference:** GitHub Actions reusable workflows are **separate files** rather than inherited job templates, making them more modular and easier to reason about.

---

## Resources

- **Reusable Workflows**: https://docs.github.com/en/actions/using-workflows/reusing-workflows
- **Workflow Syntax**: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **Security Hardening**: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions

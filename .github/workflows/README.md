# GitHub Actions Workflows

This directory contains GitHub Actions workflows for CI/CD automation.

## Workflows

### 🔍 **CI Workflow** (`ci.yml`)

**Triggers:**
- Push to `main`, `develop`, or `feat-*` branches
- Pull requests to `main` or `develop`
- Manual dispatch

**Jobs:**

1. **Quality Gates** (Lint & Type Check)
   - Runs `ruff` for linting and formatting checks
   - Runs `mypy` for type checking
   - Fails fast if code quality issues detected

2. **Test Suite** (Matrix: Python 3.10, 3.11, 3.12)
   - Runs full pytest suite on multiple Python versions
   - Uploads coverage reports for Python 3.12
   - Ensures cross-version compatibility

3. **Build Distribution**
   - Builds wheel using `uv build`
   - Verifies wheel can be installed
   - Tests CLI entrypoint (`gdal-mcp --help`)
   - Uploads wheel as artifact (30-day retention)

**When it runs:** Every push and pull request

**Expected duration:** ~3-5 minutes

---

### 📦 **Publish Workflow** (`publish.yml`)

**Triggers:**
- GitHub release published
- Manual dispatch (for testing)

**Jobs:**

1. **Publish to PyPI**
   - Builds source distribution and wheel
   - Publishes to PyPI using trusted publishing (OIDC)
   - Uploads release artifacts (90-day retention)

**Requirements:**
- PyPI trusted publishing configured (see setup below)
- GitHub release created with semantic version tag (e.g., `v0.1.0`)

**When it runs:** When you create a GitHub release

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

**Alternative (API Token Method):**
If you prefer using API tokens:
- Create PyPI API token
- Add to GitHub Secrets as `PYPI_API_TOKEN`
- Update `publish.yml` to use token authentication

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
uvx --from gdal-mcp gdal-mcp
```

---

## Local Testing

Before pushing, test locally:

```bash
# Quality gates
uv run ruff check .
uv run ruff format --check .
uv run mypy src/

# Tests
uv run pytest test/ -v

# Build
uv build
uv pip install dist/*.whl
gdal-mcp --help
```

---

## Workflow Status Badges

Add to README.md:

```markdown
[![CI](https://github.com/JordanGunn/gdal-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/JordanGunn/gdal-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/gdal-mcp)](https://pypi.org/project/gdal-mcp/)
```

---

## Troubleshooting

**CI fails on lint:**
- Run `uv run ruff check . --fix` locally
- Run `uv run ruff format .` locally
- Commit fixes

**CI fails on type check:**
- Run `uv run mypy src/` locally
- Fix type errors
- Commit fixes

**Publish fails:**
- Ensure PyPI trusted publishing is configured
- Check release tag follows semantic versioning (vX.Y.Z)
- Verify version in `pyproject.toml` matches tag

**Build artifact not appearing:**
- Check workflow logs for build errors
- Artifacts expire after 30/90 days (configurable)

---

## Comparison to GitLab CI

If you're coming from GitLab CI:

| GitLab CI | GitHub Actions |
|-----------|----------------|
| `.gitlab-ci.yml` | `.github/workflows/*.yml` |
| `stages:` | `jobs:` with `needs:` |
| `script:` | `run:` |
| `artifacts:` | `actions/upload-artifact@v4` |
| `dependencies:` | `needs:` |
| `only/except` | `on:` with filters |
| `cache:` | `actions/cache@v4` |
| Variables | `env:` or secrets |
| CI/CD variables | GitHub Secrets |

**Key differences:**
- GitHub Actions uses marketplace actions (reusable components)
- Jobs run in parallel by default (use `needs:` for dependencies)
- Matrix builds are native (`strategy.matrix`)
- Artifacts are separate from job outputs

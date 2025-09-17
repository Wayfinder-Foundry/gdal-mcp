# Agents / Contributor Guide — Python best practices & PEP adherence

Purpose
- Provide concise, actionable guidance for contributors and automated agents working on this repository.
- Emphasize adherence to Python PEPs (style, typing, docstrings) and the project's tooling.
- Add project-specific notes for GDAL native dependencies, packaging, and CI.

Core principles
- Follow PEP 8 for style and naming (use snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE for constants).
- Use PEP 257 docstrings for modules, classes, and public functions/methods.
- Prefer type hints (PEP 484). Keep signatures explicit and avoid overly broad Any where a concrete type helps readability.
- Keep functions small and single-responsibility. Favor composition over inheritance when appropriate.

Formatting & linting
- Use Black for formatting; accept its defaults (88-char line length).
- Use Ruff for linting and auto-fixes; resolve remaining issues manually.
- Commands:
  - pip install -e ".[dev]"
  - black stac_mcp/ tests/ examples/ || black .
  - ruff check stac_mcp/ tests/ examples/ --fix

Testing & validation
- Write tests for behavior, not implementation; prefer parametrized tests for similar cases.
- Run the full test suite locally:
  - pytest -v
- Validate MCP/CLI/server functionality (example usage):
  - python examples/example_usage.py
- Integration tests that exercise GDAL bindings require system GDAL — see GDAL setup below.

GDAL / native dependency notes (project-specific)
- GDAL is a native dependency. Prefer a conda/mamba environment to install matching GDAL and libgdal:
  - conda create -n gdal-mcp python=3.11
  - conda activate gdal-mcp
  - mamba install -c conda-forge gdal
- Alternative: use platform-provided GDAL or manylinux wheels built with cibuildwheel in CI.
- When GDAL is installed via conda/docker, set GDAL env vars when necessary:
  - export GDAL_DATA=/path/to/gdal/data
  - export PROJ_LIB=/path/to/proj/data
- In CI, use a docker image or matrix entries that include preinstalled GDAL to validate integration tests.

Packaging & CI
- Use pyproject.toml / PEP 517 for builds. When building wheels for distribution prefer cibuildwheel for manylinux wheels.
- CI should:
  - install dev deps,
  - run Black and Ruff,
  - run tests (unit + integration where GDAL is available),
  - lint and type-check (optional: mypy).
- For reproducible CI builds involving GDAL, use Docker images with system GDAL or rely on conda-forge channels in the runner.

Logging & errors
- Use the standard logging module; configure logging at entrypoints only.
- Do not swallow exceptions silently. Surface useful context and wrap exceptions only when adding helpful information.
- Avoid print() for diagnostics in library code.

Async & IO
- Prefer async APIs when interacting with network or IO in the MCP server; follow standard asyncio patterns.
- Avoid blocking calls in async code. Use run_in_executor for CPU-bound or blocking work.

Dependencies & environment
- Use virtual environments, uv for isolation.
- Pin dev dependencies in pyproject.toml where appropriate.
- Install in editable mode during development: pip install -e ".[dev]"

Commit & PR guidance
- Write clear commit messages with intent and scope.
- Run formatting and tests before pushing.
- Keep PRs focused and small; include a brief description of changes and validation steps.
- If the change affects GDAL behavior or integration tests, document how to reproduce locally.

CI & pre-merge checks
- Ensure Black and Ruff pass.
- Ensure all tests pass locally and in the CI.
- Ensure platform-specific integration tests that rely on GDAL run in at least one CI job.
- Follow the repository's Validation checklist (format, lint, tests, example run).

Quick contributor checklist
1. Prepare environment (uv recommended for GDAL):
    - uv new gdal-mcp python=3.11
    - uv activate gdal-mcp
    - uv install gdal
2. Install dev deps:
   - pip install -e ".[dev]"
3. Format & lint:
   - black stac_mcp/ tests/ examples/
   - ruff check stac_mcp/ tests/ examples/ --fix
4. Run tests:
   - pytest -v
5. Smoke test example:
   - python examples/example_usage.py
6. If changes touch GDAL integration:
   - run integration tests against a GDAL-enabled environment (local conda or CI job).

References
- PEP 8 — Style Guide for Python Code: https://peps.python.org/pep-0008/
- PEP 257 — Docstring Conventions: https://peps.python.org/pep-0257/
- PEP 484 — Type Hints: https://peps.python.org/pep-0484/
- GDAL site: https://gdal.org/
- conda-forge GDAL: https://anaconda.org/conda-forge/gdal

Notes
- This project standardizes on Black, Ruff, and pytest — prefer those tools and the commands above.
- Keep changes minimal, test-driven, and well-documented in PR descriptions.
- Regularly update this guide as tooling, GDAL versions, or practices evolve.
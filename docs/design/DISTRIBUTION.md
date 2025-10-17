---
type: product_context
title: Distribution Strategy
tags: [distribution, uvx, docker, product_context]
---

# Distribution Strategy

Shipping the GDAL MCP consistently across environments is as important as implementing the tools themselves. This plan highlights two first-class distribution paths—`uvx` and Docker—alongside release automation and repository structure guidance.

## `uvx` Distribution

`uvx` offers a zero-install launcher for Python applications. By publishing the GDAL MCP as a Python package, users can execute the server directly with `uvx gdal-mcp` without pre-installing dependencies.

Implementation details:

1. **Packaging metadata.** Use `pyproject.toml` with `project.scripts = { "gdal-mcp" = "gdal_mcp.__main__:main" }` so `uvx` exposes a console entry point.
2. **fastMCP integration.** Depend on `fastmcp` and configure the entrypoint to instantiate the GDAL tool set before handing control to fastMCP’s server runner.
3. **Wheel dependencies.** Document that GDAL binaries will not be explicitly used, but rather, emulated in alignment with the ubiquotously known gdal CLI commands. This avoids the requirement that the GDAL binaries be available on the host system.
4. **Version pinning.** Leverage `uv lock` files to ensure deterministic dependency resolution for both development and runtime.
5. **Usage docs.** Add a quick-start snippet to the README:
   ```bash
   uvx gdal-mcp --workspace /data/projects
   ```
   The launcher downloads the wheel, resolves dependencies, and starts the fastMCP server in one step.
6. **Offline-friendly.** Encourage teams to prime a private `uvx` package index or pre-populate caches when air-gapped deployments are required.

This approach is ideal for developers who already use `uv` or want an ephemeral environment without managing virtualenvs manually.

## Docker Distribution

Docker remains the an alternative way to bundle the application:

1. **Base image.** Start from an official GDAL image or a slim Python image with GDAL installed via `apt`.
2. **Layering.** Copy the packaged wheel (built during CI) into the container and install it with `pip` or `uv pip install`. Include healthcheck scripts and default configuration.
3. **Runtime.** Expose the fastMCP HTTP port and mount a workspace volume for input/output datasets.
4. **Publishing.** Push versioned images to a registry so that users can run `docker run ghcr.io/org/gdal-mcp:latest` and obtain a consistent environment.

Combining Docker with `uvx` lets teams choose between light-weight local execution and fully isolated containers.

## Release Automation

1. **Continuous Integration.** Configure GitHub Actions to run tests, linting, and sample tool invocations on every pull request.
2. **Tagged releases.** When tagging a release, CI should build wheels, generate the Docker image, run smoke tests, and publish artefacts to PyPI and the container registry.
3. **Changelog management.** Maintain `CHANGELOG.md` so users can trace tool additions, schema updates, and dependency changes across releases.

## Local Development

- Use `uv` for dependency management (`uv sync` to install dev requirements and create a managed virtual environment).
- Provide `uv run` commands in contributor docs so developers can launch the fastMCP server (`uv run gdal-mcp serve --transport stdio`).
- Document how to run HTTP transport (`uv run gdal-mcp serve --transport http --port 8000`) and how to override GDAL discovery with `GDAL_MCP_GDAL_HOME` if needed.
- Include sample datasets in `test/data/` for integration testing and documentation examples.
- Encourage pre-commit hooks (`uv run pre-commit run --all-files`) to enforce formatting and schema linting before pushing changes.

By centring `uvx` and Docker, the GDAL MCP project delivers a flexible installation experience that mirrors modern Python tooling while respecting GDAL’s native dependencies.

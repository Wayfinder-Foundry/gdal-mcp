# GDAL MCP Development Container

This directory contains the development container configuration for GDAL MCP, providing a consistent, pre-configured development environment.

## What's Included

### Base Image
- **GDAL**: Official GDAL 3.8.0 Ubuntu image with full geospatial libraries
- **Python**: Python 3.12 with development headers
- **System Tools**: git, curl, vim, jq, and other essential utilities

### Python Stack
- **uv**: Fast Python package manager for dependency management
- **Rasterio**: Python bindings for GDAL raster operations
- **PyProj**: Coordinate reference system transformations
- **pyogrio/Fiona**: Vector data I/O
- **Shapely**: Geometric operations
- **All dev dependencies**: pytest, mypy, ruff, etc.

### VS Code Extensions
- Python language support and IntelliSense
- Ruff (linting and formatting)
- MyPy (type checking)
- YAML and TOML support
- GitLens for Git integration
- Docker support

## Getting Started

### Prerequisites
- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

### Opening in a Container

#### Method 1: VS Code Command Palette
1. Open the repository in VS Code
2. Press `F1` or `Ctrl+Shift+P` (Windows/Linux) / `Cmd+Shift+P` (Mac)
3. Type "Dev Containers: Reopen in Container"
4. Wait for the container to build (first time takes 3-5 minutes)

#### Method 2: VS Code Prompt
1. Open the repository in VS Code
2. Click "Reopen in Container" when prompted in the bottom-right corner

#### Method 3: GitHub Codespaces
1. Go to the repository on GitHub
2. Click "Code" → "Codespaces" → "Create codespace on main"
3. Wait for the environment to initialize

### First Build
The first time you open the devcontainer:
- Docker will build the image (~3-5 minutes)
- `postCreateCommand.sh` will run automatically:
  - Installs Python dependencies with `uv sync`
  - Runs initial quality checks (linting, type checking)
  - Runs the test suite
  - Creates necessary directories

## Development Workflow

### Running the MCP Server

**Stdio transport (for MCP clients):**
```bash
uv run gdal --transport stdio
```

**HTTP transport (for testing):**
```bash
uv run gdal --transport http --port 8000
```

The HTTP server will be accessible at `http://localhost:8000` (automatically forwarded).

### Testing

**Run all tests:**
```bash
uv run pytest test/ -v
```

**Run with coverage:**
```bash
uv run pytest test/ --cov=src --cov-report=html
```

**Run specific test file:**
```bash
uv run pytest test/test_raster_tools.py -v
```

### Code Quality

**Lint and format:**
```bash
uv run ruff check . --fix
uv run ruff format .
```

**Type checking:**
```bash
uv run mypy src/
```

**Run all quality gates:**
```bash
uv run ruff check . --fix && uv run ruff format . && uv run mypy src/
```

### Working with GDAL Data

Test data is available in `/workspace/test/data/`:
- Sample rasters (GeoTIFF)
- Sample vectors (Shapefile, GeoJSON)
- Fixtures for automated testing

The workspace is configured with `GDAL_MCP_WORKSPACES=/workspace/test/data` for security testing.

## Container Features

### Environment Variables
- `GDAL_CACHEMAX=512`: GDAL cache size
- `PYTHONDONTWRITEBYTECODE=1`: Prevent .pyc files
- `PYTHONUNBUFFERED=1`: Real-time output
- `GDAL_MCP_WORKSPACES=/workspace/test/data`: Allowed file paths

### Port Forwarding
- **Port 8000**: HTTP transport for MCP server

### Volume Mounts
- `.uv/`: UV package cache (persisted)
- `.cache/`: General cache directory (persisted)
- Full workspace mounted at `/workspace`

### User Configuration
- Runs as `vscode` user (non-root)
- Sudo access available for system changes
- User UID/GID matches host (1000:1000)

## Troubleshooting

### Container Build Fails
- Check Docker has enough resources (4GB+ RAM recommended)
- Clear Docker cache: `docker system prune -a`
- Rebuild: `F1` → "Dev Containers: Rebuild Container"

### Dependencies Not Installing
```bash
# Manually sync dependencies
uv sync --all-extras

# Clear UV cache and reinstall
rm -rf .uv/ && uv sync --all-extras
```

### Tests Failing
- Ensure you're in the workspace directory: `cd /workspace`
- Check test data exists: `ls test/data/`
- Run with verbose output: `uv run pytest test/ -vv`

### GDAL Tools Not Found
The devcontainer uses Python-native libraries (Rasterio, pyogrio) instead of GDAL CLI tools. All operations are performed through Python bindings.

## Customization

### Adding VS Code Extensions
Edit `.devcontainer/devcontainer.json`:
```json
"extensions": [
  "existing.extension",
  "your.new-extension"
]
```

### Changing Python Version
Edit `.devcontainer/devcontainer.json`:
```json
"args": {
  "PYTHON_VERSION": "3.11"
}
```

### Adding System Packages
Edit `.devcontainer/Dockerfile` and add to the `apt-get install` section.

## Resources

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [GDAL Documentation](https://gdal.org/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## Contributing

Improvements to the devcontainer are welcome! Please:
1. Test changes locally
2. Update this README if needed
3. Submit a PR with clear description

---

**Happy Developing! 🚀**

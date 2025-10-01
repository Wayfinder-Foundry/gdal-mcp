# ADR-0022: Workspace Scoping and Access Control

**Status**: Accepted  
**Date**: 2025-09-30  
**Deciders**: Jordan Gunn, Cascade AI  
**Tags**: #security #access-control #mcp #workspaces

## Context

MCP servers often run with elevated privileges and can access any file on the system. This poses security risks:

1. **Unintended data access**: Analysts may have sensitive data in various directories
2. **Path traversal**: Malicious or accidental access to system files
3. **Multi-tenant concerns**: Different users/projects should have isolated data access
4. **Compliance**: Data governance may require strict access boundaries

**Current state**: GDAL MCP tools accept any file path without validation. A tool could potentially access:
- `/etc/passwd` (system files)
- `/home/other_user/private/` (other users' data)
- Any path the server process can read

**MCP specification** defines a "roots" capability where clients can declare filesystem boundaries, but:
- Clients expose roots to servers (optional)
- Servers must respect and enforce boundaries
- Defense in depth requires server-side validation

## Decision

**Implement workspace scoping** with configurable allowed directories:

### 1. **Configuration Sources** (Priority Order)

**Priority 1**: Environment variable (highest)
```bash
GDAL_MCP_WORKSPACES="/data/projects:/home/user/gis:/mnt/shared"
```

**Priority 2**: Config file `gdal-mcp.yaml` (if exists in CWD or `~/.config/gdal-mcp/`)
```yaml
workspaces:
  - /data/projects
  - /home/user/gis
  - /mnt/shared/geospatial
```

**Priority 3**: No configuration = allow all (backward compatible, but warn in logs)

### 2. **Path Validation Rules**

```python
def validate_path(path: str, workspaces: list[Path]) -> Path:
    """Validate and resolve path against allowed workspaces.
    
    Args:
        path: User-provided path (relative or absolute)
        workspaces: List of allowed workspace directories
    
    Returns:
        Resolved absolute path
    
    Raises:
        ToolError: If path is outside allowed workspaces
    """
    # Resolve to absolute path (handles .., symlinks)
    resolved = Path(path).resolve()
    
    # If no workspaces configured, allow all (backward compatible)
    if not workspaces:
        return resolved
    
    # Check if path is within any allowed workspace
    for workspace in workspaces:
        try:
            resolved.relative_to(workspace)
            return resolved  # ✓ Path is allowed
        except ValueError:
            continue
    
    # Path is outside all workspaces - DENY
    raise ToolError(
        f"Access denied: '{path}' is outside allowed workspaces. "
        f"Allowed directories: {', '.join(str(w) for w in workspaces)}"
    )
```

### 3. **Integration Points**

**Every tool that accesses files must validate paths:**

```python
# raster.info
async def _info(uri: str, ctx: Context | None = None) -> Info:
    # Validate path before opening
    validated_path = validate_path(uri, get_workspaces())
    
    with rasterio.open(str(validated_path)) as ds:
        ...
```

**Validation happens in core logic functions** (not MCP wrappers) to ensure:
- Direct function calls (tests) are also validated
- Consistent security regardless of entry point

### 4. **MCP Roots Capability** (Optional Future Enhancement)

FastMCP may expose `roots` capability to declare workspaces to clients:

```python
# Future: Expose workspaces as MCP roots
mcp.add_roots([
    Root(uri=f"file://{ws}", name=ws.name)
    for ws in get_workspaces()
])
```

Benefits:
- Clients can show workspace boundaries in UI
- Better UX (users know where they can access data)
- Standards-compliant MCP implementation

## Rationale

### Why Environment Variables?

**Pros**:
- ✅ Simple deployment (no config files to manage)
- ✅ Works with Docker, systemd, MCP client configs
- ✅ Easy to override per-instance
- ✅ Standard practice (12-factor apps)

**Cons**:
- ⚠️ Limited to simple list (no per-workspace metadata)
- ⚠️ Not ideal for complex configs

### Why Config File?

**Pros**:
- ✅ Structured configuration (YAML)
- ✅ Can add per-workspace metadata (read-only, labels, etc.)
- ✅ Version-controllable

**Cons**:
- ⚠️ Requires file management
- ⚠️ Harder to override per-instance

### Why Both?

**Best of both worlds**:
- Env var for simple/production deployments
- Config file for complex scenarios
- Env var takes precedence (easy override)

### Why "No Config = Allow All"?

**Backward compatibility**:
- ✅ Existing deployments continue working
- ✅ Development/testing doesn't require setup
- ✅ Users can opt-in to security

**But**:
- ⚠️ Log clear WARNING when running unrestricted
- ⚠️ Documentation emphasizes production should configure workspaces

### Why Validate in Core Functions?

**Defense in depth**:
```python
# Validation happens here (core logic)
async def _info(uri: str, ctx: Context | None = None):
    validated_path = validate_path(uri, get_workspaces())
    ...

# Not here (MCP wrapper)
async def info(uri: str, ctx: Context | None = None):
    return await _info(uri, ctx)  # Already validated
```

**Benefits**:
- ✅ Tests also enforce security
- ✅ Direct function calls are secured
- ✅ No way to bypass validation

## Implementation Pattern

### Configuration Loader

```python
# src/config.py
from pathlib import Path
import os
import yaml

def get_workspaces() -> list[Path]:
    """Load allowed workspace directories from config.
    
    Priority:
    1. GDAL_MCP_WORKSPACES env var (colon-separated)
    2. gdal-mcp.yaml config file
    3. Empty list (allow all, with warning)
    """
    # Priority 1: Environment variable
    env_workspaces = os.getenv("GDAL_MCP_WORKSPACES")
    if env_workspaces:
        return [
            Path(ws.strip()).resolve() 
            for ws in env_workspaces.split(":")
            if ws.strip()
        ]
    
    # Priority 2: Config file
    config_paths = [
        Path.cwd() / "gdal-mcp.yaml",
        Path.home() / ".config/gdal-mcp/config.yaml",
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                if "workspaces" in config:
                    return [
                        Path(ws).resolve() 
                        for ws in config["workspaces"]
                    ]
    
    # Priority 3: No config - allow all (with warning)
    import logging
    logging.warning(
        "No workspace configuration found. All paths allowed. "
        "For production, set GDAL_MCP_WORKSPACES or create gdal-mcp.yaml"
    )
    return []
```

### Path Validator

```python
# src/validation.py
from pathlib import Path
from fastmcp.exceptions import ToolError
from src.config import get_workspaces

def validate_path(path: str, workspaces: list[Path] | None = None) -> Path:
    """Validate path against allowed workspaces."""
    if workspaces is None:
        workspaces = get_workspaces()
    
    resolved = Path(path).resolve()
    
    # No restrictions if no workspaces configured
    if not workspaces:
        return resolved
    
    # Check each workspace
    for workspace in workspaces:
        try:
            resolved.relative_to(workspace)
            return resolved  # ✓ Allowed
        except ValueError:
            continue
    
    # ✗ Denied
    raise ToolError(
        f"Access denied: '{path}' is outside allowed workspaces.\n"
        f"Allowed directories:\n" +
        "\n".join(f"  - {ws}" for ws in workspaces) +
        "\n\nConfigure workspaces via GDAL_MCP_WORKSPACES environment variable."
    )
```

### Tool Integration

```python
# src/tools/raster/info.py
from src.validation import validate_path

async def _info(uri: str, band: int | None = None, ctx: Context | None = None):
    # Validate before any file access
    validated_path = validate_path(uri)
    
    if ctx:
        await ctx.info(f"📂 Opening raster: {validated_path}")
    
    with rasterio.open(str(validated_path)) as ds:
        ...
```

## Security Properties

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| **Path traversal** | Resolve symbolic links, normalize `..` |
| **Absolute paths** | Validate against workspace roots |
| **Relative paths** | Resolve to absolute before validation |
| **Symlinks** | `.resolve()` follows links to real path |
| **Race conditions** | Path validated at function entry |

### Attack Scenarios

**Scenario 1**: Attacker tries `../../etc/passwd`
```python
validate_path("../../etc/passwd", [Path("/data/projects")])
# Resolves to: /etc/passwd
# Check: /etc/passwd relative to /data/projects → ValueError
# Result: ToolError (Access denied)
```

**Scenario 2**: Attacker uses absolute path
```python
validate_path("/home/victim/private.tif", [Path("/data/projects")])
# Already absolute: /home/victim/private.tif
# Check: Not under /data/projects → ValueError
# Result: ToolError (Access denied)
```

**Scenario 3**: Attacker uses symlink
```python
# /data/projects/link -> /etc/passwd
validate_path("/data/projects/link", [Path("/data/projects")])
# Resolves to: /etc/passwd (via .resolve())
# Check: /etc/passwd relative to /data/projects → ValueError
# Result: ToolError (Access denied)
```

**Scenario 4**: Legitimate access
```python
validate_path("/data/projects/dem.tif", [Path("/data/projects")])
# Resolves to: /data/projects/dem.tif
# Check: /data/projects/dem.tif relative to /data/projects → Success
# Result: Path("/data/projects/dem.tif")
```

## Consequences

**Positive**:
- ✅ **Security**: Prevent unauthorized file access
- ✅ **Compliance**: Enforceable data boundaries
- ✅ **Multi-tenant**: Isolate user workspaces
- ✅ **Auditability**: Clear access control rules
- ✅ **Backward compatible**: No config = allow all
- ✅ **Flexible**: Env var or config file
- ✅ **MCP-aligned**: Can expose via roots capability

**Negative**:
- ⚠️ **Configuration complexity**: Users must configure workspaces
- ⚠️ **Error messages**: Users may be confused by access denials
- ⚠️ **Performance**: Path resolution on every file access (minimal ~microseconds)

**Neutral**:
- Development/testing works without config (allow all)
- Production deployments should always configure workspaces

## Alternatives Considered

**Alternative 1**: No validation (current state)
- ❌ Rejected: Security risk too high for production

**Alternative 2**: Client-side only (MCP roots)
- ❌ Rejected: Clients can't be trusted, server must enforce

**Alternative 3**: Whitelist specific files
- ❌ Rejected: Too restrictive, users work with dynamic datasets

**Alternative 4**: Chroot/containerization only
- ❌ Rejected: Defense in depth, not all deployments use containers

**Alternative 5**: Read-only mode
- ❌ Rejected: Tools need write access (convert, reproject)

## Migration Path

**Phase 1** (This ADR): Implement validation with opt-in
- Default: No restrictions (backward compatible)
- Warning logged when unrestricted

**Phase 2**: Documentation and examples
- Update README with workspace configuration
- Provide example configs for common scenarios
- Add to QUICKSTART.md

**Phase 3** (Future): Consider default restriction
- Require explicit configuration for production
- Default to CWD if no config (safer than allow-all)

## Related

- **MCP Specification**: Roots capability
- **ADR-0020**: Context-driven tool design (error messages via ToolError)
- **ADR-0021**: LLM-optimized descriptions (explain access errors to LLMs)

## References

- [MCP Roots Specification](https://modelcontextprotocol.io)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [12-Factor App: Config](https://12factor.net/config)

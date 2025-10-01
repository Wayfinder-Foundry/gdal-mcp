"""Path validation for workspace scoping and access control."""
from __future__ import annotations

from pathlib import Path

from fastmcp.exceptions import ToolError

from src.config import get_workspaces


def validate_path(path: str, workspaces: list[Path] | None = None) -> Path:
    """Validate path against allowed workspace directories.
    
    Ensures the resolved path is within one of the allowed workspaces.
    Handles:
    - Relative paths (resolved to absolute)
    - Path traversal (../ resolved)
    - Symbolic links (followed to real path)
    - Absolute paths (validated against workspaces)
    
    Args:
        path: User-provided path (relative or absolute)
        workspaces: Optional list of allowed workspaces (defaults to get_workspaces())
    
    Returns:
        Resolved absolute Path object if allowed
    
    Raises:
        ToolError: If path is outside all allowed workspaces
    
    Security:
        - Path is resolved to absolute (handles .., symlinks)
        - Validated against workspace roots
        - No path can escape workspace boundaries
    
    Examples:
        >>> # With workspaces configured
        >>> validate_path("/data/projects/dem.tif")  # ✓ Allowed
        PosixPath('/data/projects/dem.tif')
        
        >>> validate_path("../../etc/passwd")  # ✗ Denied
        ToolError: Access denied...
        
        >>> # Without workspaces (development mode)
        >>> validate_path("/any/path.tif")  # ✓ Allowed
        PosixPath('/any/path.tif')
    """
    if workspaces is None:
        workspaces = get_workspaces()
    
    # Resolve to absolute path (handles .., symlinks, relative paths)
    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError) as e:
        raise ToolError(
            f"Invalid path '{path}': {str(e)}"
        ) from e
    
    # If no workspaces configured, allow all paths (development mode)
    if not workspaces:
        return resolved
    
    # Check if path is within any allowed workspace
    for workspace in workspaces:
        try:
            # This will succeed only if resolved is within workspace
            resolved.relative_to(workspace)
            # Path is allowed - return it
            return resolved
        except ValueError:
            # Not in this workspace, try next
            continue
    
    # Path is outside all allowed workspaces - DENY
    workspace_list = "\n".join(f"  • {ws}" for ws in workspaces)
    raise ToolError(
        f"Access denied: Path '{path}' (resolves to '{resolved}') is outside allowed workspaces.\n\n"
        f"Allowed workspace directories:\n{workspace_list}\n\n"
        f"To allow this path, add its parent directory to GDAL_MCP_WORKSPACES:\n"
        f"  export GDAL_MCP_WORKSPACES=\"{':'.join(str(w) for w in workspaces)}:{resolved.parent}\"\n\n"
        f"See docs/ADR/0022-workspace-scoping-and-access-control.md for configuration details."
    )


def validate_output_path(path: str, workspaces: list[Path] | None = None) -> Path:
    """Validate output path for write operations.
    
    Similar to validate_path but also ensures parent directory exists
    or is creatable within workspace boundaries.
    
    Args:
        path: Output path for file creation
        workspaces: Optional list of allowed workspaces
    
    Returns:
        Resolved absolute Path object if allowed
    
    Raises:
        ToolError: If path is outside workspaces or parent doesn't exist
    """
    if workspaces is None:
        workspaces = get_workspaces()
    
    # First validate the path itself
    resolved = validate_path(path, workspaces)
    
    # Check if parent directory exists
    parent = resolved.parent
    if not parent.exists():
        # Check if parent is creatable (within workspace)
        if workspaces:
            # Validate parent directory is also within workspace
            try:
                validate_path(str(parent), workspaces)
            except ToolError:
                raise ToolError(
                    f"Cannot create output file '{path}': "
                    f"Parent directory '{parent}' does not exist and cannot be created "
                    f"(outside allowed workspaces)."
                )
        
        raise ToolError(
            f"Cannot create output file '{path}': "
            f"Parent directory '{parent}' does not exist. "
            f"Please create it first or specify an existing directory."
        )
    
    return resolved

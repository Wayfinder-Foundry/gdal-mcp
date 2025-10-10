"""Middleware for centralized path validation and access control."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

from src.config import get_workspaces

logger = logging.getLogger(__name__)


class PathValidationMiddleware(Middleware):
    """Middleware to validate file paths against allowed workspaces.

    Automatically validates path arguments for all tools, enforcing
    workspace boundaries without requiring explicit validation in each tool.

    Path arguments validated:
    - 'uri': Input file path (read operations)
    - 'path': Input file path (alternative naming)
    - 'output': Output file path (write operations)

    Benefits:
    - Single point of validation (DRY principle)
    - Consistent security enforcement across all tools
    - No tool can bypass validation
    - Easy to audit and maintain

    Example:
        >>> from fastmcp import FastMCP
        >>> from src.middleware import PathValidationMiddleware
        >>>
        >>> mcp = FastMCP("GDAL MCP")
        >>> mcp.add_middleware(PathValidationMiddleware())
    """

    # Arguments that represent input file paths (read operations)
    INPUT_PATH_ARGS = {"uri", "path", "file", "input"}

    # Arguments that represent output file paths (write operations)
    OUTPUT_PATH_ARGS = {"output", "destination", "dest", "target"}

    async def on_call_tool(
        self, context: MiddlewareContext, call_next: Any
    ) -> Any:
        """Intercept tool calls to validate path arguments.

        Args:
            context: Middleware context with tool call information
            call_next: Function to call the next middleware or tool

        Returns:
            Tool execution result if validation passes

        Raises:
            ToolError: If any path argument is outside allowed workspaces
        """
        tool_name = context.message.name
        arguments = context.message.arguments or {}

        logger.debug(f"PathValidationMiddleware: Checking tool '{tool_name}'")

        # Validate input paths (read operations)
        for arg_name in self.INPUT_PATH_ARGS:
            if arg_name in arguments:
                path_value = arguments[arg_name]
                if path_value:  # Skip empty/None values
                    try:
                        logger.debug(f"Validating input path '{arg_name}': {path_value}")
                        # This will raise ToolError if path is not allowed
                        validate_path(str(path_value))
                        logger.debug(f"✓ Input path '{path_value}' allowed")
                    except ToolError as e:
                        # Enhance error message with tool context
                        raise ToolError(f"Tool '{tool_name}' denied: {str(e)}") from e

        # Validate output paths (write operations)
        for arg_name in self.OUTPUT_PATH_ARGS:
            if arg_name in arguments:
                path_value = arguments[arg_name]
                if path_value:  # Skip empty/None values
                    try:
                        logger.debug(f"Validating output path '{arg_name}': {path_value}")
                        # Use output-specific validation (checks parent directory)
                        validate_output_path(str(path_value))
                        logger.debug(f"✓ Output path '{path_value}' allowed")
                    except ToolError as e:
                        # Enhance error message with tool context
                        raise ToolError(f"Tool '{tool_name}' denied: {str(e)}") from e

        # All paths validated - proceed with tool execution
        logger.debug(f"✓ All paths validated for '{tool_name}', executing tool")
        return await call_next(context)


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
        raise ToolError(f"Invalid path '{path}': {str(e)}") from e

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
    msg = (
        f"Access denied: Path '{path}' (resolves to '{resolved}') "
        f"is outside allowed workspaces.\n\n"
        f"Allowed workspace directories:\n{workspace_list}\n\n"
        f"To allow this path, add its parent directory to GDAL_MCP_WORKSPACES:\n"
        f'  export GDAL_MCP_WORKSPACES="{":".join(str(w) for w in workspaces)}:'
        f'{resolved.parent}"\n\n'
        f"See docs/ADR/0022-workspace-scoping-and-access-control.md for details."
    )
    raise ToolError(msg)


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
            except ToolError as e:
                msg = (
                    f"Cannot create output file '{path}': "
                    f"Parent directory '{parent}' does not exist and cannot be created "
                    f"(outside allowed workspaces)."
                )
                raise ToolError(msg) from e

        raise ToolError(
            f"Cannot create output file '{path}': "
            f"Parent directory '{parent}' does not exist. "
            f"Please create it first or specify an existing directory."
        )

    return resolved

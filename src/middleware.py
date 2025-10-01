"""Middleware for centralized path validation and access control."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

from src.validation import validate_path, validate_output_path

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

    async def on_call_tool(self, context: MiddlewareContext, call_next) -> Any:
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
                        logger.debug(
                            f"Validating input path '{arg_name}': {path_value}"
                        )
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
                        logger.debug(
                            f"Validating output path '{arg_name}': {path_value}"
                        )
                        # Use output-specific validation (checks parent directory)
                        validate_output_path(str(path_value))
                        logger.debug(f"✓ Output path '{path_value}' allowed")
                    except ToolError as e:
                        # Enhance error message with tool context
                        raise ToolError(f"Tool '{tool_name}' denied: {str(e)}") from e

        # All paths validated - proceed with tool execution
        logger.debug(f"✓ All paths validated for '{tool_name}', executing tool")
        return await call_next(context)

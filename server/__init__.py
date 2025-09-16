"""MCP Snippets.

This package contains simple examples of MCP server features.
Each server demonstrates a single feature and can be run as a standalone server.

To run a server, use the command:
    uv run server basic_tool sse
"""

import sys
import importlib

from typing import Literal, cast


def run_server():
    """Run a server by name with optional transport.

    Usage: server <server-name> [transport]
    Example: server basic_tool sse
    """
    if len(sys.argv) < 2:
        print("Usage: server <server-name> [transport]")
        print("Available servers: gdal_tools")
        print("Available transports: stdio (default), sse, streamable-http")
        sys.exit(1)

    server_name = sys.argv[1]
    transport = sys.argv[2] if len(sys.argv) > 2 else "stdio"

    try:
        if server_name == "gdal_tools":
            from . import gdal_tools
            gdal_tools.mcp.run(cast(Literal["stdio", "sse", "streamable-http"], transport))
        else:
            module = importlib.import_module(f".{server_name}", package=__name__)
            module.mcp.run(cast(Literal["stdio", "sse", "streamable-http"], transport))
    except ImportError:
        print(f"Error: Server '{server_name}' not found")
        sys.exit(1)


if __name__ == "__main__":  # Allow `python -m server basic_tool stdio`
    run_server()

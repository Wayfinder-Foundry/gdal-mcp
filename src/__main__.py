from __future__ import annotations

import logging
import typer
from .server import mcp

app = typer.Typer(add_completion=False, no_args_is_help=False)


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@app.callback(invoke_without_command=True)
def _default(
    ctx: typer.Context,
    transport: str = typer.Option(
        "stdio", "--transport", help="Transport: stdio or http"
    ),
    host: str = typer.Option("0.0.0.0", help="Host for HTTP transport"),
    port: int = typer.Option(8000, help="Port for HTTP transport"),
    log_level: str = typer.Option("INFO", help="Logging level"),
) -> None:
    """Default entry runs the server when no subcommand is provided."""
    if ctx.invoked_subcommand is not None:
        return
    _setup_logging(log_level)
    if transport == "stdio":
        mcp.run()
    elif transport == "http":
        mcp.run(transport="http", host=host, port=port)
    else:
        raise typer.BadParameter("transport must be 'stdio' or 'http'")


@app.command(help="Run the GDAL MCP server")
def serve(
    transport: str = typer.Option(
        "stdio", "--transport", help="Transport: stdio or http"
    ),
    host: str = typer.Option("0.0.0.0", help="Host for HTTP transport"),
    port: int = typer.Option(8000, help="Port for HTTP transport"),
    log_level: str = typer.Option("INFO", help="Logging level"),
) -> None:
    _setup_logging(log_level)
    if transport == "stdio":
        mcp.run()
    elif transport == "http":
        mcp.run(transport="http", host=host, port=port)
    else:
        raise typer.BadParameter("transport must be 'stdio' or 'http'")


def main() -> None:  # console_script entrypoint
    app()


if __name__ == "__main__":
    main()

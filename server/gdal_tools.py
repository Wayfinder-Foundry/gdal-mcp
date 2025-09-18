"""GDAL MCP Server and utility wrappers.

This module exposes:
- Simple Python wrappers around common GDAL CLI tools (gdalinfo, gdal_translate, gdalwarp, gdalbuildvrt)
- A Model Context Protocol (MCP) stdio server that publishes those tools

The implementation mirrors the structure of the provided STAC example while
staying focused on executing GDAL commands safely with helpful validation.
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import os
import shutil
from pathlib import Path
from typing import Any, Iterable, Optional

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .enums.format import Format
from .enums.resampling import Resampling

# ---------------- Logging -----------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------- Helpers -----------------

def _validate_file_path(path: str | Path) -> bool:
    """Return True if input looks like an accessible dataset.

    Accepts:
    - Local filesystem paths that exist
    - Remote/public URIs (http, https)
    - GDAL VSI/Cloud schemes (e.g., /vsicurl/, s3://, gs://, /vsis3/, /vsigs/)
    """
    s = str(path)
    # Remote URLs
    if s.startswith(("http://", "https://")):
        return True
    # Common GDAL virtual file systems and cloud schemes
    if s.startswith(("/vsicurl/", "/vsis3/", "/vsigs/", "/vsiaz/", "s3://", "gs://", "az://")):
        return True
    # Fallback to local file existence
    return Path(s).exists()


def _output_path(
    src: str | Path,
    *,
    suffix: str = "",
    extension: str | None = None,
) -> str:
    """Build an output path based on a source path with optional suffix and extension.

    - If extension is None, keep the source suffix; else replace with provided extension.
    """
    p = Path(src)
    stem = p.stem + (suffix or "")
    ext = extension if extension is not None else p.suffix
    if ext and not ext.startswith("."):
        ext = "." + ext
    return str(p.with_name(stem + (ext or "")))


def command(cmd: Iterable[str], timeout: float | int = 60) -> dict[str, Any]:
    """Run a subprocess command and return a structured result.

    Returns a dict with keys: success (bool), stdout (str), stderr (str), and optional error (str).
    """
    try:
        result = subprocess.run(
            list(cmd), capture_output=True, text=True, timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "", "error": "Command timed out"}
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "error": "Command not found",
        }
    except Exception as exc:  # safety net
        return {
            "success": False,
            "stdout": "",
            "stderr": str(exc),
            "error": "Execution failed",
        }


def _resolve_exe(name: str) -> str:
    """Resolve an executable name to an absolute path.

    Precedence:
    1. GDAL_BIN env var (prefix directory)
    2. shutil.which on current PATH
    3. Fallback to the name as-is
    """
    base = name
    gdal_bin = os.environ.get("GDAL_BIN")
    if gdal_bin:
        candidate = Path(gdal_bin) / base
        if candidate.exists():  # noqa: PTH110
            return str(candidate)
    found = shutil.which(base)
    return found or base


# ------------- High-level wrappers -------------

def check_gdal_installation() -> str:
    """Check that GDAL is installed and reachable on PATH.

    Returns a human-friendly message.
    """
    res = command([_resolve_exe("gdalinfo"), "--version"])  # type: ignore[list-item]
    if res.get("success"):
        version = res.get("stdout", "").strip()
        return f"GDAL is installed: {version}"
    return "Error: GDAL not installed or not in PATH"


def list_gdal_formats() -> str:
    """Return the output of `gdalinfo --formats` as a string."""
    res = command([_resolve_exe("gdalinfo"), "--formats"])  # type: ignore[list-item]
    if res.get("success"):
        return res.get("stdout", "")
    err = res.get("error") or res.get("stderr") or "Unknown error"
    return f"Error: {err}"


def gdalinfo(
    dataset: str,
    *,
    json_output: bool = False,
    stats: bool = False,
    extra_args: Optional[list[str]] = None,
) -> str:
    """Run gdalinfo and return its stdout or an error string.

    Parameters align with the MCP tool's input schema.
    """
    if not _validate_file_path(dataset):
        return "Error: Dataset not found"
    cmd: list[str] = [_resolve_exe("gdalinfo")]
    if json_output:
        cmd.append("-json")
    if stats:
        cmd.append("-stats")
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(dataset)
    res = command(cmd)
    if res.get("success"):
        return res.get("stdout", "")
    return f"Error: {res.get('error') or res.get('stderr') or 'gdalinfo failed'}"


def gdal_translate(
    src_dataset: str,
    dst_dataset: Optional[str] = None,
    *,
    output_format: Optional[str] = None,
    bands: Optional[list[int]] = None,
    extra_args: Optional[list[str]] = None,
) -> str:
    """Run gdal_translate to convert a dataset.

    - Validates output format if provided using a small whitelist.
    - Creates a default destination path if not supplied.
    """
    if not _validate_file_path(src_dataset):
        return "Error: Source dataset not found"

    if output_format and not Format.supported(output_format):
        return f"Invalid output format: {output_format}"

    if dst_dataset is None:
        # Default extension based on format hint
        ext = ".tif" if (output_format or "").lower() in {"gtiff", "gtif", "gtiff"} or output_format == "GTiff" else None
        dst_dataset = _output_path(src_dataset, suffix="_converted", extension=ext)

    cmd: list[str] = [_resolve_exe("gdal_translate")]
    if output_format:
        cmd += ["-of", output_format]
    if bands:
        for b in bands:
            cmd += ["-b", str(int(b))]
    if extra_args:
        cmd.extend(extra_args)
    cmd += [src_dataset, dst_dataset]
    res = command(cmd)
    if res.get("success"):
        return f"Successfully converted {src_dataset} -> {dst_dataset}"
    return f"Error: {res.get('error') or res.get('stderr') or 'gdal_translate failed'}"


def gdalwarp(
    src_datasets: list[str],
    dst_dataset: Optional[str] = None,
    *,
    target_epsg: Optional[int] = None,
    resampling: Optional[str] = None,
    extra_args: Optional[list[str]] = None,
) -> str:
    """Run gdalwarp to reproject/warp datasets.

    - Validates resampling method against known options.
    - Creates a default output path when not provided.
    """
    if not src_datasets:
        return "Error: No source datasets provided"
    if not all(_validate_file_path(p) for p in src_datasets):
        return "Error: One or more source datasets not found"

    if resampling and not Resampling.exists(resampling):
        return f"Invalid resampling: {resampling}"

    if dst_dataset is None:
        dst_dataset = _output_path(src_datasets[0], suffix="_warped", extension=None)

    cmd: list[str] = [_resolve_exe("gdalwarp")]
    if target_epsg:
        cmd += ["-t_srs", f"EPSG:{int(target_epsg)}"]
    if resampling:
        cmd += ["-r", resampling]
    if extra_args:
        cmd.extend(extra_args)
    cmd += src_datasets + [dst_dataset]
    res = command(cmd)
    if res.get("success"):
        return f"Successfully warped {len(src_datasets)} file(s) -> {dst_dataset}"
    return f"Error: {res.get('error') or res.get('stderr') or 'gdalwarp failed'}"


def gdalbuildvrt(
    source_files: list[str],
    dst_vrt: Optional[str] = None,
    *,
    resolution: Optional[str] = None,
    extra_args: Optional[list[str]] = None,
) -> str:
    """Run gdalbuildvrt to build a VRT from sources."""
    if not source_files:
        return "Error: No source datasets provided"
    if not all(_validate_file_path(p) for p in source_files):
        return "Error: One or more source datasets not found"

    if dst_vrt is None:
        dst_vrt = _output_path(source_files[0], suffix="_mosaic", extension=".vrt")

    cmd: list[str] = [_resolve_exe("gdalbuildvrt")]
    if resolution:
        cmd += ["-resolution", resolution]
    if extra_args:
        cmd.extend(extra_args)
    cmd += [dst_vrt] + list(source_files)
    res = command(cmd)
    if res.get("success"):
        return f"Successfully created VRT -> {dst_vrt}"
    return f"Error: {res.get('error') or res.get('stderr') or 'gdalbuildvrt failed'}"


# ---------------- MCP Server wiring ----------------

# Initialize the MCP server
server = Server("gdal-mcp")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available GDAL tools with their input schemas."""
    return [
        Tool(
            name="gdalinfo",
            description="Get metadata information about a raster dataset using gdalinfo",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset": {"type": "string", "description": "Path to dataset"},
                    "json_output": {"type": "boolean", "default": False},
                    "stats": {"type": "boolean", "default": False},
                },
                "required": ["dataset"],
            },
        ),
        Tool(
            name="gdal_translate",
            description="Convert a raster dataset using gdal_translate",
            inputSchema={
                "type": "object",
                "properties": {
                    "src_dataset": {"type": "string", "description": "Source path"},
                    "dst_dataset": {"type": "string", "description": "Destination path (optional)"},
                    "output_format": {
                        "type": "string",
                        "description": f"Output format (e.g., {', '.join(Format.all())})",
                    },
                    "bands": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Optional list of band indices (1-based)",
                    },
                },
                "required": ["src_dataset"],
            },
        ),
        Tool(
            name="gdalwarp",
            description="Reproject or warp raster(s) using gdalwarp",
            inputSchema={
                "type": "object",
                "properties": {
                    "src_datasets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Source dataset paths",
                    },
                    "dst_dataset": {"type": "string", "description": "Destination path (optional)"},
                    "target_epsg": {"type": "integer", "description": "Target EPSG code"},
                    "resampling": {
                        "type": "string",
                        "description": f"Resampling method ({', '.join(Resampling.all())})",
                    },
                },
                "required": ["src_datasets"],
            },
        ),
        Tool(
            name="gdalbuildvrt",
            description="Create a VRT from multiple rasters using gdalbuildvrt",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Source raster paths",
                    },
                    "dst_vrt": {"type": "string", "description": "Destination VRT path (optional)"},
                    "resolution": {"type": "string", "description": "Resolution strategy (e.g., average)"},
                },
                "required": ["source_files"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(tool_name: str, arguments: dict):
    """Dispatch tool calls to the appropriate wrapper and return textual output."""
    try:
        if tool_name == "gdalinfo":
            text = gdalinfo(
                dataset=arguments["dataset"],
                json_output=arguments.get("json_output", False),
                stats=arguments.get("stats", False),
            )
            return [TextContent(type="text", text=text)]

        if tool_name == "gdal_translate":
            text = gdal_translate(
                src_dataset=arguments["src_dataset"],
                dst_dataset=arguments.get("dst_dataset"),
                output_format=arguments.get("output_format"),
                bands=arguments.get("bands"),
            )
            return [TextContent(type="text", text=text)]

        if tool_name == "gdalwarp":
            text = gdalwarp(
                src_datasets=arguments["src_datasets"],
                dst_dataset=arguments.get("dst_dataset"),
                target_epsg=arguments.get("target_epsg"),
                resampling=arguments.get("resampling"),
            )
            return [TextContent(type="text", text=text)]

        if tool_name == "gdalbuildvrt":
            text = gdalbuildvrt(
                source_files=arguments["source_files"],
                dst_vrt=arguments.get("dst_vrt"),
                resolution=arguments.get("resolution"),
            )
            return [TextContent(type="text", text=text)]

        raise ValueError(f"Unknown tool: {tool_name}")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise


async def main() -> None:
    """Main entry point for the GDAL MCP server (stdio transport)."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gdal-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def cli_main() -> None:
    """CLI entry point to run the GDAL MCP server."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
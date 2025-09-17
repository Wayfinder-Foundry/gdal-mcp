"""GDAL Tools for MCP Server.

This module provides GDAL command-line tools as MCP tools for AI agents.
"""

import os
import sys
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Literal, cast, Union, Tuple

from server.enums.resampling import Resampling
from server.enums.format import Format

# TODO: remove stateless_http=True if stateful sessions are needed
mcp = FastMCP(name="GDAL Tools", json_response=True, stateless_http=True)


def _validate_file_path(path: Union[str, Path]) -> bool:
    """Validate that the file path exists and is readable."""
    try:
        path_obj = Path(path)
        return path_obj.exists() and path_obj.is_file() and os.access(path_obj, os.R_OK)
    except Exception:
        return False


def _output_path(path: Union[str, Path], suffix: str = "", extension: str = None) -> str:
    """Generate an output file path based on input path."""
    input_path_obj = Path(path)
    if extension:
        new_extension = extension
    else:
        new_extension = input_path_obj.suffix
    
    output_name = f"{input_path_obj.stem}{suffix}{new_extension}"
    return str(input_path_obj.parent / output_name)


def command(cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
    """Run a GDAL command and return the result.
    
    Args:
        cmd: Command and arguments as a list
        timeout: Timeout in seconds
        
    Returns:
        Dictionary containing command result
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        else:
            return {
                "success": False,
                "error": f"Command failed: {result.stderr}",
                "stdout": result.stdout,
                "return_code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Command not found: {cmd[0]}. Please ensure GDAL is installed."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


@mcp.tool()
def gdalinfo(dataset: str, json_output: bool = False, stats: bool = False) -> str:
    """Get information about a raster dataset using gdalinfo.
    
    This tool provides summary information about a raster dataset including:
    - File format and size
    - Coordinate system and geolocation
    - Band information
    - Metadata
    - Optionally, band statistics
    
    Args:
        dataset: Path to the raster dataset file
        json_output: Return output in JSON format (default: False)
        stats: Compute and include raster band statistics (default: False)
        
    Returns:
        String containing the gdalinfo output or error message
    """
    if not _validate_file_path(dataset):
        return f"Error: File not found or not readable: {dataset}"
    
    cmd = ["gdalinfo"]
    
    if json_output:
        cmd.append("-json")
    
    if stats:
        cmd.append("-stats")
    
    cmd.append(dataset)
    
    result = command(cmd)
    
    if result["success"]:
        return result["stdout"]
    else:
        return f"Error: {result['error']}"


@mcp.tool()
def gdal_translate(
    src_dataset: str,
    dst_dataset: str = "",
    output_format: str = Format.GTIFF,
    bands: List[int] = None,
    scale_min: float = None,
    scale_max: float = None,
    output_type: str = None
) -> str:
    """Convert raster data between formats using gdal_translate.
    
    This tool converts raster data between different formats and can also:
    - Subset specific bands
    - Rescale pixel values
    - Change output data type
    - Compress output files
    
    Args:
        src_dataset: Path to source raster dataset
        dst_dataset: Path to output dataset (auto-generated if empty)
        output_format: GDAL output format (default: GTiff)
        bands: List of band numbers to copy (1-based indexing)
        scale_min: Minimum value for scaling
        scale_max: Maximum value for scaling
        output_type: Output data type (Byte, UInt16, Int16, UInt32, Int32, Float32, Float64)
        
    Returns:
        String containing the result path or error message
    """
    if not _validate_file_path(src_dataset):
        return f"Error: Source file not found or not readable: {src_dataset}"
    
    # Validate output format
    if not Format.supported(output_format):
        return f"Error: Invalid output format '{output_format}'. Valid options: {', '.join(Format.all())}"
    
    # Generate output path if not provided
    if not dst_dataset:
        format_extensions = {
            "GTiff": ".tif",
            "JPEG": ".jpg",
            "PNG": ".png",
            "HFA": ".img",
            "ENVI": ".dat"
        }
        ext = format_extensions.get(output_format, ".tif")
        dst_dataset = _output_path(src_dataset, "_converted", ext)
    
    cmd = ["gdal_translate"]
    
    # Add format option
    cmd.extend(["-of", output_format])
    
    # Add band selection
    if bands:
        for band in bands:
            cmd.extend(["-b", str(band)])
    
    # Add scaling options
    if scale_min is not None and scale_max is not None:
        cmd.extend(["-scale", str(scale_min), str(scale_max)])
    
    # Add output type
    if output_type:
        cmd.extend(["-ot", output_type])
    
    # Add source and destination
    cmd.extend([src_dataset, dst_dataset])
    
    result = command(cmd, timeout=120)
    
    if result["success"]:
        return f"Successfully converted to: {dst_dataset}"
    else:
        return f"Error: {result['error']}"


@mcp.tool()
def gdalwarp(
    src_datasets: List[Union[str, Path]],
    dst_dataset: str = "",
    target_epsg: int = 4326,
    resampling: str = Resampling.NEAREST,
    output_format: str = Format.GTIFF,
    overwrite: bool = False
) -> str:
    """Reproject and warp raster images using gdalwarp.
    
    This tool reprojects raster images and can:
    - Change coordinate system
    - Mosaic multiple inputs
    - Apply different resampling algorithms
    - Crop to specific extents
    
    Args:
        src_datasets: List of source raster dataset paths
        dst_dataset: Path to output dataset (auto-generated if empty)
        target_epsg: Target EPSG code for spatial reference system (default: 4326)
        resampling: Resampling algorithm (near, bilinear, cubic, etc.)
        output_format: GDAL output format (default: GTiff)
        overwrite: Overwrite existing output file
        
    Returns:
        String containing the result path or error message
    """
    if not src_datasets:
        return "Error: No source datasets provided"
    
    # Validate all source files
    for src in src_datasets:
        if not _validate_file_path(src):
            return f"Error: Source file not found or not readable: {src}"
    
    # Validate resampling method
    if not Resampling.exists(resampling):
        return f"Error: Invalid resampling method '{resampling}'. Valid options: {', '.join(Resampling.all())}"
    
    # Validate output format
    if not Format.supported(output_format):
        return f"Error: Invalid output format '{output_format}'. Valid options: {', '.join(Format.all())}"
    
    # Generate output path if not provided
    if not dst_dataset:
        base_name = Path(src_datasets[0]).stem
        dst_dataset = _output_path(src_datasets[0], f"_warped_EPSG_{target_epsg}", ".tif")
    
    # Build target SRS from EPSG code
    target_srs = f"EPSG:{target_epsg}"
    
    cmd = ["gdalwarp"]
    
    # Add options
    cmd.extend(["-t_srs", target_srs])
    cmd.extend(["-r", resampling])
    cmd.extend(["-of", output_format])
    
    if overwrite:
        cmd.append("-overwrite")
    
    # Add all source files and destination
    cmd.extend(src_datasets)
    cmd.append(dst_dataset)
    
    result = command(cmd, timeout=180)
    
    if result["success"]:
        return f"Successfully warped to: {dst_dataset}"
    else:
        return f"Error: {result['error']}"


@mcp.tool()
def gdalbuildvrt(
    src_datasets: List[Union[str, Path]],
    dst_vrt: str = "",
    resolution: str = "average",
    separate: bool = False
) -> str:
    """Build a virtual dataset (VRT) from input rasters using gdalbuildvrt.
    
    This tool creates a virtual mosaic that combines multiple raster files:
    - Creates lightweight VRT files
    - Handles different resolutions
    - Can separate bands or mosaic them
    
    Args:
        src_datasets: List of source raster dataset paths
        dst_vrt: Path to output VRT file (auto-generated if empty)
        resolution: Output resolution (highest, lowest, average)
        separate: Place each input file into separate VRT bands
        
    Returns:
        String containing the result path or error message
    """
    if not src_datasets:
        return "Error: No source datasets provided"
    
    # Validate all source files
    for src in src_datasets:
        if not _validate_file_path(src):
            return f"Error: Source file not found or not readable: {src}"
    
    # Generate output path if not provided
    if not dst_vrt:
        dst_vrt = _output_path(src_datasets[0], "_mosaic", ".vrt")
    
    cmd = ["gdalbuildvrt"]
    
    # Add options
    cmd.extend(["-resolution", resolution])
    
    if separate:
        cmd.append("-separate")
    
    # Add destination and all sources
    cmd.append(dst_vrt)
    cmd.extend(src_datasets)
    
    result = command(cmd)
    
    if result["success"]:
        return f"Successfully created VRT: {dst_vrt}"
    else:
        return f"Error: {result['error']}"


@mcp.tool()
def check_gdal_installation() -> str:
    """Check if GDAL is properly installed and accessible."""
    try:
        result = subprocess.run(
            ["gdalinfo", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        
        if result.returncode == 0:
            version_info = result.stdout.strip()
            
            # Also check for common GDAL utilities
            utilities = ["gdal_translate", "gdalwarp", "gdalbuildvrt"]
            available_utils = []
            
            for util in utilities:
                try:
                    subprocess.run([util, "--help"], capture_output=True, timeout=5, check=False)
                    available_utils.append(util)
                except:
                    pass
            
            return f"GDAL is installed: {version_info}\nAvailable utilities: {', '.join(available_utils)}"
        else:
            return f"GDAL command failed: {result.stderr}"
            
    except FileNotFoundError:
        return "GDAL is not installed or not in PATH. Please install GDAL."
    except Exception as e:
        return f"Error checking GDAL installation: {str(e)}"


@mcp.tool()
def list_gdal_formats() -> str:
    """List all supported GDAL formats."""
    try:
        result = subprocess.run(
            ["gdalinfo", "--formats"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error getting formats: {result.stderr}"
            
    except Exception as e:
        return f"Error: {str(e)}"


def run_server():
    """Entry point for console script to run GDAL MCP server.

    Uses stdio transport by default. Optionally allow a transport argument
    (stdio, sse, streamable-http) for flexibility, mirroring pattern in
    `server.__init__.run_server` but specialized for this single server.
    """

    allowed: List[str] = ["stdio", "sse", "streamable-http"]
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("-h", "--help"):
            print("Usage: gdal-mcp-server [transport]\n")
            print("Run the GDAL MCP server exposing GDAL tools as MCP tools.")
            print("Optional transport (default stdio): stdio | sse | streamable-http")
            return 0
        if arg not in allowed:
            print(f"Unknown transport '{arg}'. Allowed: {', '.join(allowed)}")
            return 1
        transport = arg
    else:
        transport = "stdio"

    mcp.run(cast(Literal["stdio", "sse", "streamable-http"], transport))


if __name__ == "__main__":  # Allow `python -m server.gdal_tools`
    run_server()
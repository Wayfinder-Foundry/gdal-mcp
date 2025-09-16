"""GDAL Info Tool for MCP Server.

This module provides a basic gdalinfo tool that wraps the gdalinfo command-line utility.
"""

import os
import subprocess

from pathlib import Path
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="GDAL Info Tool")


def validate_file_path(file_path: str) -> bool:
    """Validate that the file path exists and is readable."""
    try:
        path = Path(file_path)
        return path.exists() and path.is_file() and os.access(path, os.R_OK)
    except Exception:
        return False


def run_gdalinfo(dataset: str, json_output: bool = False, stats: bool = False) -> Dict[str, Any]:
    """Run gdalinfo command and return the result.
    
    Args:
        dataset: Path to the raster dataset
        json_output: Return output in JSON format
        stats: Compute and include raster band statistics
        
    Returns:
        Dictionary containing the gdalinfo output or error information
    """
    if not validate_file_path(dataset):
        return {
            "error": f"File not found or not readable: {dataset}",
            "success": False
        }
    
    # Build the gdalinfo command
    cmd = ["gdalinfo"]
    
    if json_output:
        cmd.append("-json")
    
    if stats:
        cmd.append("-stats")
    
    cmd.append(dataset)
    
    try:
        # Run the command with timeout and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            check=False
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout,
                "format": "json" if json_output else "text"
            }
        else:
            return {
                "success": False,
                "error": f"gdalinfo failed: {result.stderr}",
                "return_code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "gdalinfo command timed out after 30 seconds"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "gdalinfo command not found. Please ensure GDAL is installed and in PATH."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error running gdalinfo: {str(e)}"
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
    result = run_gdalinfo(dataset, json_output, stats)
    
    if result["success"]:
        return result["output"]
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
            return f"GDAL is installed: {result.stdout.strip()}"
        else:
            return f"GDAL command failed: {result.stderr}"
            
    except FileNotFoundError:
        return "GDAL is not installed or not in PATH. Please install GDAL."
    except Exception as e:
        return f"Error checking GDAL installation: {str(e)}"
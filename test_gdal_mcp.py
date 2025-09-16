#!/usr/bin/env python3
"""Test script for GDAL MCP server.

This script demonstrates how to use the GDAL MCP tools manually.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from gdal_tools import (
    check_gdal_installation,
    gdalinfo,
    gdal_translate,
    gdalwarp,
    gdalbuildvrt,
    list_gdal_formats
)

def test_basic_functionality():
    """Test basic GDAL functionality."""
    print("=== GDAL MCP Tools Test ===\n")
    
    # Test 1: Check GDAL installation
    print("1. Checking GDAL installation:")
    result = check_gdal_installation()
    print(result)
    print()
    
    # Test 2: List GDAL formats
    print("2. Available GDAL formats (first 10 lines):")
    formats = list_gdal_formats()
    print('\n'.join(formats.split('\n')[:10]))
    print()
    
    # Test 3: gdalinfo on sample file
    print("3. Testing gdalinfo on sample.tif:")
    if os.path.exists("test_data/sample.tif"):
        info = gdalinfo("test_data/sample.tif", json_output=False, stats=False)
        # Print first few lines
        lines = info.split('\n')[:15]
        print('\n'.join(lines))
    else:
        print("Sample file not found. Creating one...")
        os.system("mkdir -p test_data && gdal_create -of GTiff -ot Byte -bands 3 -outsize 360 180 -a_srs EPSG:4326 -a_ullr -180 90 180 -90 test_data/sample.tif")
        info = gdalinfo("test_data/sample.tif", json_output=False, stats=False)
        lines = info.split('\n')[:15]
        print('\n'.join(lines))
    print()
    
    # Test 4: gdal_translate
    print("4. Testing gdal_translate:")
    if os.path.exists("test_data/sample.tif"):
        result = gdal_translate(
            "test_data/sample.tif",
            "test_data/sample_single_band.tif",
            output_format="GTiff",
            bands=[1]
        )
        print(result)
        
        # Verify the result
        if os.path.exists("test_data/sample_single_band.tif"):
            info = gdalinfo("test_data/sample_single_band.tif")
            band_count = len([line for line in info.split('\n') if 'Band ' in line and 'Block=' in line])
            print(f"Converted file has {band_count} band(s)")
    print()
    
    # Test 5: gdalwarp
    print("5. Testing gdalwarp:")
    if os.path.exists("test_data/sample.tif"):
        result = gdalwarp(
            ["test_data/sample.tif"],
            "test_data/sample_reprojected.tif",
            target_epsg=3857,
            resampling="bilinear"
        )
        print(result)
    print()
    
    # Test 6: gdalbuildvrt
    print("6. Testing gdalbuildvrt:")
    source_files = []
    for f in ["sample.tif", "sample_single_band.tif"]:
        if os.path.exists(f"test_data/{f}"):
            source_files.append(f"test_data/{f}")
    
    if len(source_files) >= 2:
        result = gdalbuildvrt(
            source_files,
            "test_data/mosaic.vrt",
            resolution="average"
        )
        print(result)
    else:
        print("Not enough source files for VRT test")
    print()
    
    print("=== Test Summary ===")
    test_files = [
        "test_data/sample.tif",
        "test_data/sample_single_band.tif", 
        "test_data/sample_reprojected.tif",
        "test_data/mosaic.vrt"
    ]
    
    for f in test_files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            print(f"✓ {f} ({size:,} bytes)")
        else:
            print(f"✗ {f} (not created)")


if __name__ == "__main__":
    test_basic_functionality()
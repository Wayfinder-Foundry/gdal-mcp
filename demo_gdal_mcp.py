#!/usr/bin/env python3
"""Interactive demo of GDAL MCP tools.

This script demonstrates the GDAL MCP tools in action and can be used
to test the functionality before integrating with MCP clients.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from gdal_tools import (
    check_gdal_installation,
    gdalinfo,
    gdal_translate,
    gdalwarp,
    gdalbuildvrt,
    list_gdal_formats
)


def print_separator(title=""):
    """Print a visual separator."""
    print("\n" + "="*60)
    if title:
        print(f" {title} ")
        print("="*60)
    print()


def demo_gdalinfo():
    """Demo gdalinfo functionality."""
    print_separator("GDALINFO DEMO")
    
    # Test with our sample file
    if os.path.exists("test_data/sample.tif"):
        print("📊 Getting information about sample.tif:")
        print()
        
        # Regular output
        info = gdalinfo("test_data/sample.tif", json_output=False, stats=False)
        print(info)
        
        print("\n" + "-"*50)
        print("🔢 Getting statistics:")
        print()
        
        # With statistics
        info_stats = gdalinfo("test_data/sample.tif", json_output=False, stats=True)
        # Show just the statistics lines
        lines = info_stats.split('\n')
        for line in lines:
            if 'Minimum=' in line or 'Maximum=' in line or 'Mean=' in line or 'StdDev=' in line:
                print(line.strip())
    else:
        print("❌ Sample file not found. Please run test_gdal_mcp.py first.")


def demo_gdal_translate():
    """Demo gdal_translate functionality."""
    print_separator("GDAL_TRANSLATE DEMO")
    
    if not os.path.exists("test_data/sample.tif"):
        print("❌ Sample file not found. Please run test_gdal_mcp.py first.")
        return
    
    print("🔄 Converting multi-band raster to single band:")
    
    # Convert to single band
    result = gdal_translate(
        src_dataset="test_data/sample.tif",
        dst_dataset="test_data/demo_red_band.tif",
        output_format="GTiff",
        bands=[1],  # Red band only
        output_type="Byte"
    )
    print(f"Result: {result}")
    
    if os.path.exists("test_data/demo_red_band.tif"):
        print("\n📊 Verifying conversion:")
        info = gdalinfo("test_data/demo_red_band.tif")
        lines = info.split('\n')
        for line in lines:
            if 'Size is' in line or 'Band ' in line:
                print(f"  {line.strip()}")
    
    print("\n🔄 Converting to JPEG format:")
    result = gdal_translate(
        src_dataset="test_data/sample.tif",
        dst_dataset="test_data/demo_preview.jpg",
        output_format="JPEG",
        bands=[1, 2, 3]  # RGB bands
    )
    print(f"Result: {result}")


def demo_gdalwarp():
    """Demo gdalwarp functionality."""
    print_separator("GDALWARP DEMO")
    
    if not os.path.exists("test_data/sample.tif"):
        print("❌ Sample file not found. Please run test_gdal_mcp.py first.")
        return
    
    print("🌍 Reprojecting from Geographic (EPSG:4326) to Web Mercator (EPSG:3857):")
    
    result = gdalwarp(
        src_datasets=["test_data/sample.tif"],
        dst_dataset="test_data/demo_webmercator.tif",
        target_srs="EPSG:3857",
        resampling="bilinear",
        output_format="GTiff"
    )
    print(f"Result: {result}")
    
    if os.path.exists("test_data/demo_webmercator.tif"):
        print("\n📊 Comparing coordinate systems:")
        print("\nOriginal file:")
        info_orig = gdalinfo("test_data/sample.tif")
        for line in info_orig.split('\n'):
            if 'GEOGCRS' in line or 'ID["EPSG"' in line:
                print(f"  {line.strip()}")
                break
        
        print("\nReprojected file:")
        info_proj = gdalinfo("test_data/demo_webmercator.tif")
        for line in info_proj.split('\n'):
            if 'PROJCRS' in line or 'ID["EPSG"' in line:
                print(f"  {line.strip()}")
                break


def demo_gdalbuildvrt():
    """Demo gdalbuildvrt functionality."""
    print_separator("GDALBUILDVRT DEMO")
    
    # Create some test files first if they don't exist
    files = []
    base_files = ["sample.tif", "demo_red_band.tif"]
    
    for f in base_files:
        if os.path.exists(f"test_data/{f}"):
            files.append(f"test_data/{f}")
    
    if len(files) < 2:
        print("❌ Need at least 2 raster files. Please run other demos first.")
        return
    
    print(f"📂 Creating VRT from {len(files)} files:")
    for f in files:
        print(f"  - {f}")
    print()
    
    result = gdalbuildvrt(
        src_datasets=files,
        dst_vrt="test_data/demo_mosaic.vrt",
        resolution="average",
        separate=False
    )
    print(f"Result: {result}")
    
    if os.path.exists("test_data/demo_mosaic.vrt"):
        print("\n📊 VRT file contents:")
        with open("test_data/demo_mosaic.vrt", 'r') as f:
            content = f.read()
            # Show first few lines
            lines = content.split('\n')[:15]
            for line in lines:
                if line.strip():
                    print(f"  {line}")
            if len(content.split('\n')) > 15:
                print("  ...")


def demo_formats():
    """Demo format listing."""
    print_separator("SUPPORTED FORMATS")
    
    print("📋 GDAL supported formats (showing first 20):")
    print()
    
    formats = list_gdal_formats()
    lines = formats.split('\n')
    
    for i, line in enumerate(lines[:20]):
        if line.strip() and not line.startswith('Supported Formats:'):
            print(f"  {line}")
    
    print(f"\n... and {len(lines) - 22} more formats")


def main():
    """Run the interactive demo."""
    print("🌍 GDAL MCP Tools Interactive Demo")
    print("=====================================")
    
    # Check GDAL installation first
    print("\n🔧 Checking GDAL installation:")
    install_check = check_gdal_installation()
    print(install_check)
    
    if "not installed" in install_check:
        print("❌ GDAL is not available. Please install GDAL first.")
        return
    
    # Ensure test data exists
    if not os.path.exists("test_data/sample.tif"):
        print("\n📁 Creating sample test data...")
        os.makedirs("test_data", exist_ok=True)
        os.system("gdal_create -of GTiff -ot Byte -bands 3 -outsize 360 180 -a_srs EPSG:4326 -a_ullr -180 90 180 -90 test_data/sample.tif")
        print("✅ Sample data created.")
    
    # Run demos
    demos = [
        ("View raster information", demo_gdalinfo),
        ("Convert raster formats", demo_gdal_translate),
        ("Reproject rasters", demo_gdalwarp),
        ("Create virtual mosaics", demo_gdalbuildvrt),
        ("List supported formats", demo_formats)
    ]
    
    while True:
        print_separator("DEMO MENU")
        print("Choose a demo to run:")
        print()
        
        for i, (name, _) in enumerate(demos, 1):
            print(f"  {i}. {name}")
        
        print(f"  0. Exit")
        print()
        
        try:
            choice = input("Enter your choice (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 Thanks for trying GDAL MCP tools!")
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(demos):
                demos[int(choice) - 1][1]()
                input("\n⏸️  Press Enter to continue...")
            else:
                print("❌ Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
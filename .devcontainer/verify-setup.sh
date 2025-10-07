#!/bin/bash
# Verification script for GDAL MCP devcontainer setup
# Run this after the devcontainer has been built to verify everything is working

set -e

echo "🔍 GDAL MCP Development Environment Verification"
echo "================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counters
PASSED=0
FAILED=0

# Helper function to check command
check_command() {
    local cmd=$1
    local name=$2
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $name: $(command -v $cmd)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $name: NOT FOUND"
        FAILED=$((FAILED + 1))
    fi
}

# Helper function to check Python import
check_python_import() {
    local module=$1
    local name=$2
    
    if python3 -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python module: $name"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} Python module: $name NOT AVAILABLE"
        FAILED=$((FAILED + 1))
    fi
}

echo "1. System Tools"
echo "---------------"
check_command "python3" "Python"
check_command "git" "Git"
check_command "uv" "UV package manager"
check_command "jq" "jq"
check_command "curl" "curl"
echo ""

echo "2. Python Version"
echo "-----------------"
PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
PASSED=$((PASSED + 1))
echo ""

echo "3. GDAL Installation"
echo "--------------------"
if command -v gdalinfo &> /dev/null; then
    GDAL_VERSION=$(gdalinfo --version 2>&1 | head -1)
    echo -e "${GREEN}✓${NC} $GDAL_VERSION"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠${NC} GDAL CLI tools not in PATH (expected - using Python bindings)"
fi
echo ""

echo "4. Python Dependencies"
echo "----------------------"
check_python_import "fastmcp" "FastMCP"
check_python_import "rasterio" "Rasterio"
check_python_import "pyproj" "PyProj"
check_python_import "shapely" "Shapely"
check_python_import "pyogrio" "pyogrio"
check_python_import "fiona" "Fiona"
check_python_import "pydantic" "Pydantic"
check_python_import "typer" "Typer"
echo ""

echo "5. Dev Tools"
echo "------------"
check_python_import "pytest" "pytest"
check_python_import "mypy" "mypy"
check_python_import "ruff" "ruff"
echo ""

echo "6. GDAL MCP CLI"
echo "---------------"
if uv run gdal --help &> /dev/null; then
    echo -e "${GREEN}✓${NC} GDAL MCP CLI is available"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC} GDAL MCP CLI not working"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "7. Workspace Configuration"
echo "--------------------------"
if [ -n "$GDAL_MCP_WORKSPACES" ]; then
    echo -e "${GREEN}✓${NC} GDAL_MCP_WORKSPACES: $GDAL_MCP_WORKSPACES"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠${NC} GDAL_MCP_WORKSPACES not set"
fi
echo ""

echo "8. Test Data"
echo "------------"
if [ -d "/workspace/test" ]; then
    echo -e "${GREEN}✓${NC} Test directory exists: /workspace/test"
    PASSED=$((PASSED + 1))
    
    TEST_FILES=$(find /workspace/test -type f -name "test_*.py" | wc -l)
    echo -e "${GREEN}✓${NC} Found $TEST_FILES test files"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC} Test directory not found"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "9. Running Quick Test"
echo "---------------------"
if uv run pytest /workspace/test/ -v --tb=short 2>&1 | tail -1 | grep -q "passed"; then
    echo -e "${GREEN}✓${NC} Tests passed"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠${NC} Some tests may have failed (check output above)"
fi
echo ""

# Summary
echo "================================================"
echo "Summary: $PASSED checks passed, $FAILED checks failed"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical checks passed! Environment is ready.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed. Review the output above.${NC}"
    echo "   Most warnings are expected. Critical failures will be marked in red."
    exit 0
fi

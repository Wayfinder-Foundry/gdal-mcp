"""Tests for path validation middleware."""
from __future__ import annotations

import os
import pytest
from unittest.mock import MagicMock

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import MiddlewareContext

from src.middleware import PathValidationMiddleware
from src.config import reset_workspaces_cache


@pytest.fixture
def middleware():
    """Create middleware instance."""
    return PathValidationMiddleware()


@pytest.fixture
def mock_context():
    """Create mock middleware context."""
    context = MagicMock(spec=MiddlewareContext)
    context.message = MagicMock()
    context.message.name = "test_tool"
    context.message.arguments = {}
    return context


@pytest.fixture
def mock_call_next():
    """Create mock call_next function."""
    async def call_next(ctx):
        return {"status": "success"}
    return call_next


@pytest.fixture(autouse=True)
def reset_workspace_cache():
    """Reset workspace cache before each test."""
    reset_workspaces_cache()
    yield
    reset_workspaces_cache()


@pytest.mark.asyncio
async def test_middleware_allows_when_no_workspaces_configured(
    middleware, mock_context, mock_call_next
):
    """Test that middleware allows all paths when no workspaces configured."""
    # No GDAL_MCP_WORKSPACES set - should allow all
    mock_context.message.arguments = {"uri": "/any/path/file.tif"}
    
    result = await middleware.on_call_tool(mock_context, mock_call_next)
    
    assert result == {"status": "success"}


@pytest.mark.asyncio
async def test_middleware_validates_input_path_within_workspace(
    middleware, mock_context, mock_call_next, tmp_path
):
    """Test that middleware allows paths within configured workspace."""
    # Create temp workspace
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Configure workspace
    os.environ["GDAL_MCP_WORKSPACES"] = str(workspace)
    reset_workspaces_cache()
    
    # Create test file within workspace
    test_file = workspace / "test.tif"
    test_file.touch()
    
    mock_context.message.arguments = {"uri": str(test_file)}
    
    result = await middleware.on_call_tool(mock_context, mock_call_next)
    
    assert result == {"status": "success"}
    
    # Cleanup
    del os.environ["GDAL_MCP_WORKSPACES"]


@pytest.mark.asyncio
async def test_middleware_denies_path_outside_workspace(
    middleware, mock_context, mock_call_next, tmp_path
):
    """Test that middleware denies paths outside configured workspace."""
    # Create temp workspace
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Configure workspace
    os.environ["GDAL_MCP_WORKSPACES"] = str(workspace)
    reset_workspaces_cache()
    
    # Try to access file outside workspace
    outside_file = tmp_path / "outside.tif"
    
    mock_context.message.arguments = {"uri": str(outside_file)}
    
    with pytest.raises(ToolError) as exc_info:
        await middleware.on_call_tool(mock_context, mock_call_next)
    
    assert "Access denied" in str(exc_info.value)
    assert "outside allowed workspaces" in str(exc_info.value)
    
    # Cleanup
    del os.environ["GDAL_MCP_WORKSPACES"]


@pytest.mark.asyncio
async def test_middleware_validates_output_path(
    middleware, mock_context, mock_call_next, tmp_path
):
    """Test that middleware validates output paths."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    os.environ["GDAL_MCP_WORKSPACES"] = str(workspace)
    reset_workspaces_cache()
    
    # Output path within workspace
    output_file = workspace / "output.tif"
    
    mock_context.message.arguments = {"output": str(output_file)}
    
    result = await middleware.on_call_tool(mock_context, mock_call_next)
    
    assert result == {"status": "success"}
    
    # Cleanup
    del os.environ["GDAL_MCP_WORKSPACES"]


@pytest.mark.asyncio
async def test_middleware_denies_output_outside_workspace(
    middleware, mock_context, mock_call_next, tmp_path
):
    """Test that middleware denies output paths outside workspace."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    os.environ["GDAL_MCP_WORKSPACES"] = str(workspace)
    reset_workspaces_cache()
    
    # Try to write outside workspace
    outside_output = tmp_path / "outside_output.tif"
    
    mock_context.message.arguments = {"output": str(outside_output)}
    
    with pytest.raises(ToolError) as exc_info:
        await middleware.on_call_tool(mock_context, mock_call_next)
    
    assert "Access denied" in str(exc_info.value)
    
    # Cleanup
    del os.environ["GDAL_MCP_WORKSPACES"]


@pytest.mark.asyncio
async def test_middleware_validates_multiple_path_args(
    middleware, mock_context, mock_call_next, tmp_path
):
    """Test that middleware validates multiple path arguments."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    os.environ["GDAL_MCP_WORKSPACES"] = str(workspace)
    reset_workspaces_cache()
    
    # Create input file
    input_file = workspace / "input.tif"
    input_file.touch()
    
    # Output path
    output_file = workspace / "output.tif"
    
    mock_context.message.arguments = {
        "uri": str(input_file),
        "output": str(output_file)
    }
    
    result = await middleware.on_call_tool(mock_context, mock_call_next)
    
    assert result == {"status": "success"}
    
    # Cleanup
    del os.environ["GDAL_MCP_WORKSPACES"]


@pytest.mark.asyncio
async def test_middleware_skips_empty_path_arguments(
    middleware, mock_context, mock_call_next
):
    """Test that middleware skips None/empty path arguments."""
    mock_context.message.arguments = {
        "uri": None,
        "output": "",
        "other_arg": "value"
    }
    
    result = await middleware.on_call_tool(mock_context, mock_call_next)
    
    assert result == {"status": "success"}


@pytest.mark.asyncio
async def test_middleware_includes_tool_name_in_error(
    middleware, mock_context, mock_call_next, tmp_path
):
    """Test that middleware includes tool name in error messages."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    os.environ["GDAL_MCP_WORKSPACES"] = str(workspace)
    reset_workspaces_cache()
    
    mock_context.message.name = "raster.info"
    mock_context.message.arguments = {"uri": "/etc/passwd"}
    
    with pytest.raises(ToolError) as exc_info:
        await middleware.on_call_tool(mock_context, mock_call_next)
    
    assert "raster.info" in str(exc_info.value)
    
    # Cleanup
    del os.environ["GDAL_MCP_WORKSPACES"]

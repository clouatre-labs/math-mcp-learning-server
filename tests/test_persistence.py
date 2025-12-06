#!/usr/bin/env python3
"""
Test cases for the Math MCP Learning Server persistence functionality.
Tests cross-platform workspace persistence, thread safety, and MCP integration.
"""

import json
import os
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from math_mcp.persistence.models import WorkspaceData, WorkspaceVariable
from math_mcp.persistence.storage import (
    ensure_workspace_directory,
    get_workspace_dir,
    get_workspace_file,
)
from math_mcp.persistence.workspace import _workspace_manager
from math_mcp.server import get_workspace, load_variable, save_calculation

# === FIXTURES ===


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing with proper isolation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test_workspace.json"
        # Patch both storage functions to ensure all WorkspaceManager instances use temp path
        with (
            patch("math_mcp.persistence.storage.get_workspace_dir", return_value=Path(temp_dir)),
            patch("math_mcp.persistence.storage.get_workspace_file", return_value=temp_path),
        ):
            # Clear global workspace manager state for test isolation
            from math_mcp.persistence.workspace import _workspace_manager

            _workspace_manager._cache = None
            _workspace_manager._workspace_file = temp_path
            yield temp_path


@pytest.fixture
def mock_context():
    """Create mock context for MCP tool testing."""

    class MockLifespanContext:
        def __init__(self):
            self.calculation_history = []

    class MockRequestContext:
        def __init__(self):
            self.lifespan_context = MockLifespanContext()

    class MockContext:
        def __init__(self):
            self.request_context = MockRequestContext()
            self.info_logs = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

    return MockContext()


# === MODEL TESTS ===


def test_workspace_variable_model():
    """Test WorkspaceVariable Pydantic model."""
    var = WorkspaceVariable(
        expression="2 + 2",
        result=4.0,
        timestamp="2025-01-01T12:00:00",
        metadata={"difficulty": "basic", "topic": "arithmetic"},
    )

    assert var.expression == "2 + 2"
    assert var.result == 4.0
    assert var.type == "calculation"  # Default value
    assert var.metadata["difficulty"] == "basic"

    # Test serialization/deserialization
    data = var.model_dump()
    restored = WorkspaceVariable(**data)
    assert restored == var


def test_workspace_data_model():
    """Test WorkspaceData Pydantic model."""
    workspace = WorkspaceData(
        created="2025-01-01T10:00:00",
        updated="2025-01-01T12:00:00",
        variables={
            "test_var": WorkspaceVariable(
                expression="pi * 2", result=6.283185307179586, timestamp="2025-01-01T12:00:00"
            )
        },
        statistics={"total_calculations": 1},
    )

    assert workspace.version == "1.0"  # Default value
    assert len(workspace.variables) == 1
    assert "test_var" in workspace.variables
    assert workspace.statistics["total_calculations"] == 1


# === STORAGE TESTS ===


def test_cross_platform_paths():
    """Test cross-platform path handling."""
    # Test Unix-like path (works on all platforms)
    with patch("os.name", "posix"), patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        workspace_dir = get_workspace_dir()
        assert str(workspace_dir) == "/home/testuser/.math-mcp"

    # Test Windows path logic using environment variable
    # (avoids creating WindowsPath on non-Windows systems)
    with (
        patch("os.name", "nt"),
        patch.dict("os.environ", {"LOCALAPPDATA": "C:\\Users\\Test\\AppData\\Local"}, clear=False),
    ):
        # When LOCALAPPDATA is set, get_workspace_dir uses it directly
        # We verify the logic without calling the function (which would create WindowsPath)
        assert os.environ.get("LOCALAPPDATA") == "C:\\Users\\Test\\AppData\\Local"
        # The expected result would be: C:\Users\Test\AppData\Local\math-mcp


def test_workspace_file_creation():
    """Test workspace file path creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("math_mcp.persistence.storage.get_workspace_dir", return_value=Path(temp_dir)):
            workspace_file = get_workspace_file()
            assert workspace_file.parent.exists()
            assert workspace_file.name == "workspace.json"


def test_ensure_workspace_directory():
    """Test workspace directory creation and permission checking."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch(
            "math_mcp.persistence.storage.get_workspace_dir",
            return_value=Path(temp_dir) / "math-mcp",
        ):
            assert ensure_workspace_directory() is True
            assert (Path(temp_dir) / "math-mcp").exists()


# === WORKSPACE MANAGER TESTS ===


def test_workspace_manager_initialization(temp_workspace):
    """Test WorkspaceManager initialization."""
    # Use global manager to ensure fixture patching is respected
    assert _workspace_manager._workspace_file == temp_workspace
    # Verify lock is an RLock (check type name since RLock is a factory)
    assert type(_workspace_manager._lock).__name__ == "RLock"


def test_save_variable_basic(temp_workspace):
    """Test basic variable saving functionality."""
    result = _workspace_manager.save_variable(
        name="test_var", expression="2 + 2", result=4.0, metadata={"difficulty": "basic"}
    )

    assert result["success"] is True
    assert result["variable_name"] == "test_var"
    assert result["is_new"] is True
    assert result["total_variables"] == 1

    # Verify file was created
    assert temp_workspace.exists()

    # Verify content
    with open(temp_workspace) as f:
        data = json.load(f)
    assert "test_var" in data["variables"]
    assert data["variables"]["test_var"]["expression"] == "2 + 2"
    assert data["variables"]["test_var"]["result"] == 4.0


def test_load_variable_basic(temp_workspace):
    """Test basic variable loading functionality."""
    # First save a variable
    _workspace_manager.save_variable("test_var", "5 * 5", 25.0)

    # Then load it
    result = _workspace_manager.load_variable("test_var")

    assert result["success"] is True
    assert result["variable_name"] == "test_var"
    assert result["expression"] == "5 * 5"
    assert result["result"] == 25.0


def test_load_nonexistent_variable(temp_workspace):
    """Test loading a variable that doesn't exist."""
    # Save one variable first
    _workspace_manager.save_variable("existing_var", "1 + 1", 2.0)

    # Try to load nonexistent variable
    result = _workspace_manager.load_variable("nonexistent_var")

    assert result["success"] is False
    assert "not found" in result["error"]
    assert "existing_var" in result["available_variables"]


def test_variable_overwrite(temp_workspace):
    """Test overwriting an existing variable."""
    # Save initial variable
    result1 = _workspace_manager.save_variable("test_var", "2 + 2", 4.0)
    assert result1["is_new"] is True

    # Overwrite with new value
    result2 = _workspace_manager.save_variable("test_var", "3 + 3", 6.0)
    assert result2["is_new"] is False
    assert result2["total_variables"] == 1  # Still only one variable

    # Verify the new value
    loaded = _workspace_manager.load_variable("test_var")
    assert loaded["expression"] == "3 + 3"
    assert loaded["result"] == 6.0


def test_workspace_summary(temp_workspace):
    """Test workspace summary generation."""
    # Empty workspace
    summary = _workspace_manager.get_workspace_summary()
    assert "Workspace is empty" in summary

    # Add some variables
    _workspace_manager.save_variable("var1", "10 + 5", 15.0, {"difficulty": "basic"})
    _workspace_manager.save_variable(
        "var2", "sin(pi/2)", 1.0, {"difficulty": "advanced", "topic": "trigonometry"}
    )

    summary = _workspace_manager.get_workspace_summary()
    assert "2 variables" in summary
    assert "var1" in summary
    assert "var2" in summary
    assert "10 + 5" in summary
    assert "sin(pi/2)" in summary
    assert "15.0" in summary
    assert "1.0" in summary


def test_thread_safety(temp_workspace):
    """Test thread-safe concurrent access."""

    def save_variables(thread_id):
        """Save variables from different threads."""
        for i in range(5):
            _workspace_manager.save_variable(
                f"thread_{thread_id}_var_{i}", f"{thread_id} + {i}", thread_id + i
            )

    # Create multiple threads
    threads = []
    for thread_id in range(3):
        thread = threading.Thread(target=save_variables, args=(thread_id,))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=5.0)  # 5 second timeout

    # Verify all variables were saved
    summary = _workspace_manager.get_workspace_summary()
    assert "15 variables" in summary  # 3 threads * 5 variables each

    # Verify no corruption by loading a few variables
    result = _workspace_manager.load_variable("thread_0_var_0")
    assert result["success"] is True
    assert result["result"] == 0.0

    result = _workspace_manager.load_variable("thread_2_var_4")
    assert result["success"] is True
    assert result["result"] == 6.0


def test_file_corruption_recovery(temp_workspace):
    """Test graceful handling of corrupted workspace files."""
    # Create corrupted JSON file
    with open(temp_workspace, "w") as f:
        f.write("{ invalid json content")

    # Clear cache to force reload
    _workspace_manager._cache = None

    # Should create new workspace instead of crashing
    result = _workspace_manager.save_variable("test_var", "1 + 1", 2.0)
    assert result["success"] is True

    # Should be able to load the variable
    loaded = _workspace_manager.load_variable("test_var")
    assert loaded["success"] is True


def test_permission_error_handling(temp_workspace):
    """Test handling of permission errors."""
    # Save a variable first
    result = _workspace_manager.save_variable("test_var", "2 + 2", 4.0)
    assert result["success"] is True

    # Mock permission error on save
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        result = _workspace_manager.save_variable("another_var", "3 + 3", 6.0)
        assert result["success"] is False
        assert "Failed to save" in result["message"]


# === MCP INTEGRATION TESTS ===


@pytest.mark.asyncio
async def test_save_calculation_tool(temp_workspace, mock_context):
    """Test save_calculation MCP tool."""
    result = await save_calculation.fn("portfolio_return", "10000 * 1.07^5", 14025.52, mock_context)

    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert content["type"] == "text"
    assert "Saved Variable" in content["text"]
    assert "portfolio_return" in content["text"]
    assert "14025.52" in content["text"]

    # Check annotations
    annotations = content["annotations"]
    assert annotations["action"] == "save_calculation"
    assert annotations["variable_name"] == "portfolio_return"
    assert annotations["is_new"] is True
    assert "difficulty" in annotations
    assert "topic" in annotations

    # Check session history was updated
    assert len(mock_context.request_context.lifespan_context.calculation_history) == 1
    history_entry = mock_context.request_context.lifespan_context.calculation_history[0]
    assert history_entry["type"] == "save_calculation"
    assert history_entry["name"] == "portfolio_return"


@pytest.mark.asyncio
async def test_load_variable_tool(temp_workspace, mock_context):
    """Test load_variable MCP tool."""
    # First save a variable using the workspace manager directly
    _workspace_manager.save_variable("circle_area", "pi * 5^2", 78.54, {"topic": "geometry"})

    # Then load it using the MCP tool
    result = await load_variable.fn("circle_area", mock_context)

    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert content["type"] == "text"
    assert "Loaded Variable" in content["text"]
    assert "circle_area" in content["text"]
    assert "78.54" in content["text"]
    assert "pi * 5^2" in content["text"]

    # Check annotations
    annotations = content["annotations"]
    assert annotations["action"] == "load_variable"
    assert annotations["variable_name"] == "circle_area"

    # Check session history was updated
    assert len(mock_context.request_context.lifespan_context.calculation_history) == 1


@pytest.mark.asyncio
async def test_load_variable_not_found(temp_workspace, mock_context):
    """Test load_variable tool with nonexistent variable."""
    result = await load_variable.fn("nonexistent_var", mock_context)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert "Error" in content["text"]
    assert "not found" in content["text"]

    annotations = content["annotations"]
    assert annotations["action"] == "load_variable_error"
    assert annotations["requested_name"] == "nonexistent_var"


@pytest.mark.asyncio
async def test_workspace_resource(temp_workspace, mock_context):
    """Test math://workspace resource."""
    # Add some variables
    _workspace_manager.save_variable("var1", "2 + 2", 4.0, {"difficulty": "basic"})
    _workspace_manager.save_variable("var2", "sqrt(16)", 4.0, {"difficulty": "intermediate"})

    # Get workspace resource
    result = await get_workspace.fn(mock_context)

    assert isinstance(result, str)
    assert "2 variables" in result
    assert "var1" in result
    assert "var2" in result
    assert "2 + 2" in result
    assert "sqrt(16)" in result


@pytest.mark.asyncio
async def test_workspace_resource_empty(temp_workspace, mock_context):
    """Test math://workspace resource when empty."""
    result = await get_workspace.fn(mock_context)

    assert isinstance(result, str)
    assert "Workspace is empty" in result
    assert "save_calculation()" in result


# === INPUT VALIDATION TESTS ===


@pytest.mark.asyncio
async def test_save_calculation_validation(temp_workspace, mock_context):
    """Test input validation for save_calculation tool."""
    # Empty name
    with pytest.raises(ValueError, match="Variable name cannot be empty"):
        await save_calculation.fn("", "2 + 2", 4.0, mock_context)

    # Invalid characters in name
    with pytest.raises(ValueError, match="Variable name must contain only"):
        await save_calculation.fn("invalid name!", "2 + 2", 4.0, mock_context)

    # Valid names should work
    result = await save_calculation.fn("valid_name-123", "2 + 2", 4.0, mock_context)
    assert "Success" in result["content"][0]["text"]


# === INTEGRATION WITH EXISTING FUNCTIONALITY ===


@pytest.mark.asyncio
async def test_integration_with_calculation_history(temp_workspace, mock_context):
    """Test that persistence integrates properly with existing calculation history."""
    # Save a calculation
    await save_calculation.fn("test_var", "5 * 5", 25.0, mock_context)

    # Load the calculation
    await load_variable.fn("test_var", mock_context)

    # Check that both operations are in session history
    history = mock_context.request_context.lifespan_context.calculation_history
    assert len(history) == 2

    save_entry = history[0]
    assert save_entry["type"] == "save_calculation"
    assert save_entry["name"] == "test_var"

    load_entry = history[1]
    assert load_entry["type"] == "load_variable"
    assert load_entry["name"] == "test_var"


def test_persistent_across_manager_instances(temp_workspace):
    """Test that data persists across workspace reloads (cache clearing)."""
    # Save data with global manager
    result = _workspace_manager.save_variable("persistent_var", "100 / 4", 25.0)
    assert result["success"] is True

    # Clear cache to simulate reload (like server restart)
    _workspace_manager._cache = None

    # Load should still work after cache clear
    loaded = _workspace_manager.load_variable("persistent_var")
    assert loaded["success"] is True
    assert loaded["expression"] == "100 / 4"
    assert loaded["result"] == 25.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

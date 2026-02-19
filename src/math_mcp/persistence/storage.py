#!/usr/bin/env python3
"""
Cross-platform storage utilities for Math MCP Learning Server.
Handles file system operations and path management across Windows, macOS, and Linux.
"""

import os
from pathlib import Path


def get_workspace_dir() -> Path:
    """Get cross-platform workspace directory following OS conventions.

    Returns:
        Path: Platform-appropriate directory for persistent data
        - Windows: %LOCALAPPDATA%/math-mcp
        - macOS/Linux: ~/.math-mcp
    """
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "math-mcp"
    else:  # macOS and Linux (and other Unix-like systems)
        return Path.home() / ".math-mcp"


def get_workspace_file() -> Path:
    """Get workspace file path with automatic directory creation.

    Creates the workspace directory if it doesn't exist.

    Returns:
        Path: Full path to workspace.json file
    """
    workspace_dir = get_workspace_dir()
    workspace_dir.mkdir(parents=True, exist_ok=True)
    return workspace_dir / "workspace.json"


def ensure_workspace_directory() -> bool:
    """Ensure workspace directory exists and is writable.

    Returns:
        bool: True if directory is accessible, False otherwise
    """
    try:
        workspace_dir = get_workspace_dir()
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Test write access
        test_file = workspace_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()

        return True
    except (OSError, PermissionError):
        return False

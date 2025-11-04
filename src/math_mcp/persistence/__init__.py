#!/usr/bin/env python3
"""
Persistence module for Math MCP Learning Server.
Provides cross-platform persistent workspace functionality following MCP best practices.
"""

from math_mcp.persistence.models import WorkspaceData, WorkspaceVariable
from math_mcp.persistence.storage import (
    ensure_workspace_directory,
    get_workspace_dir,
    get_workspace_file,
)
from math_mcp.persistence.workspace import WorkspaceManager, _workspace_manager

__all__ = [
    "WorkspaceData",
    "WorkspaceVariable",
    "WorkspaceManager",
    "_workspace_manager",
    "get_workspace_dir",
    "get_workspace_file",
    "ensure_workspace_directory",
]

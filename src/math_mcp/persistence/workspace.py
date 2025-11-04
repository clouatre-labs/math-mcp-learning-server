#!/usr/bin/env python3
"""
Thread-safe workspace manager for persistent calculations.
Core persistence logic for Math MCP Learning Server following enterprise patterns.
"""

import json
import logging
import threading
from datetime import datetime
from typing import Any

from math_mcp.persistence.models import WorkspaceData, WorkspaceVariable
from math_mcp.persistence.storage import get_workspace_file


class WorkspaceManager:
    """Thread-safe workspace manager for persistent calculations across sessions.

    Provides atomic operations for saving/loading calculation variables with
    graceful error handling and cross-platform compatibility.
    """

    def __init__(self):
        """Initialize workspace manager with thread safety."""
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        self._workspace_file = get_workspace_file()
        self._cache: WorkspaceData | None = None

    def _load_workspace(self) -> WorkspaceData:
        """Load workspace from disk with comprehensive error handling.

        Returns:
            WorkspaceData: Loaded workspace or new empty workspace on error
        """
        try:
            if self._workspace_file.exists():
                with open(self._workspace_file, encoding="utf-8") as f:
                    data = json.load(f)
                    return WorkspaceData(**data)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            logging.warning(f"Failed to load workspace: {e}. Creating new workspace.")
        except Exception as e:
            logging.error(f"Unexpected error loading workspace: {e}")

        # Return new workspace if loading fails
        now = datetime.now().isoformat()
        return WorkspaceData(
            created=now,
            updated=now,
            statistics={"total_calculations": 0, "session_count": 1, "last_access": now},
        )

    def _save_workspace(self, workspace: WorkspaceData) -> bool:
        """Save workspace to disk with atomic write pattern.

        Args:
            workspace: WorkspaceData to save

        Returns:
            bool: True if save succeeded, False otherwise
        """
        try:
            # Update metadata
            workspace.updated = datetime.now().isoformat()

            # Atomic write using temporary file
            temp_file = self._workspace_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(workspace.model_dump(), f, indent=2, ensure_ascii=False)

            # Atomic replacement - prevents corruption on crash
            temp_file.replace(self._workspace_file)
            return True

        except (PermissionError, OSError) as e:
            logging.error(f"Failed to save workspace: {e}")
            return False

    def save_variable(
        self, name: str, expression: str, result: float, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Save a calculation variable to persistent workspace.

        Args:
            name: Variable name (must be valid identifier)
            expression: Mathematical expression
            result: Calculated result
            metadata: Optional educational metadata

        Returns:
            Dict with operation status and details
        """
        with self._lock:
            workspace = self._load_workspace()

            # Create variable
            variable = WorkspaceVariable(
                expression=expression,
                result=result,
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {},
            )

            # Update workspace
            is_new = name not in workspace.variables
            workspace.variables[name] = variable
            workspace.statistics["total_calculations"] = len(workspace.variables)
            workspace.statistics["last_access"] = variable.timestamp

            # Save to disk
            success = self._save_workspace(workspace)

            return {
                "success": success,
                "variable_name": name,
                "is_new": is_new,
                "total_variables": len(workspace.variables),
                "message": f"{'Saved' if success else 'Failed to save'} variable '{name}'",
            }

    def load_variable(self, name: str) -> dict[str, Any]:
        """Load a variable from workspace.

        Args:
            name: Variable name to load

        Returns:
            Dict with variable data or error information
        """
        with self._lock:
            workspace = self._load_workspace()

            if name not in workspace.variables:
                return {
                    "success": False,
                    "error": f"Variable '{name}' not found",
                    "available_variables": list(workspace.variables.keys()),
                }

            variable = workspace.variables[name]

            # Update access time
            workspace.statistics["last_access"] = datetime.now().isoformat()
            self._save_workspace(workspace)

            return {
                "success": True,
                "variable_name": name,
                "expression": variable.expression,
                "result": variable.result,
                "timestamp": variable.timestamp,
                "metadata": variable.metadata,
            }

    def get_workspace_summary(self) -> str:
        """Get formatted workspace summary for math://workspace resource.

        Returns:
            str: Human-readable workspace summary
        """
        with self._lock:
            workspace = self._load_workspace()

            if not workspace.variables:
                return "**Workspace is empty.** Use save_calculation() to store variables across sessions."

            summary = f"# Math Workspace ({len(workspace.variables)} variables)\n\n"
            summary += f"**Created:** {workspace.created}\n"
            summary += f"**Last Updated:** {workspace.updated}\n\n"

            summary += "## Saved Variables\n\n"
            for name, var in workspace.variables.items():
                summary += f"- **{name}**: `{var.expression}` = {var.result}\n"
                summary += f"  - Saved: {var.timestamp}\n"
                if var.metadata:
                    metadata_str = ", ".join(f"{k}: {v}" for k, v in var.metadata.items())
                    summary += f"  - Metadata: {metadata_str}\n"
                summary += "\n"

            stats = workspace.statistics
            summary += "## Statistics\n\n"
            summary += f"- **Total Calculations:** {stats.get('total_calculations', 0)}\n"
            summary += f"- **Session Count:** {stats.get('session_count', 1)}\n"
            summary += f"- **Last Access:** {stats.get('last_access', 'Never')}\n"

            return summary

    def list_variables(self) -> dict[str, Any]:
        """Get list of all variable names for autocomplete/suggestions.

        Returns:
            Dict with variable names and metadata
        """
        with self._lock:
            workspace = self._load_workspace()
            return {
                "variables": list(workspace.variables.keys()),
                "count": len(workspace.variables),
                "last_updated": workspace.updated,
            }


# Global workspace manager instance - initialized once per server process
_workspace_manager = WorkspaceManager()

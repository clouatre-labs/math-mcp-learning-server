"""MCP tool sub-servers mounted onto the main Math Learning Server."""

from fastmcp import FastMCP

from math_mcp.tools.matrix import create_matrix_tools
from math_mcp.tools.visualization import visualization_mcp

# Matrix operations sub-server
matrix_mcp = FastMCP("matrix-operations")
create_matrix_tools(matrix_mcp)

__all__ = ["matrix_mcp", "visualization_mcp"]

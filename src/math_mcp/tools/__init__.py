"""MCP tool sub-servers mounted onto the main Math Learning Server."""

from fastmcp import FastMCP

from math_mcp.tools.calculate import calculate_mcp
from math_mcp.tools.matrix import create_matrix_tools
from math_mcp.tools.persistence import persistence_mcp
from math_mcp.tools.visualization import visualization_mcp

# Matrix operations sub-server
matrix_mcp = FastMCP("matrix-operations")
create_matrix_tools(matrix_mcp)

__all__ = ["calculate_mcp", "matrix_mcp", "persistence_mcp", "visualization_mcp"]

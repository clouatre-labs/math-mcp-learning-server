"""MCP tools modules for math operations."""

from fastmcp import FastMCP

from math_mcp.tools.matrix import create_matrix_tools

# Create a FastMCP instance for matrix operations
matrix_mcp = FastMCP(name="matrix-operations")

# Register matrix tools with the instance
create_matrix_tools(matrix_mcp)

__all__ = ["matrix_mcp"]

"""Typed response models for MCP tools.

This module defines Pydantic BaseModel subclasses for all tool return types.
Typed returns improve MCP client schema generation and provide IDE autocomplete
for downstream consumers. Each model uses pure attribute access (no __getitem__)
and keeps content items as plain dicts to avoid over-modeling MCP protocol blobs.

Educational note: BaseModel serialization via model_dump() produces identical
JSON to the previous dict-based returns, but with the added benefit of
runtime validation and static type checking.
"""

from typing import Any

from pydantic import BaseModel, Field


class CalculationResult(BaseModel):
    """Result of a mathematical calculation.

    Used by: calculate, statistics, compound_interest, convert_units tools.

    Attributes:
        content: List of content items (text, images, etc.) for MCP protocol.
                 Items remain as plain dicts to preserve MCP flexibility.
    """

    content: list[dict[str, Any]] = Field(
        default_factory=list,
        description="MCP content items (text, images, etc.)",
    )


class MatrixResult(BaseModel):
    """Result of a matrix operation.

    Used by: all 5 matrix tools (add, multiply, transpose, determinant, inverse).

    Attributes:
        content: List of content items describing the matrix operation result.
                 Items remain as plain dicts.
    """

    content: list[dict[str, Any]] = Field(
        default_factory=list,
        description="MCP content items with matrix data and visualization",
    )


class WorkspaceResult(BaseModel):
    """Result of a workspace operation (save/load).

    Used by: save_calculation, load_variable tools.

    Attributes:
        content: List of content items for MCP protocol.
                 Items remain as plain dicts to preserve MCP flexibility.
    """

    content: list[dict[str, Any]] = Field(
        default_factory=list,
        description="MCP content items",
    )


class VisualizationResult(BaseModel):
    """Result of a visualization operation.

    Used by: all 6 visualization tools (plot, scatter, histogram, heatmap, 3d_surface, mandelbrot).

    Attributes:
        content: List of content items with plot images and descriptions.
                 Items remain as plain dicts.
    """

    content: list[dict[str, Any]] = Field(
        default_factory=list,
        description="MCP content items with plot images and metadata",
    )

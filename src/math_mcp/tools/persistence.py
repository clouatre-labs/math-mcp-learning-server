"""
Persistence Tools Sub-Server
FastMCP sub-server for saving and loading calculations from persistent workspace.
"""

from datetime import datetime
from typing import Annotated, Any, cast

from fastmcp import Context, FastMCP
from pydantic import Field, SkipValidation

from math_mcp.eval import (
    _classify_expression_difficulty,
    _classify_expression_topic,
    validate_variable_name,
)
from math_mcp.settings import (
    MAX_EXPRESSION_LENGTH,
    MAX_VARIABLE_NAME_LENGTH,
    validated_tool,
)
from math_mcp.tools._session import _get_or_create_session_id

# Create sub-server for persistence tools
persistence_mcp = FastMCP(name="Persistence Tools")


@persistence_mcp.tool(
    annotations={
        "title": "Save Calculation to Workspace",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
async def save_calculation(
    name: Annotated[str, Field(max_length=MAX_VARIABLE_NAME_LENGTH)],
    expression: Annotated[str, Field(max_length=MAX_EXPRESSION_LENGTH)],
    result: float,
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Save calculation to persistent workspace (survives restarts).

    Args:
        name: Variable name to save under
        expression: The mathematical expression
        result: The calculated result

    Examples:
        save_calculation("portfolio_return", "10000 * 1.07^5", 14025.52)
        save_calculation("circle_area", "pi * 5^2", 78.54)
    """
    validate_variable_name(name)

    if ctx:
        await ctx.info(f"Saving calculation '{name}' = {result}")

    difficulty = _classify_expression_difficulty(expression)
    topic = _classify_expression_topic(expression)

    metadata = {
        "difficulty": difficulty,
        "topic": topic,
        "session_id": await _get_or_create_session_id(ctx),
    }

    from math_mcp.persistence.workspace import _workspace_manager

    result_data = _workspace_manager.save_variable(name, expression, result, metadata)

    history_entry = {
        "type": "save_calculation",
        "name": name,
        "expression": expression,
        "result": result,
        "timestamp": datetime.now().isoformat(),
    }
    if ctx and ctx.lifespan_context:
        cast(Any, ctx.lifespan_context).calculation_history.append(history_entry)

    return {
        "content": [
            {
                "type": "text",
                "text": f"**Saved Variable:** {name} = {result}\n**Expression:** {expression}\n**Status:** {'Success' if result_data['success'] else 'Failed'}",
                "annotations": {
                    "action": "save_calculation",
                    "variable_name": name,
                    "is_new": result_data.get("is_new", True),
                    "total_variables": result_data.get("total_variables", 0),
                    **metadata,
                },
            }
        ]
    }


@persistence_mcp.tool()
async def load_variable(name: str, ctx: SkipValidation[Context | None] = None) -> dict[str, Any]:
    """Load previously saved calculation result from workspace.

    Args:
        name: Variable name to load

    Examples:
        load_variable("portfolio_return")  # Returns saved calculation
        load_variable("circle_area")       # Access across sessions
    """
    if ctx:
        await ctx.info(f"Loading variable '{name}'")
    from math_mcp.persistence.workspace import _workspace_manager

    result_data = _workspace_manager.load_variable(name)

    if not result_data["success"]:
        available = result_data.get("available_variables", [])
        error_msg = result_data["error"]
        if available:
            error_msg += f"\nAvailable variables: {', '.join(available)}"

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Error:** {error_msg}",
                    "annotations": {
                        "action": "load_variable_error",
                        "requested_name": name,
                        "available_count": len(available),
                    },
                }
            ]
        }

    history_entry = {
        "type": "load_variable",
        "name": name,
        "expression": result_data["expression"],
        "result": result_data["result"],
        "timestamp": datetime.now().isoformat(),
    }
    if ctx and ctx.lifespan_context:
        cast(Any, ctx.lifespan_context).calculation_history.append(history_entry)

    return {
        "content": [
            {
                "type": "text",
                "text": f"**Loaded Variable:** {name} = {result_data['result']}\n**Expression:** {result_data['expression']}\n**Saved:** {result_data['timestamp']}",
                "annotations": {
                    "action": "load_variable",
                    "variable_name": name,
                    "original_timestamp": result_data["timestamp"],
                    **result_data.get("metadata", {}),
                },
            }
        ]
    }

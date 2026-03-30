"""
Persistence Tools Sub-Server
FastMCP sub-server for saving and loading calculations from persistent workspace.
"""

from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field, SkipValidation

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


class SaveCalculationResult(BaseModel):
    """Result of saving a calculation to the workspace."""

    name: str
    expression: str
    result: float
    success: bool
    is_new: bool
    total_variables: int
    difficulty: str
    topic: str
    session_id: str | None = None
    action: str = "save_calculation"


class LoadVariableResult(BaseModel):
    """Result of loading a variable from the workspace."""

    success: bool
    name: str
    action: str
    result: float | None = None
    expression: str | None = None
    timestamp: str | None = None
    error: str | None = None
    available_variables: list[str] | None = None
    difficulty: str | None = None
    topic: str | None = None
    session_id: str | None = None


# Create sub-server for persistence tools
persistence_mcp = FastMCP(name="Persistence Tools")


@persistence_mcp.tool(
    annotations={
        "title": "Save Calculation to Workspace",
        "readOnlyHint": False,
        "openWorldHint": False,
        "idempotentHint": False,
    }
)
@validated_tool
async def save_calculation(
    name: Annotated[
        str,
        Field(
            max_length=MAX_VARIABLE_NAME_LENGTH,
            description="Variable name for the saved calculation. Used to retrieve it later. Example: 'circle_area'",
        ),
    ],
    expression: Annotated[
        str,
        Field(
            max_length=MAX_EXPRESSION_LENGTH,
            description="The mathematical expression that was evaluated. Example: 'pi * r**2'",
        ),
    ],
    result: Annotated[
        float, Field(description="Numeric result of evaluating the expression, e.g., 78.54")
    ],
    ctx: SkipValidation[Context | None] = None,
) -> SaveCalculationResult:
    """Save calculation to persistent workspace (survives restarts).

    Returns:
        SaveCalculationResult: Result of saving the calculation containing:
            - name: The variable name
            - expression: The saved expression
            - result: The calculated result
            - success: Whether the save operation succeeded
            - is_new: Whether this is a new variable or an update
            - total_variables: Total number of saved variables in workspace
            - difficulty: Complexity level of the expression
            - topic: Category of the expression
            - session_id: Session identifier

    Examples:
        save_calculation("portfolio_return", "10000 * 1.07^5", 14025.52)
        save_calculation("circle_area", "pi * 5^2", 78.54)
    """
    validate_variable_name(name)

    if ctx:
        await ctx.info(f"Saving calculation '{name}' = {result}")

    difficulty = _classify_expression_difficulty(expression)
    topic = _classify_expression_topic(expression)
    session_id = await _get_or_create_session_id(ctx)

    from math_mcp.persistence.workspace import _workspace_manager

    result_data = _workspace_manager.save_variable(
        name,
        expression,
        result,
        {
            "difficulty": difficulty,
            "topic": topic,
            "session_id": session_id,
        },
    )

    return SaveCalculationResult(
        name=name,
        expression=expression,
        result=result,
        success=result_data["success"],
        is_new=result_data.get("is_new", True),
        total_variables=result_data.get("total_variables", 0),
        difficulty=difficulty,
        topic=topic,
        session_id=session_id,
    )


@persistence_mcp.tool(
    annotations={
        "title": "Load Variable",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    }
)
async def load_variable(
    name: Annotated[
        str, Field(description="Name of the variable to load from workspace, e.g., 'circle_area'")
    ],
    ctx: SkipValidation[Context | None] = None,
) -> LoadVariableResult:
    """Load previously saved calculation result from workspace.

    Returns:
        LoadVariableResult: Result of loading the variable containing:
            - success: Whether the variable was found
            - name: The variable name
            - action: Operation type (load_variable)
            - result: The calculated result (if successful)
            - expression: The saved expression (if successful)
            - timestamp: When the variable was saved
            - difficulty: Complexity level of the expression
            - topic: Category of the expression
            - session_id: Session identifier where it was saved
            - error: Error message (if unsuccessful)
            - available_variables: List of available variables (if unsuccessful)

    Examples:
        load_variable("portfolio_return")  # Returns saved calculation
        load_variable("circle_area")       # Access across sessions
    """
    if ctx:
        await ctx.info(f"Loading variable '{name}'")
    from math_mcp.persistence.workspace import _workspace_manager

    result_data = _workspace_manager.load_variable(name)

    if not result_data["success"]:
        if ctx:
            await ctx.warning(f"Variable '{name}' not found in workspace")
        return LoadVariableResult(
            success=False,
            name=name,
            action="load_variable",
            error=result_data.get("error"),
            available_variables=result_data.get("available_variables"),
        )

    metadata = result_data.get("metadata", {})
    return LoadVariableResult(
        success=True,
        name=name,
        action="load_variable",
        result=result_data.get("result"),
        expression=result_data.get("expression"),
        timestamp=result_data.get("timestamp"),
        difficulty=metadata.get("difficulty"),
        topic=metadata.get("topic"),
        session_id=metadata.get("session_id"),
    )

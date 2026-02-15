#!/usr/bin/env python3
"""
Math MCP Server - FastMCP 2.0 Implementation
Educational MCP server demonstrating all three MCP pillars: Tools, Resources, and Prompts.
Uses FastMCP 2.0 patterns with structured output and multi-transport support.
"""

import logging
import math
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
from fastmcp.server.middleware.rate_limiting import (
    RateLimitError,
    SlidingWindowRateLimitingMiddleware,
)
from pydantic import Field, SkipValidation
from starlette.responses import JSONResponse

from math_mcp.agent_card import AgentCard, AgentSkill
from math_mcp.eval import (
    _classify_expression_difficulty,
    _classify_expression_topic,
    convert_temperature,
    evaluate_with_timeout,
    validate_variable_name,
)
from math_mcp.settings import (
    ALLOWED_OPERATIONS,
    MathMCPSettings,
    validated_tool,
)
from math_mcp.tools import matrix_mcp, visualization_mcp

# Try importing numpy for matrix operations
try:
    import numpy as np
    import numpy.linalg as la

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    la = None  # type: ignore

# Initialize settings from environment
settings = MathMCPSettings()

# Keep constants for backward compatibility
RATE_LIMIT_PER_MINUTE = settings.mcp_rate_limit_per_minute

# === INPUT SIZE LIMITS ===

MAX_EXPRESSION_LENGTH = settings.max_expression_length
MAX_STRING_PARAM_LENGTH = settings.max_string_param_length
MAX_ARRAY_SIZE = settings.max_array_size
MAX_VARIABLE_NAME_LENGTH = settings.max_variable_name_length

# === APPLICATION CONTEXT ===


@dataclass
class AppContext:
    """Application context with calculation history."""

    calculation_history: list[dict[str, Any]]


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with calculation history."""
    # Initialize calculation history
    calculation_history: list[dict[str, Any]] = []
    try:
        yield AppContext(calculation_history=calculation_history)
    finally:
        # Could save history to file here
        pass


# === FASTMCP SERVER SETUP ===

mcp = FastMCP(
    name="Math Learning Server",
    lifespan=app_lifespan,
    instructions="A comprehensive math server demonstrating MCP fundamentals with tools, resources, and prompts for educational purposes.",
)

# Mount sub-server tools using FastMCP composition pattern
mcp.mount(matrix_mcp)
mcp.mount(visualization_mcp)


# === RATE LIMITING MIDDLEWARE ===


def _log_rate_limit_violation(error: Exception, context) -> None:
    """Log rate limit violations for monitoring."""
    if isinstance(error, RateLimitError):
        logging.warning(f"Rate limit exceeded: method={context.method}")


# Add middleware in correct order: StructuredLogging -> ErrorHandling -> RateLimiting
# Logging middleware placed first to capture all requests before other processing
mcp.add_middleware(StructuredLoggingMiddleware(include_payloads=True))
mcp.add_middleware(ErrorHandlingMiddleware(error_callback=_log_rate_limit_violation))
if RATE_LIMIT_PER_MINUTE > 0:
    mcp.add_middleware(
        SlidingWindowRateLimitingMiddleware(max_requests=RATE_LIMIT_PER_MINUTE, window_minutes=1)
    )
    logging.info(f"Rate limiting enabled: {RATE_LIMIT_PER_MINUTE} requests/minute")


# === TOOLS: COMPUTATIONAL OPERATIONS ===


@mcp.tool(
    annotations={"title": "Mathematical Calculator", "readOnlyHint": False, "openWorldHint": True}
)
@validated_tool
async def calculate(
    expression: Annotated[str, Field(max_length=MAX_EXPRESSION_LENGTH)],
    ctx: SkipValidation[Context],
) -> dict[str, Any]:
    """Safely evaluate mathematical expressions with support for basic operations and math functions.

    Supported operations: +, -, *, /, **, ()
    Supported functions: sin, cos, tan, log, sqrt, abs, pow

    Examples:
    - "2 + 3 * 4" → 14
    - "sqrt(16)" → 4.0
    - "sin(3.14159/2)" → 1.0
    """

    # FastMCP 2.0 Context logging best practice
    await ctx.info(f"Calculating expression: {expression}")

    result = await evaluate_with_timeout(expression)
    timestamp = datetime.now().isoformat()
    difficulty = _classify_expression_difficulty(expression)

    # Add to calculation history
    history_entry = {
        "type": "calculation",
        "expression": expression,
        "result": result,
        "timestamp": timestamp,
    }
    ctx.request_context.lifespan_context.calculation_history.append(history_entry)

    # Return content with educational annotations
    return {
        "content": [
            {
                "type": "text",
                "text": f"**Calculation:** {expression} = {result}",
                "annotations": {
                    "difficulty": difficulty,
                    "topic": "arithmetic",
                    "timestamp": timestamp,
                },
            }
        ]
    }


@mcp.tool(
    annotations={"title": "Statistical Analysis", "readOnlyHint": True, "openWorldHint": False}
)
@validated_tool
async def statistics(
    numbers: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    operation: str,
    ctx: SkipValidation[Context],
) -> dict[str, Any]:
    """Perform statistical calculations on a list of numbers.

    Available operations: mean, median, mode, std_dev, variance
    """

    # Validate operation against whitelist
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(
            f"Invalid operation: {operation}. Allowed: {', '.join(sorted(ALLOWED_OPERATIONS))}"
        )

    # FastMCP 2.0 Context logging - demonstrates async operation with user feedback
    await ctx.info(f"Performing {operation} on {len(numbers)} data points")

    import statistics as stats  # Import with alias to avoid naming conflict

    if not numbers:
        raise ValueError("Cannot calculate statistics on empty list")

    operations = {
        "mean": stats.mean,
        "median": stats.median,
        "mode": stats.mode,
        "std_dev": lambda x: stats.stdev(x) if len(x) > 1 else 0,
        "variance": lambda x: stats.variance(x) if len(x) > 1 else 0,
    }

    result = operations[operation](numbers)
    # Ensure result is always a float for type safety
    # Since input is list[float], all results should be convertible to float
    result_float = float(result)  # type: ignore[arg-type]

    # Determine difficulty based on operation and data size
    difficulty = (
        "advanced"
        if operation in ["std_dev", "variance"]
        else "intermediate"
        if len(numbers) > 10
        else "basic"
    )

    return {
        "content": [
            {
                "type": "text",
                "text": f"**{operation.title()}** of {len(numbers)} numbers: {result_float}",
                "annotations": {
                    "difficulty": difficulty,
                    "topic": "statistics",
                    "operation": operation,
                    "sample_size": len(numbers),
                },
            }
        ]
    }


@mcp.tool()
async def compound_interest(
    principal: float,
    rate: float,
    time: float,
    compounds_per_year: int = 1,
    ctx: Context = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """Calculate compound interest for investments.

    Formula: A = P(1 + r/n)^(nt)
    Where:
    - P = principal amount
    - r = annual interest rate (as decimal)
    - n = number of times interest compounds per year
    - t = time in years
    """
    # FastMCP 2.0 Context logging - provides visibility into financial calculations
    if ctx:
        await ctx.info(
            f"Calculating compound interest: ${principal:,.2f} @ {rate * 100}% for {time} years"
        )

    if principal <= 0:
        raise ValueError("Principal must be greater than 0")
    if rate < 0:
        raise ValueError("Interest rate cannot be negative")
    if time <= 0:
        raise ValueError("Time must be greater than 0")
    if compounds_per_year <= 0:
        raise ValueError("Compounds per year must be greater than 0")

    # Calculate compound interest: A = P(1 + r/n)^(nt)
    final_amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)
    total_interest = final_amount - principal

    return {
        "content": [
            {
                "type": "text",
                "text": f"**Compound Interest Calculation:**\nPrincipal: ${principal:,.2f}\nFinal Amount: ${final_amount:,.2f}\nTotal Interest Earned: ${total_interest:,.2f}",
                "annotations": {
                    "difficulty": "intermediate",
                    "topic": "finance",
                    "formula": "A = P(1 + r/n)^(nt)",
                    "time_years": time,
                },
            }
        ]
    }


@mcp.tool()
async def convert_units(
    value: float,
    from_unit: str,
    to_unit: str,
    unit_type: str,
    ctx: Context = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """Convert between different units of measurement.

    Supported unit types:
    - length: mm, cm, m, km, in, ft, yd, mi
    - weight: g, kg, oz, lb
    - temperature: c, f, k (Celsius, Fahrenheit, Kelvin)
    """
    # FastMCP 2.0 Context logging - tracks conversion operations for educational purposes
    if ctx:
        await ctx.info(f"Converting {value} {from_unit} to {to_unit} ({unit_type})")

    # Conversion tables (to base units)
    conversions = {
        "length": {  # to millimeters
            "mm": 1,
            "cm": 10,
            "m": 1000,
            "km": 1000000,
            "in": 25.4,
            "ft": 304.8,
            "yd": 914.4,
            "mi": 1609344,
        },
        "weight": {  # to grams
            "g": 1,
            "kg": 1000,
            "oz": 28.35,
            "lb": 453.59,
        },
    }

    if unit_type == "temperature":
        result = convert_temperature(value, from_unit, to_unit)
    else:
        conversion_table = conversions.get(unit_type)
        if not conversion_table:
            raise ValueError(
                f"Unknown unit type '{unit_type}'. Available: length, weight, temperature"
            )

        from_factor = conversion_table.get(from_unit.lower())
        to_factor = conversion_table.get(to_unit.lower())

        if from_factor is None:
            raise ValueError(f"Unknown {unit_type} unit '{from_unit}'")
        if to_factor is None:
            raise ValueError(f"Unknown {unit_type} unit '{to_unit}'")

        # Convert: value → base unit → target unit
        base_value = value * from_factor
        result = base_value / to_factor

    return {
        "content": [
            {
                "type": "text",
                "text": f"**Unit Conversion:** {value} {from_unit} = {result:.4g} {to_unit}",
                "annotations": {
                    "difficulty": "basic",
                    "topic": "unit_conversion",
                    "conversion_type": unit_type,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                },
            }
        ]
    }


@mcp.tool(
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
    ctx: SkipValidation[Context],
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
    # Validate variable name for filesystem safety
    validate_variable_name(name)

    # FastMCP 2.0 Context logging
    await ctx.info(f"Saving calculation '{name}' = {result}")

    # Get educational metadata from expression classification
    difficulty = _classify_expression_difficulty(expression)
    topic = _classify_expression_topic(expression)

    metadata = {
        "difficulty": difficulty,
        "topic": topic,
        "session_id": id(ctx.request_context.lifespan_context),
    }

    # Save to persistent workspace
    from math_mcp.persistence.workspace import _workspace_manager

    result_data = _workspace_manager.save_variable(name, expression, result, metadata)

    # Also add to session history
    history_entry = {
        "type": "save_calculation",
        "name": name,
        "expression": expression,
        "result": result,
        "timestamp": datetime.now().isoformat(),
    }
    ctx.request_context.lifespan_context.calculation_history.append(history_entry)

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


@mcp.tool()
async def load_variable(name: str, ctx: Context) -> dict[str, Any]:
    """Load previously saved calculation result from workspace.

    Args:
        name: Variable name to load

    Examples:
        load_variable("portfolio_return")  # Returns saved calculation
        load_variable("circle_area")       # Access across sessions
    """
    # FastMCP 2.0 Context logging
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

    # Add to session history
    history_entry = {
        "type": "load_variable",
        "name": name,
        "expression": result_data["expression"],
        "result": result_data["result"],
        "timestamp": datetime.now().isoformat(),
    }
    ctx.request_context.lifespan_context.calculation_history.append(history_entry)

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


# === RESOURCES: DATA EXPOSURE ===


@mcp.resource("math://test")
async def simple_test(ctx: Context) -> str:
    """Simple test resource like FastMCP examples"""
    await ctx.info("Accessing test resource")
    return "Test resource working successfully!"


@mcp.resource(
    "math://constants/{constant}", annotations={"readOnlyHint": True, "idempotentHint": True}
)
def get_math_constant(constant: str) -> str:
    """Get mathematical constants like pi, e, golden ratio, etc."""
    constants = {
        "pi": {"value": math.pi, "description": "Ratio of circle's circumference to diameter"},
        "e": {"value": math.e, "description": "Euler's number, base of natural logarithm"},
        "golden_ratio": {"value": (1 + math.sqrt(5)) / 2, "description": "Golden ratio φ"},
        "euler_gamma": {"value": 0.5772156649015329, "description": "Euler-Mascheroni constant γ"},
        "sqrt2": {"value": math.sqrt(2), "description": "Square root of 2"},
        "sqrt3": {"value": math.sqrt(3), "description": "Square root of 3"},
    }

    if constant not in constants:
        available = ", ".join(constants.keys())
        return f"Unknown constant '{constant}'. Available constants: {available}"

    const_info = constants[constant]
    return f"{constant}: {const_info['value']}\nDescription: {const_info['description']}"


@mcp.resource("math://functions")
async def list_available_functions(ctx: Context) -> str:
    """List all available mathematical functions with examples and syntax help."""
    await ctx.info("Accessing function reference documentation")
    return """# Available Mathematical Functions

## Basic Functions
- **abs(x)**: Absolute value
  - Example: abs(-5) = 5.0

## Trigonometric Functions
- **sin(x)**: Sine (input in radians)
  - Example: sin(3.14159/2) ≈ 1.0
- **cos(x)**: Cosine (input in radians)
  - Example: cos(0) = 1.0
- **tan(x)**: Tangent (input in radians)
  - Example: tan(3.14159/4) ≈ 1.0

## Mathematical Functions
- **sqrt(x)**: Square root
  - Example: sqrt(16) = 4.0
- **log(x)**: Natural logarithm
  - Example: log(2.71828) ≈ 1.0
- **pow(x, y)**: x raised to the power of y
  - Example: pow(2, 3) = 8.0

## Usage Notes
- All functions use parentheses: function(parameter)
- Multi-parameter functions use commas: pow(base, exponent)
- Use operators for basic math: +, -, *, /, **
- Parentheses for grouping: (2 + 3) * 4

## Examples
- Simple: 2 + 3 * 4 = 14.0
- Functions: sqrt(16) + pow(2, 3) = 12.0
- Complex: sin(3.14159/2) + cos(0) = 2.0
"""


@mcp.resource("math://history")
async def get_calculation_history(ctx: Context) -> str:
    """Get the history of calculations performed across sessions."""
    await ctx.info("Accessing calculation history")
    from math_mcp.persistence.workspace import _workspace_manager

    # Get workspace history
    workspace_data = _workspace_manager._load_workspace()

    if not workspace_data.variables:
        return "No calculations in workspace yet. Use save_calculation() to persist calculations."

    history_text = "Calculation History (from workspace):\n\n"

    # Sort by timestamp to show chronological order
    variables = list(workspace_data.variables.items())
    variables.sort(key=lambda x: x[1].timestamp, reverse=True)

    for i, (name, var) in enumerate(variables[:10], 1):  # Show last 10
        history_text += f"{i}. {name}: {var.expression} = {var.result} (saved {var.timestamp})\n"

    if len(variables) > 10:
        history_text += f"\n... and {len(variables) - 10} more calculations"

    return history_text


@mcp.resource("math://workspace", annotations={"readOnlyHint": True, "idempotentHint": False})
async def get_workspace(ctx: Context) -> str:
    """Get persistent calculation workspace showing all saved variables.

    This resource displays the complete state of the persistent workspace,
    including all saved calculations, metadata, and statistics. The workspace
    survives server restarts and is accessible across different transport modes.
    """
    await ctx.info("Accessing persistent workspace")
    from math_mcp.persistence.workspace import _workspace_manager

    return _workspace_manager.get_workspace_summary()


# === PROMPTS: INTERACTION TEMPLATES ===


@mcp.prompt()
def math_tutor(topic: str, level: str = "intermediate", include_examples: bool = True) -> str:
    """Generate a math tutoring prompt for explaining concepts.

    Args:
        topic: Mathematical topic to explain (e.g., "derivatives", "statistics")
        level: Difficulty level (beginner, intermediate, advanced)
        include_examples: Whether to include worked examples
    """
    prompt = f"""You are an expert mathematics tutor. Please explain the concept of {topic} at a {level} level.

Please structure your explanation as follows:
1. **Definition**: Provide a clear, concise definition
2. **Key Concepts**: Break down the main ideas
3. **Applications**: Where this is used in real life
"""

    if include_examples:
        prompt += "4. **Worked Examples**: Provide 2-3 step-by-step examples\n"

    prompt += f"""
Make your explanation engaging and accessible for a {level} learner. Use analogies when helpful, and encourage questions.
"""

    return prompt


@mcp.prompt()
def formula_explainer(formula: str, context: str = "general mathematics") -> str:
    """Generate a prompt for explaining mathematical formulas in detail.

    Args:
        formula: The mathematical formula to explain (e.g., "A = πr²")
        context: The mathematical context (e.g., "geometry", "calculus", "statistics")
    """
    return f"""Please provide a comprehensive explanation of the formula: {formula}

Include the following in your explanation:

1. **What it represents**: What does this formula calculate or describe?
2. **Variable definitions**: Define each variable/symbol in the formula
3. **Context**: How this formula fits within {context}
4. **Step-by-step breakdown**: If the formula has multiple parts, explain each step
5. **Example calculation**: Show how to use the formula with specific numbers
6. **Real-world applications**: Where might someone use this formula?
7. **Common mistakes**: What errors do people often make when using this formula?

Make your explanation clear and educational, suitable for someone learning about {context}.
"""


# === AGENT CARD ENDPOINT ===


async def build_agent_card() -> AgentCard:
    """Build A2A v0.3 agent card with dynamic tool introspection.

    Introspects the MCP server's tools and builds a complete agent card
    that describes this server's capabilities, skills, and interfaces.
    This enables agent discovery and capability advertisement per A2A spec.

    Returns:
        AgentCard: Complete A2A v0.3 agent card with all required fields.
    """
    # Introspect tools from the MCP server
    tools = (await mcp.get_tools()).values()

    # Build skills from tools
    skills: list[AgentSkill] = []
    for tool in tools:
        skill = AgentSkill.model_validate(
            {
                "id": tool.name,
                "name": tool.name.replace("_", " ").title(),
                "description": tool.description or f"Tool: {tool.name}",
                "tags": ["mcp", "tool"],
                "inputModes": ["application/json"],
                "outputModes": ["application/json", "text/plain"],
            }
        )
        skills.append(skill)

    # Get dynamic version from package metadata
    try:
        version = pkg_version("math-mcp-learning-server")
    except PackageNotFoundError:
        # Fallback if package metadata is unavailable
        version = "0.10.3"

    # Build agent card with server metadata
    agent_card = AgentCard.model_validate(
        {
            "protocolVersion": "1.0",
            "name": "Math Learning Server",
            "description": "Educational MCP server demonstrating FastMCP 2.0 best practices for math operations, visualization, and persistent workspaces.",
            "version": version,
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False,
            },
            "defaultInputModes": ["application/json"],
            "defaultOutputModes": ["application/json", "text/plain", "image/png"],
            "skills": [s.model_dump(by_alias=True) for s in skills],
            "documentationUrl": "https://github.com/clouatre-labs/math-mcp-learning-server",
            "supportsExtendedAgentCard": False,
        }
    )

    return agent_card


# === A2A AGENT CARD ENDPOINT ===


@mcp.custom_route("/.well-known/agent-card.json", methods=["GET"])
async def agent_card_endpoint(request) -> JSONResponse:
    """Serve A2A v0.3 agent card for server discovery.

    This endpoint implements the A2A (Agent-to-Agent) v0.3 specification
    for agent discovery. It provides metadata about the MCP server's
    capabilities, skills, and interfaces in a standardized format.

    The response uses camelCase JSON serialization as required by the
    A2A specification, with Pydantic model_dump_json(by_alias=True).

    Args:
        request: Starlette Request object (unused but required by route handler).

    Returns:
        JSONResponse: A2A v0.3 agent card with server metadata and skills.
    """
    card = await build_agent_card()
    # Use model_dump with by_alias=True for camelCase JSON serialization
    return JSONResponse(card.model_dump(by_alias=True, mode="json"))


# === MAIN ENTRY POINT ===


def main() -> None:
    """Main entry point supporting multiple transports.

    Supports stdio, sse, and streamable-http transports. The A2A agent
    card endpoint is automatically registered via @mcp.custom_route()
    and available on all HTTP-based transports.
    """
    import sys
    from typing import Literal, cast

    # Parse command line arguments for transport type
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio"  # default
    if len(sys.argv) > 1:
        if sys.argv[1] in ["stdio", "sse", "streamable-http"]:
            transport = cast(Literal["stdio", "sse", "streamable-http"], sys.argv[1])

    # Run the MCP server with the specified transport
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()

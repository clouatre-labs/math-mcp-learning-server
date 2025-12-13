#!/usr/bin/env python3
"""
Math MCP Server - FastMCP 2.0 Implementation
Educational MCP server demonstrating all three MCP pillars: Tools, Resources, and Prompts.
Uses FastMCP 2.0 patterns with structured output and multi-transport support.
"""

import asyncio
import logging
import math
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
from fastmcp.server.middleware.rate_limiting import (
    RateLimitError,
    SlidingWindowRateLimitingMiddleware,
)
from pydantic import ConfigDict, Field, SkipValidation, field_validator, validate_call
from pydantic_settings import BaseSettings

# Import visualization functions (using absolute import for FastMCP Cloud compatibility)
from math_mcp import visualization

# Try importing numpy for matrix operations
try:
    import numpy as np
    import numpy.linalg as la

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    la = None  # type: ignore

# === CONFIGURATION MANAGEMENT ===


class MathMCPSettings(BaseSettings):
    """Environment-based configuration with automatic validation."""

    math_timeout: float = 5.0
    mcp_rate_limit_per_minute: int = Field(default=100, ge=0)
    max_expression_length: int = Field(default=500, ge=0)
    max_string_param_length: int = Field(default=100, ge=0)
    max_array_size: int = Field(default=10000, ge=0)
    max_groups_count: int = Field(default=100, ge=0)
    max_group_size: int = Field(default=1000, ge=0)
    max_variable_name_length: int = Field(default=50, ge=0)
    max_days_financial: int = Field(default=1000, ge=0)

    model_config = ConfigDict(env_prefix="", case_sensitive=False)

    @field_validator("math_timeout", mode="after")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Ensure timeout is positive."""
        if v <= 0:
            raise ValueError("math_timeout must be positive")
        return v


# Initialize settings from environment
settings = MathMCPSettings()

# Keep constants for backward compatibility
EXPRESSION_TIMEOUT_SECONDS = settings.math_timeout
RATE_LIMIT_PER_MINUTE = settings.mcp_rate_limit_per_minute

# === INPUT SIZE LIMITS ===

MAX_EXPRESSION_LENGTH = settings.max_expression_length
MAX_STRING_PARAM_LENGTH = settings.max_string_param_length
MAX_ARRAY_SIZE = settings.max_array_size
MAX_GROUPS_COUNT = settings.max_groups_count
MAX_GROUP_SIZE = settings.max_group_size
MAX_VARIABLE_NAME_LENGTH = settings.max_variable_name_length
MAX_DAYS_FINANCIAL = settings.max_days_financial

# Whitelist constants
ALLOWED_OPERATIONS = {"mean", "median", "mode", "std_dev", "variance"}
ALLOWED_TRENDS = {"bullish", "bearish", "volatile"}


# === CONSTANTS ===

MATH_FUNCTIONS_SINGLE = ["sin", "cos", "tan", "log", "sqrt", "abs"]
MATH_FUNCTIONS_ALL = {"sin", "cos", "tan", "log", "sqrt", "abs", "pow"}
DANGEROUS_PATTERNS = ["import", "exec", "__", "eval", "open", "file"]

TOPIC_KEYWORDS = {
    "finance": ["interest", "rate", "investment", "portfolio"],
    "geometry": ["pi", "radius", "area", "volume"],
    "trigonometry": ["sin", "cos", "tan"],
    "logarithms": ["log", "ln", "exp"],
}

TEMP_CONVERSIONS = {
    "c": {"f": lambda c: c * 9 / 5 + 32, "k": lambda c: c + 273.15},
    "f": {"c": lambda f: (f - 32) * 5 / 9, "k": lambda f: (f - 32) * 5 / 9 + 273.15},
    "k": {"c": lambda k: k - 273.15, "f": lambda k: (k - 273.15) * 9 / 5 + 32},
}


# === CUSTOM DECORATOR FOR TOOL VALIDATION ===


def validated_tool(func):
    """Apply Pydantic validation to tool functions with Context support."""
    return validate_call(config={"arbitrary_types_allowed": True})(func)


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


# === SECURITY: SAFE EXPRESSION EVALUATION ===


def _validate_expression_syntax(expression: str) -> None:
    """Provide specific error messages for common syntax errors."""
    clean_expr = expression.replace(" ", "").lower()

    # Check for common function syntax issues
    if "pow(" in clean_expr and "," not in clean_expr:
        raise ValueError(
            "Function 'pow()' requires two parameters: pow(base, exponent). Example: pow(2, 3)"
        )

    # Check for empty function calls (functions with no parameters)
    for func in MATH_FUNCTIONS_SINGLE:
        empty_call = f"{func}()"
        if empty_call in clean_expr:
            raise ValueError(f"Function '{func}()' requires one parameter. Example: {func}(3.14)")


def safe_eval_expression(expression: str) -> float:
    """Safely evaluate mathematical expressions with restricted scope."""
    # Validate syntax and provide helpful error messages
    _validate_expression_syntax(expression)

    # Remove whitespace
    clean_expr = expression.replace(" ", "")

    # Only allow safe characters (including comma for function parameters)
    allowed_chars = set("0123456789+-*/.(),e")

    # Security check - log and block dangerous patterns
    if any(pattern in clean_expr.lower() for pattern in DANGEROUS_PATTERNS):
        logging.warning(f"Security: Blocked unsafe expression attempt: {expression[:50]}...")
        raise ValueError(
            "Expression contains forbidden operations. Only mathematical expressions are allowed."
        )

    # Check for unsafe characters
    if not all(c in allowed_chars or c.isalpha() for c in clean_expr):
        raise ValueError(
            "Expression contains invalid characters. Use only numbers, +, -, *, /, (), and math functions."
        )

    # Replace math functions with safe alternatives
    safe_expr = clean_expr
    for func in MATH_FUNCTIONS_ALL:
        if func in clean_expr:
            if func != "abs":  # abs is built-in, others need math module
                safe_expr = safe_expr.replace(func, f"math.{func}")

    # Evaluate with restricted globals
    try:
        allowed_globals = {"__builtins__": {"abs": abs}, "math": math}
        result = eval(safe_expr, allowed_globals, {})
        return float(result)
    except ZeroDivisionError:
        raise ValueError("Mathematical error: Division by zero is undefined.")
    except OverflowError:
        raise ValueError("Mathematical error: Result is too large to compute.")
    except ValueError as e:
        if "math domain error" in str(e):
            raise ValueError(
                "Mathematical error: Invalid input for function (e.g., sqrt of negative number)."
            )
        raise ValueError(f"Mathematical expression error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Expression evaluation failed: {str(e)}")


async def evaluate_with_timeout(expression: str) -> float:
    """
    Safely evaluate mathematical expression with execution timeout.

    Prevents denial-of-service by ensuring expression evaluation completes
    within EXPRESSION_TIMEOUT_SECONDS. Wraps synchronous safe_eval_expression()
    in an async executor to allow timeout enforcement.

    This is an educational example of wrapping CPU-bound synchronous operations
    in async context using asyncio.wait_for() and loop.run_in_executor().

    Args:
        expression: Mathematical expression string to evaluate.

    Returns:
        float: Result of the expression evaluation.

    Raises:
        ValueError: If expression evaluation exceeds timeout or is invalid.
    """
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, safe_eval_expression, expression),
            timeout=EXPRESSION_TIMEOUT_SECONDS,
        )
    except TimeoutError as e:
        raise ValueError(
            f"Expression evaluation exceeded {EXPRESSION_TIMEOUT_SECONDS}s timeout. "
            f"Try simplifying the expression or breaking it into smaller parts."
        ) from e


# === CUSTOM VALIDATORS (for logic Field constraints can't handle) ===


def validate_variable_name(name: str) -> str:
    """Validate variable name for filesystem safety (alphanumeric + underscore/hyphen only)."""
    if not name.strip():
        raise ValueError("Variable name cannot be empty")
    if not name.replace("_", "").replace("-", "").isalnum():
        raise ValueError(
            "Variable name must contain only letters, numbers, underscores, and hyphens"
        )
    return name


def validate_nested_array_groups(groups: list[list[float]]) -> list[list[float]]:
    """Validate nested array group sizes."""
    for i, group in enumerate(groups):
        if len(group) > settings.max_group_size:
            raise ValueError(
                f"Group {i} exceeds maximum size of {settings.max_group_size} elements. "
                f"Current size: {len(group)}"
            )
    return groups


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin."""
    from_lower = from_unit.lower()
    to_lower = to_unit.lower()

    # Direct conversion if same unit
    if from_lower == to_lower:
        return value

    # Convert to Celsius first if not already
    if from_lower == "c":
        celsius = value
    elif from_lower in TEMP_CONVERSIONS:
        celsius = TEMP_CONVERSIONS[from_lower]["c"](value)
    else:
        raise ValueError(f"Unknown temperature unit '{from_unit}'")

    # Convert from Celsius to target
    if to_lower == "c":
        return celsius
    elif to_lower in TEMP_CONVERSIONS["c"]:
        return TEMP_CONVERSIONS["c"][to_lower](celsius)
    else:
        raise ValueError(f"Unknown temperature unit '{to_unit}'")


# === TOOLS: COMPUTATIONAL OPERATIONS ===


def _classify_expression_difficulty(expression: str) -> str:
    """Classify mathematical expression difficulty for educational annotations."""
    clean_expr = expression.replace(" ", "").lower()

    # Count complexity indicators
    has_functions = any(func in clean_expr for func in MATH_FUNCTIONS_ALL)
    has_parentheses = "(" in clean_expr
    has_exponents = "**" in clean_expr or "^" in clean_expr
    operator_count = sum(clean_expr.count(op) for op in "+-*/")

    if has_functions or has_exponents:
        return "advanced"
    elif has_parentheses or operator_count > 2:
        return "intermediate"
    else:
        return "basic"


def _classify_expression_topic(expression: str) -> str:
    """Enhanced topic classification for educational metadata."""
    clean_expr = expression.lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(word in clean_expr for word in keywords):
            return topic

    return "arithmetic"


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


@mcp.tool(annotations={"title": "Function Plotter", "readOnlyHint": False, "openWorldHint": False})
@validated_tool
async def plot_function(
    expression: Annotated[str, Field(max_length=MAX_EXPRESSION_LENGTH)],
    x_range: tuple[float, float],
    num_points: Annotated[int, Field(ge=2, le=MAX_ARRAY_SIZE)] = 100,
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Generate mathematical function plots (requires matplotlib).

    Args:
        expression: Mathematical expression to plot (e.g., "x**2", "sin(x)")
        x_range: Tuple of (min, max) for x-axis range
        num_points: Number of points to plot (default: 100)
        ctx: FastMCP context for logging

    Returns:
        Dict with base64-encoded PNG image or error message

    Examples:
        plot_function("x**2", (-5, 5))
        plot_function("sin(x)", (-3.14, 3.14))
    """

    # Try importing optional dependencies
    try:
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "**Matplotlib not available**\n\nInstall with: `pip install math-mcp-learning-server[plotting]`\n\nOr for development: `uv sync --extra plotting`",
                    "annotations": {
                        "error": "missing_dependency",
                        "install_command": "pip install math-mcp-learning-server[plotting]",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }

    # FastMCP 2.0 Context logging
    if ctx:
        await ctx.info(f"Plotting function: {expression} over range {x_range}")

    try:
        # Validate x_range
        x_min, x_max = x_range
        if x_min >= x_max:
            raise ValueError("x_range minimum must be less than maximum")
        if num_points < 2:
            raise ValueError("num_points must be at least 2")

        # Generate x values
        x_values = np.linspace(x_min, x_max, num_points)

        # Evaluate expression for each x value
        y_values = []
        for x in x_values:
            # Replace x in expression with actual value
            expr_with_value = expression.replace("x", f"({x})")
            try:
                y = await evaluate_with_timeout(expr_with_value)
                y_values.append(y)
            except ValueError:
                # Handle domain errors (like sqrt of negative) or timeout
                y_values.append(float("nan"))

        # Create figure and plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x_values, y_values, linewidth=2, color="#2E86AB")
        ax.set_xlabel("x", fontsize=12)
        ax.set_ylabel("f(x)", fontsize=12)
        ax.set_title(f"Plot of f(x) = {expression}", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color="k", linewidth=0.5)
        ax.axvline(x=0, color="k", linewidth=0.5)

        # Save to base64
        import base64
        from io import BytesIO

        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        # Classify difficulty
        difficulty = _classify_expression_difficulty(expression)

        return {
            "content": [
                {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": "image/png",
                    "annotations": {
                        "difficulty": difficulty,
                        "topic": "visualization",
                        "expression": expression,
                        "x_range": f"[{x_min}, {x_max}]",
                        "num_points": num_points,
                        "educational_note": "Function plotting visualizes mathematical relationships",
                    },
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Plot Error:** {str(e)}\n\nPlease check your expression and x_range values.",
                    "annotations": {
                        "error": "plot_error",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": {
                        "error": "unexpected_error",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }


@mcp.tool(
    annotations={"title": "Statistical Histogram", "readOnlyHint": False, "openWorldHint": False}
)
@validated_tool
async def create_histogram(
    data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    bins: int = 20,
    title: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Data Distribution",
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Create statistical histograms (requires matplotlib).

    Args:
        data: List of numerical values
        bins: Number of histogram bins (default: 20)
        title: Chart title
        ctx: FastMCP context for logging

    Returns:
        Dict with base64-encoded PNG image or error message

    Examples:
        create_histogram([1, 2, 2, 3, 3, 3, 4, 4, 5], bins=5)
    """
    if bins < 1:
        raise ValueError("bins must be at least 1")

    # Try importing optional dependencies
    try:
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy  # noqa: F401 - imported for side effects, required by matplotlib
    except ImportError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "**Matplotlib not available**\n\nInstall with: `pip install math-mcp-learning-server[plotting]`\n\nOr for development: `uv sync --extra plotting`",
                    "annotations": {
                        "error": "missing_dependency",
                        "install_command": "pip install math-mcp-learning-server[plotting]",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }

    # FastMCP 2.0 Context logging
    if ctx:
        await ctx.info(f"Creating histogram with {len(data)} data points and {bins} bins")

    try:
        # Validate inputs
        if not data:
            raise ValueError("Cannot create histogram with empty data")
        if len(data) == 1:
            raise ValueError("Histogram requires at least 2 data points")
        if bins < 1:
            raise ValueError("bins must be at least 1")

        # Calculate statistics
        import statistics as stats

        mean_val = stats.mean(data)
        median_val = stats.median(data)
        std_dev = stats.stdev(data) if len(data) > 1 else 0

        # Create histogram
        fig, ax = plt.subplots(figsize=(10, 6))
        n, bins_edges, patches = ax.hist(
            data, bins=bins, color="#A23B72", alpha=0.7, edgecolor="black"
        )

        # Add vertical lines for mean and median
        ax.axvline(
            mean_val, color="#F18F01", linestyle="--", linewidth=2, label=f"Mean: {mean_val:.2f}"
        )
        ax.axvline(
            median_val,
            color="#C73E1D",
            linestyle="-.",
            linewidth=2,
            label=f"Median: {median_val:.2f}",
        )

        ax.set_xlabel("Value", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        # Save to base64
        import base64
        from io import BytesIO

        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return {
            "content": [
                {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": "image/png",
                    "annotations": {
                        "difficulty": "intermediate",
                        "topic": "statistics",
                        "data_points": len(data),
                        "bins": bins,
                        "mean": round(mean_val, 4),
                        "median": round(median_val, 4),
                        "std_dev": round(std_dev, 4),
                        "educational_note": "Histograms show the distribution and frequency of data values",
                    },
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Histogram Error:** {str(e)}\n\nPlease check your data and parameters.",
                    "annotations": {
                        "error": "histogram_error",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": {
                        "error": "unexpected_error",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }


@mcp.tool(annotations={"title": "Line Chart", "readOnlyHint": False, "openWorldHint": False})
@validated_tool
async def plot_line_chart(
    x_data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    y_data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    title: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Line Chart",
    x_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "X",
    y_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Y",
    color: Annotated[str | None, Field(max_length=MAX_STRING_PARAM_LENGTH)] = None,
    show_grid: bool = True,
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Create a line chart from data points (requires matplotlib).

    Args:
        x_data: X-axis data points
        y_data: Y-axis data points
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Line color (name or hex code, e.g., 'blue', '#2E86AB')
        show_grid: Whether to show grid lines
        ctx: FastMCP context for logging

    Returns:
        Dict with base64-encoded PNG image or error message

    Examples:
        plot_line_chart([1, 2, 3, 4], [1, 4, 9, 16], title="Squares")
        plot_line_chart([0, 1, 2], [0, 1, 4], color='red', x_label='Time', y_label='Distance')
    """
    try:
        import matplotlib  # noqa: F401 - Check if available
    except ImportError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "**Matplotlib not available**\n\nInstall with: `pip install math-mcp-learning-server[plotting]`\n\nOr for development: `uv sync --extra plotting`",
                    "annotations": {
                        "error": "missing_dependency",
                        "install_command": "pip install math-mcp-learning-server[plotting]",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }

    if ctx:
        await ctx.info(f"Creating line chart with {len(x_data)} data points")

    try:
        image_base64 = visualization.create_line_chart(
            x_data=x_data,
            y_data=y_data,
            title=title,
            x_label=x_label,
            y_label=y_label,
            color=color,
            show_grid=show_grid,
        ).decode("utf-8")

        return {
            "content": [
                {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": "image/png",
                    "annotations": {
                        "difficulty": "intermediate",
                        "topic": "visualization",
                        "chart_type": "line",
                        "data_points": len(x_data),
                        "educational_note": "Line charts show trends and relationships between continuous data points",
                    },
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Line Chart Error:** {str(e)}\n\nPlease check that x_data and y_data have the same length and contain at least 2 points.",
                    "annotations": {
                        "error": "line_chart_error",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": {
                        "error": "unexpected_error",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }


@mcp.tool(annotations={"title": "Scatter Plot", "readOnlyHint": False, "openWorldHint": False})
@validated_tool
async def plot_scatter_chart(
    x_data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    y_data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    title: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Scatter Plot",
    x_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "X",
    y_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Y",
    color: Annotated[str | None, Field(max_length=MAX_STRING_PARAM_LENGTH)] = None,
    point_size: int = 50,
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Create a scatter plot from data points (requires matplotlib).

    Args:
        x_data: X-axis data points
        y_data: Y-axis data points
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Point color (name or hex code, e.g., 'blue', '#2E86AB')
        point_size: Size of scatter points (default: 50)
        ctx: FastMCP context for logging

    Returns:
        Dict with base64-encoded PNG image or error message

    Examples:
        plot_scatter_chart([1, 2, 3, 4], [1, 4, 9, 16], title="Correlation Study")
        plot_scatter_chart([1, 2, 3], [2, 4, 5], color='purple', point_size=100)
    """

    try:
        import matplotlib  # noqa: F401 - Check if available
    except ImportError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "**Matplotlib not available**\n\nInstall with: `pip install math-mcp-learning-server[plotting]`\n\nOr for development: `uv sync --extra plotting`",
                    "annotations": {
                        "error": "missing_dependency",
                        "install_command": "pip install math-mcp-learning-server[plotting]",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }

    if ctx:
        await ctx.info(f"Creating scatter plot with {len(x_data)} data points")

    try:
        image_base64 = visualization.create_scatter_plot(
            x_data=x_data,
            y_data=y_data,
            title=title,
            x_label=x_label,
            y_label=y_label,
            color=color,
            point_size=point_size,
        ).decode("utf-8")

        return {
            "content": [
                {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": "image/png",
                    "annotations": {
                        "difficulty": "intermediate",
                        "topic": "visualization",
                        "chart_type": "scatter",
                        "data_points": len(x_data),
                        "educational_note": "Scatter plots reveal correlations and patterns in paired data",
                    },
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Scatter Plot Error:** {str(e)}\n\nPlease check that x_data and y_data have the same length.",
                    "annotations": {
                        "error": "scatter_plot_error",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": {
                        "error": "unexpected_error",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }


@mcp.tool(annotations={"title": "Box Plot", "readOnlyHint": False, "openWorldHint": False})
@validated_tool
async def plot_box_plot(
    data_groups: Annotated[list[list[float]], Field(max_length=MAX_GROUPS_COUNT)],
    group_labels: Annotated[list[str] | None, Field(max_length=MAX_GROUPS_COUNT)] = None,
    title: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Box Plot",
    y_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Values",
    color: Annotated[str | None, Field(max_length=MAX_STRING_PARAM_LENGTH)] = None,
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Create a box plot for comparing distributions (requires matplotlib).

    Args:
        data_groups: List of data groups to compare
        group_labels: Labels for each group (optional)
        title: Chart title
        y_label: Y-axis label
        color: Box plot color (name or hex code, e.g., 'blue', '#2E86AB')
        ctx: FastMCP context for logging

    Returns:
        Dict with base64-encoded PNG image or error message

    Examples:
        plot_box_plot([[1, 2, 3, 4], [2, 3, 4, 5]], group_labels=['Group A', 'Group B'])
        plot_box_plot([[10, 20, 30], [15, 25, 35], [20, 30, 40]], color='green')
    """
    # Validate nested array group sizes
    validate_nested_array_groups(data_groups)

    try:
        import matplotlib  # noqa: F401 - Check if available
    except ImportError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "**Matplotlib not available**\n\nInstall with: `pip install math-mcp-learning-server[plotting]`\n\nOr for development: `uv sync --extra plotting`",
                    "annotations": {
                        "error": "missing_dependency",
                        "install_command": "pip install math-mcp-learning-server[plotting]",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }

    if ctx:
        await ctx.info(f"Creating box plot with {len(data_groups)} groups")

    try:
        image_base64 = visualization.create_box_plot(
            data_groups=data_groups,
            group_labels=group_labels,
            title=title,
            y_label=y_label,
            color=color,
        ).decode("utf-8")

        return {
            "content": [
                {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": "image/png",
                    "annotations": {
                        "difficulty": "advanced",
                        "topic": "statistics",
                        "chart_type": "box_plot",
                        "groups": len(data_groups),
                        "educational_note": "Box plots display distribution quartiles, median, and outliers for comparison",
                    },
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Box Plot Error:** {str(e)}\n\nPlease check that data_groups is not empty and all groups contain at least one value.",
                    "annotations": {
                        "error": "box_plot_error",
                        "difficulty": "advanced",
                        "topic": "statistics",
                    },
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": {
                        "error": "unexpected_error",
                        "difficulty": "advanced",
                        "topic": "statistics",
                    },
                }
            ]
        }


@mcp.tool(
    annotations={"title": "Financial Line Chart", "readOnlyHint": False, "openWorldHint": False}
)
@validated_tool
async def plot_financial_line(
    days: Annotated[int, Field(ge=2, le=MAX_DAYS_FINANCIAL)] = 30,
    trend: str = "bullish",
    start_price: float = 100.0,
    color: Annotated[str | None, Field(max_length=MAX_STRING_PARAM_LENGTH)] = None,
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Generate and plot synthetic financial price data (requires matplotlib).

    Creates realistic price movement patterns for educational purposes.
    Does not use real market data.

    Args:
        days: Number of days to generate (default: 30)
        trend: Market trend ('bullish', 'bearish', or 'volatile')
        start_price: Starting price value (default: 100.0)
        color: Line color (name or hex code, e.g., 'blue', '#2E86AB')
        ctx: FastMCP context for logging

    Returns:
        Dict with base64-encoded PNG image or error message

    Examples:
        plot_financial_line(days=60, trend='bullish')
        plot_financial_line(days=90, trend='volatile', start_price=150.0, color='orange')
    """
    # Validate trend against whitelist
    if trend not in ALLOWED_TRENDS:
        raise ValueError(f"Invalid trend: {trend}. Allowed: {', '.join(sorted(ALLOWED_TRENDS))}")

    try:
        import matplotlib  # noqa: F401 - Check if available
    except ImportError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "**Matplotlib not available**\n\nInstall with: `pip install math-mcp-learning-server[plotting]`\n\nOr for development: `uv sync --extra plotting`",
                    "annotations": {
                        "error": "missing_dependency",
                        "install_command": "pip install math-mcp-learning-server[plotting]",
                        "difficulty": "intermediate",
                        "topic": "visualization",
                    },
                }
            ]
        }

    if ctx:
        await ctx.info(f"Generating synthetic {trend} price data for {days} days")

    try:
        # Validate trend parameter
        if trend not in ["bullish", "bearish", "volatile"]:
            raise ValueError("trend must be 'bullish', 'bearish', or 'volatile'")

        # Generate synthetic data
        dates, prices = visualization.generate_synthetic_price_data(
            days=days,
            trend=trend,  # type: ignore
            start_price=start_price,
        )

        # Create financial chart
        image_base64 = visualization.create_financial_line_chart(
            dates=dates,
            prices=prices,
            title=f"Synthetic {trend.capitalize()} Price Movement ({days} days)",
            y_label="Price ($)",
            color=color,
        ).decode("utf-8")

        # Calculate statistics
        import statistics as stats

        price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
        volatility = stats.stdev(prices) if len(prices) > 1 else 0

        return {
            "content": [
                {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": "image/png",
                    "annotations": {
                        "difficulty": "advanced",
                        "topic": "financial_analysis",
                        "chart_type": "financial_line",
                        "days": days,
                        "trend": trend,
                        "start_price": round(start_price, 2),
                        "end_price": round(prices[-1], 2),
                        "price_change_percent": round(price_change, 2),
                        "volatility": round(volatility, 2),
                        "educational_note": "Synthetic data generated for educational purposes only - not real market data",
                    },
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Financial Chart Error:** {str(e)}\n\nPlease check your parameters (days >= 2, valid trend, positive start_price).",
                    "annotations": {
                        "error": "financial_chart_error",
                        "difficulty": "advanced",
                        "topic": "financial_analysis",
                    },
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": {
                        "error": "unexpected_error",
                        "difficulty": "advanced",
                        "topic": "financial_analysis",
                    },
                }
            ]
        }


# === MATRIX OPERATIONS (requires numpy) ===


def _check_numpy_available() -> None:
    """Check if numpy is available and raise error if not."""
    if not NUMPY_AVAILABLE:
        raise ValueError(
            "NumPy is required for matrix operations. "
            "Install with: pip install math-mcp-learning-server[scientific]"
        )


def _validate_matrix(matrix: list[list[float]], max_size: int = 100) -> Any:
    """Validate matrix input and convert to numpy array.

    Args:
        matrix: Input matrix as list of lists
        max_size: Maximum dimension size (prevents DoS)

    Returns:
        numpy.ndarray: Validated matrix

    Raises:
        ValueError: If matrix is invalid
    """
    _check_numpy_available()

    if not matrix:
        raise ValueError("Matrix cannot be empty")

    if not all(isinstance(row, list) for row in matrix):
        raise ValueError("Matrix must be a list of lists")

    row_lengths = [len(row) for row in matrix]
    if len(set(row_lengths)) > 1:
        raise ValueError("All matrix rows must have the same length")

    if not all(isinstance(val, (int, float)) for row in matrix for val in row):
        raise ValueError("All matrix elements must be numeric (int or float)")

    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0

    if rows > max_size or cols > max_size:
        raise ValueError(
            f"Matrix dimensions ({rows}x{cols}) exceed maximum size ({max_size}x{max_size})"
        )

    return np.array(matrix, dtype=float)


def _format_matrix(matrix_array: Any) -> str:
    """Format numpy array as readable string.

    Args:
        matrix_array: numpy array to format

    Returns:
        str: Formatted matrix string
    """
    return np.array2string(matrix_array, precision=4, suppress_small=True)


@mcp.tool()
async def matrix_multiply(
    matrix_a: list[list[float]],
    matrix_b: list[list[float]],
    ctx: Context = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """Multiply two matrices using NumPy.

    Args:
        matrix_a: First matrix (m x n)
        matrix_b: Second matrix (n x p)

    Returns:
        Result matrix (m x p)

    Raises:
        ValueError: If matrices have incompatible dimensions

    Examples:
        matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
        matrix_multiply([[1, 2, 3]], [[1], [2], [3]])
    """
    if ctx:
        await ctx.info("Performing matrix multiplication")

    try:
        mat_a = _validate_matrix(matrix_a)
        mat_b = _validate_matrix(matrix_b)

        if mat_a.shape[1] != mat_b.shape[0]:
            raise ValueError(
                f"Incompatible matrix dimensions for multiplication: "
                f"({mat_a.shape[0]}x{mat_a.shape[1]}) × ({mat_b.shape[0]}x{mat_b.shape[1]}). "
                f"Number of columns in first matrix must equal number of rows in second matrix."
            )

        result = np.matmul(mat_a, mat_b)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Matrix Multiplication Result:**\n{_format_matrix(result)}",
                    "annotations": {
                        "difficulty": "intermediate",
                        "topic": "linear_algebra",
                        "operation": "matrix_multiply",
                        "result_shape": f"{result.shape[0]}x{result.shape[1]}",
                    },
                }
            ]
        }

    except ValueError as e:
        raise ToolError(f"Matrix multiplication error: {str(e)}")


@mcp.tool()
async def matrix_transpose(
    matrix: list[list[float]],
    ctx: Context = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """Transpose a matrix (swap rows and columns).

    Args:
        matrix: Input matrix

    Returns:
        Transposed matrix

    Examples:
        matrix_transpose([[1, 2, 3], [4, 5, 6]])  # Returns [[1, 4], [2, 5], [3, 6]]
        matrix_transpose([[1, 2], [3, 4]])
    """
    if ctx:
        await ctx.info("Performing matrix transpose")

    try:
        mat = _validate_matrix(matrix)
        result = np.transpose(mat)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Matrix Transpose Result:**\n{_format_matrix(result)}",
                    "annotations": {
                        "difficulty": "basic",
                        "topic": "linear_algebra",
                        "operation": "matrix_transpose",
                        "result_shape": f"{result.shape[0]}x{result.shape[1]}",
                    },
                }
            ]
        }

    except ValueError as e:
        raise ToolError(f"Matrix transpose error: {str(e)}")


@mcp.tool()
async def matrix_determinant(
    matrix: list[list[float]],
    ctx: Context = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """Calculate the determinant of a square matrix.

    Args:
        matrix: Square matrix (n x n)

    Returns:
        Determinant value

    Raises:
        ValueError: If matrix is not square

    Examples:
        matrix_determinant([[4, 6], [3, 8]])  # Returns 14
        matrix_determinant([[1, 2], [2, 4]])  # Returns 0 (singular)
    """
    if ctx:
        await ctx.info("Calculating matrix determinant")

    try:
        mat = _validate_matrix(matrix)

        if mat.shape[0] != mat.shape[1]:
            raise ValueError(
                f"Determinant requires a square matrix. "
                f"Got {mat.shape[0]}x{mat.shape[1]} matrix instead."
            )

        det = la.det(mat)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Matrix Determinant:** {det:.6g}",
                    "annotations": {
                        "difficulty": "intermediate",
                        "topic": "linear_algebra",
                        "operation": "matrix_determinant",
                        "matrix_size": f"{mat.shape[0]}x{mat.shape[1]}",
                    },
                }
            ]
        }

    except ValueError as e:
        raise ToolError(f"Matrix determinant error: {str(e)}")


@mcp.tool()
async def matrix_inverse(
    matrix: list[list[float]],
    ctx: Context = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """Calculate the inverse of a square matrix.

    Args:
        matrix: Square matrix (n x n)

    Returns:
        Inverse matrix

    Raises:
        ValueError: If matrix is not square or is singular

    Examples:
        matrix_inverse([[4, 7], [2, 6]])
        matrix_inverse([[1, 0], [0, 1]])  # Identity matrix
    """
    if ctx:
        await ctx.info("Calculating matrix inverse")

    try:
        mat = _validate_matrix(matrix)

        if mat.shape[0] != mat.shape[1]:
            raise ValueError(
                f"Matrix inverse requires a square matrix. "
                f"Got {mat.shape[0]}x{mat.shape[1]} matrix instead."
            )

        try:
            result = la.inv(mat)
        except la.LinAlgError:
            raise ValueError(
                "Matrix is singular and cannot be inverted. "
                "Determinant is zero or matrix is not invertible."
            )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Matrix Inverse Result:**\n{_format_matrix(result)}",
                    "annotations": {
                        "difficulty": "advanced",
                        "topic": "linear_algebra",
                        "operation": "matrix_inverse",
                        "matrix_size": f"{mat.shape[0]}x{mat.shape[1]}",
                    },
                }
            ]
        }

    except ValueError as e:
        raise ToolError(f"Matrix inverse error: {str(e)}")


@mcp.tool()
async def matrix_eigenvalues(
    matrix: list[list[float]],
    ctx: Context = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """Calculate the eigenvalues of a square matrix.

    Args:
        matrix: Square matrix (n x n)

    Returns:
        List of eigenvalues (may be complex numbers)

    Raises:
        ValueError: If matrix is not square

    Examples:
        matrix_eigenvalues([[4, 2], [1, 3]])
        matrix_eigenvalues([[3, 0, 0], [0, 5, 0], [0, 0, 7]])  # Diagonal matrix
    """
    if ctx:
        await ctx.info("Calculating matrix eigenvalues")

    try:
        mat = _validate_matrix(matrix)

        if mat.shape[0] != mat.shape[1]:
            raise ValueError(
                f"Eigenvalues require a square matrix. "
                f"Got {mat.shape[0]}x{mat.shape[1]} matrix instead."
            )

        eigenvalues = la.eigvals(mat)

        # Format eigenvalues (handle complex numbers)
        def _format_complex_eigenvalue(val: Any) -> str:
            """Format complex eigenvalue avoiding +- for negative imaginary parts."""
            if np.isreal(val):
                return f"{val.real:.6g}"
            elif val.imag >= 0:
                return f"{val.real:.6g}+{val.imag:.6g}j"
            else:
                return f"{val.real:.6g}{val.imag:.6g}j"  # negative sign already in val.imag

        eigenval_str = ", ".join([_format_complex_eigenvalue(val) for val in eigenvalues])

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Matrix Eigenvalues:** [{eigenval_str}]",
                    "annotations": {
                        "difficulty": "advanced",
                        "topic": "linear_algebra",
                        "operation": "matrix_eigenvalues",
                        "matrix_size": f"{mat.shape[0]}x{mat.shape[1]}",
                        "count": len(eigenvalues),
                    },
                }
            ]
        }

    except ValueError as e:
        raise ToolError(f"Matrix eigenvalues error: {str(e)}")


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


# === MAIN ENTRY POINT ===


def main() -> None:
    """Main entry point supporting multiple transports."""
    import sys
    from typing import Literal, cast

    # Parse command line arguments for transport type
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio"  # default
    if len(sys.argv) > 1:
        if sys.argv[1] in ["stdio", "sse", "streamable-http"]:
            transport = cast(Literal["stdio", "sse", "streamable-http"], sys.argv[1])

    # Run with specified transport
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()

"""
Calculate Tools Sub-Server
FastMCP sub-server for mathematical calculations, statistics, and unit conversions.
"""

from typing import Annotated, Any, cast

from fastmcp import Context, FastMCP
from pydantic import Field, SkipValidation

from math_mcp.eval import (
    _classify_expression_difficulty,
    convert_temperature,
    evaluate_with_timeout,
)
from math_mcp.settings import (
    ALLOWED_OPERATIONS,
    MAX_ARRAY_SIZE,
    MAX_EXPRESSION_LENGTH,
    validated_tool,
)

# Create sub-server for calculation tools
calculate_mcp = FastMCP(name="Calculate Tools")


@calculate_mcp.tool(
    annotations={"title": "Mathematical Calculator", "readOnlyHint": False, "openWorldHint": True}
)
@validated_tool
async def calculate(
    expression: Annotated[str, Field(max_length=MAX_EXPRESSION_LENGTH)],
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Safely evaluate mathematical expressions with support for basic operations and math functions.

    Supported operations: +, -, *, /, **, ()
    Supported functions: sin, cos, tan, log, sqrt, abs, pow

    Examples:
    - "2 + 3 * 4" → 14
    - "sqrt(16)" → 4.0
    - "sin(3.14159/2)" → 1.0
    """
    from datetime import datetime

    if ctx:
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
    if ctx and ctx.lifespan_context:
        cast(Any, ctx.lifespan_context).calculation_history.append(history_entry)

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


@calculate_mcp.tool(
    annotations={"title": "Statistical Analysis", "readOnlyHint": True, "openWorldHint": False}
)
@validated_tool
async def statistics(
    numbers: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    operation: str,
    ctx: SkipValidation[Context | None] = None,
) -> dict[str, Any]:
    """Perform statistical calculations on a list of numbers.

    Available operations: mean, median, mode, std_dev, variance
    """
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(
            f"Invalid operation: {operation}. Allowed: {', '.join(sorted(ALLOWED_OPERATIONS))}"
        )

    if ctx:
        await ctx.info(f"Performing {operation} on {len(numbers)} data points")

    import statistics as stats

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
    result_float = float(result)

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


@calculate_mcp.tool()
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


@calculate_mcp.tool()
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
    if ctx:
        await ctx.info(f"Converting {value} {from_unit} to {to_unit} ({unit_type})")

    conversions = {
        "length": {
            "mm": 1,
            "cm": 10,
            "m": 1000,
            "km": 1000000,
            "in": 25.4,
            "ft": 304.8,
            "yd": 914.4,
            "mi": 1609344,
        },
        "weight": {
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

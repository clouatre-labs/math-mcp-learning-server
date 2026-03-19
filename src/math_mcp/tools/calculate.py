"""
Calculate Tools Sub-Server
FastMCP sub-server for mathematical calculations, statistics, and unit conversions.
"""

from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field, SkipValidation

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


class CalculationResult(BaseModel):
    """Result of a mathematical expression evaluation."""

    expression: str
    result: float
    difficulty: str
    topic: str


class StatisticsResult(BaseModel):
    """Result of statistical calculation."""

    operation: str
    result: float
    sample_size: int
    difficulty: str
    topic: str


class CompoundInterestResult(BaseModel):
    """Result of compound interest calculation."""

    principal: float
    final_amount: float
    total_interest: float
    rate: float
    time: float
    compounds_per_year: int
    difficulty: str
    topic: str
    formula: str


class UnitConversionResult(BaseModel):
    """Result of unit conversion."""

    value: float
    from_unit: str
    to_unit: str
    converted_value: float
    unit_type: str
    difficulty: str
    topic: str


# Create sub-server for calculation tools
calculate_mcp = FastMCP(name="Calculate Tools")


@calculate_mcp.tool(
    annotations={
        "title": "Mathematical Calculator",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    }
)
@validated_tool
async def calculate(
    expression: Annotated[str, Field(max_length=MAX_EXPRESSION_LENGTH)],
    ctx: SkipValidation[Context | None] = None,
) -> CalculationResult:
    """Safely evaluate mathematical expressions with support for basic operations and math functions.

    Supported operations: +, -, *, /, **, ()
    Supported functions: sin, cos, tan, log, sqrt, abs, pow

    Examples:
    - "2 + 3 * 4" → 14
    - "sqrt(16)" → 4.0
    - "sin(3.14159/2)" → 1.0
    """
    if ctx:
        await ctx.info(f"Calculating expression: {expression}")

    result = await evaluate_with_timeout(expression)
    difficulty = _classify_expression_difficulty(expression)

    return CalculationResult(
        expression=expression,
        result=result,
        difficulty=difficulty,
        topic="arithmetic",
    )


@calculate_mcp.tool(
    annotations={
        "title": "Statistical Analysis",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    }
)
@validated_tool
async def statistics(
    numbers: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    operation: str,
    ctx: SkipValidation[Context | None] = None,
) -> StatisticsResult:
    """Perform statistical calculations on a list of numbers.

    Available operations: mean, median, mode, std_dev, variance
    """
    if operation not in ALLOWED_OPERATIONS:
        if ctx:
            await ctx.warning(f"Invalid operation requested: {operation}")
        raise ValueError(
            f"Invalid operation: {operation}. Allowed: {', '.join(sorted(ALLOWED_OPERATIONS))}"
        )

    if ctx:
        await ctx.report_progress(0, 2, "Validating input")

    if ctx:
        await ctx.info(f"Performing {operation} on {len(numbers)} data points")

    import statistics as stats

    if not numbers:
        if ctx:
            await ctx.warning("Cannot calculate statistics on empty list")
        raise ValueError("Cannot calculate statistics on empty list")

    if ctx:
        await ctx.report_progress(1, 2, "Computing statistics")

    operations = {
        "mean": stats.mean,
        "median": stats.median,
        "mode": stats.mode,
        "std_dev": lambda x: stats.stdev(x) if len(x) > 1 else 0,
        "variance": lambda x: stats.variance(x) if len(x) > 1 else 0,
    }

    result = operations[operation](numbers)
    result_float = float(result)

    if ctx:
        await ctx.report_progress(2, 2, "Complete")

    difficulty = (
        "advanced"
        if operation in ["std_dev", "variance"]
        else "intermediate"
        if len(numbers) > 10
        else "basic"
    )

    return StatisticsResult(
        operation=operation,
        result=result_float,
        sample_size=len(numbers),
        difficulty=difficulty,
        topic="statistics",
    )


@calculate_mcp.tool(
    annotations={
        "title": "Compound Interest Calculator",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    }
)
@validated_tool
async def compound_interest(
    principal: float,
    rate: float,
    time: float,
    compounds_per_year: int = 1,
    ctx: SkipValidation[Context | None] = None,
) -> CompoundInterestResult:
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
        if ctx:
            await ctx.warning(f"Invalid principal: {principal}")
        raise ValueError("Principal must be greater than 0")
    if rate < 0:
        if ctx:
            await ctx.warning(f"Negative rate: {rate}")
        raise ValueError("Interest rate cannot be negative")
    if rate > 1.0:
        if ctx:
            await ctx.warning(f"rate {rate} looks like a percentage not a decimal")
        raise ValueError(
            f"rate must be a decimal between 0.0 and 1.0 (e.g., 0.05 for 5%). "
            f"Got {rate}. Did you mean {rate / 100:.4f}?"
        )
    if time <= 0:
        if ctx:
            await ctx.warning(f"Invalid time: {time}")
        raise ValueError("Time must be greater than 0")
    if compounds_per_year <= 0:
        if ctx:
            await ctx.warning(f"Invalid compounds_per_year: {compounds_per_year}")
        raise ValueError("Compounds per year must be greater than 0")

    final_amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)
    total_interest = final_amount - principal

    return CompoundInterestResult(
        principal=principal,
        final_amount=final_amount,
        total_interest=total_interest,
        rate=rate,
        time=time,
        compounds_per_year=compounds_per_year,
        difficulty="intermediate",
        topic="finance",
        formula="A = P(1 + r/n)^(nt)",
    )


@calculate_mcp.tool(
    annotations={
        "title": "Unit Converter",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    }
)
@validated_tool
async def convert_units(
    value: float,
    from_unit: str,
    to_unit: str,
    unit_type: str,
    ctx: SkipValidation[Context | None] = None,
) -> UnitConversionResult:
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
            if ctx:
                await ctx.warning(f"Unknown unit type requested: {unit_type}")
            raise ValueError(
                f"Unknown unit type '{unit_type}'. Available: length, weight, temperature"
            )

        from_factor = conversion_table.get(from_unit.lower())
        to_factor = conversion_table.get(to_unit.lower())

        if from_factor is None:
            if ctx:
                await ctx.warning(f"Unknown {unit_type} unit: {from_unit}")
            raise ValueError(f"Unknown {unit_type} unit '{from_unit}'")
        if to_factor is None:
            if ctx:
                await ctx.warning(f"Unknown {unit_type} unit: {to_unit}")
            raise ValueError(f"Unknown {unit_type} unit '{to_unit}'")

        base_value = value * from_factor
        result = base_value / to_factor

    return UnitConversionResult(
        value=value,
        from_unit=from_unit,
        to_unit=to_unit,
        converted_value=result,
        unit_type=unit_type,
        difficulty="basic",
        topic="unit_conversion",
    )

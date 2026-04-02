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
    name="calc_expression",
    annotations={
        "title": "Mathematical Calculator",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    },
)
@validated_tool
async def calc_expression(
    expression: Annotated[
        str,
        Field(
            max_length=MAX_EXPRESSION_LENGTH,
            description="Mathematical expression to evaluate. Supports +, -, *, /, **, and math functions (sin, cos, sqrt, log, etc.). Example: '2 * sin(pi/4) + sqrt(16)'",
        ),
    ],
    ctx: SkipValidation[Context | None] = None,
) -> CalculationResult:
    """Safely evaluate mathematical expressions with support for basic operations and math functions.

    Supported operations: +, -, *, /, **, ()
    Supported functions: sin, cos, tan, log, sqrt, abs, pow

    Note:
        Use this tool to evaluate a single mathematical expression. To compute descriptive statistics over a list of numbers, use the statistics tool instead.

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
    name="calc_statistics",
    annotations={
        "title": "Statistical Analysis",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    },
)
@validated_tool
async def calc_statistics(
    numbers: Annotated[
        list[float],
        Field(
            max_length=MAX_ARRAY_SIZE,
            description="List of numbers to compute descriptive statistics on. Example: [1.0, 2.5, 3.0, 4.5, 5.0]",
        ),
    ],
    operation: Annotated[
        str,
        Field(
            description="Statistical operation to perform. Allowed values: mean, median, mode, std_dev, variance",
            examples=["mean", "median", "mode", "std_dev", "variance"],
        ),
    ],
    ctx: SkipValidation[Context | None] = None,
) -> StatisticsResult:
    """Perform statistical calculations on a list of numbers.

    Available operations: mean, median, mode, std_dev, variance

    Note:
        Use this tool to compute descriptive statistics over a list of numbers. To evaluate a single mathematical expression, use the calculate tool instead.

    Examples:
        statistics([1.0, 2.5, 3.0, 4.5, 5.0], "mean")  # Returns 3.2
        statistics([1.0, 2.5, 3.0, 4.5, 5.0], "std_dev")  # Returns ~1.58
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
    name="calc_interest",
    annotations={
        "title": "Compound Interest Calculator",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    },
)
@validated_tool
async def calc_interest(
    principal: Annotated[
        float,
        Field(gt=0, description="Initial investment amount in dollars (must be > 0), e.g. 1000.0"),
    ],
    rate: Annotated[
        float,
        Field(
            ge=0,
            le=1.0,
            description="Annual interest rate as decimal 0.0-1.0 (e.g. 0.05 = 5%). If entering a percentage, divide by 100 first.",
        ),
    ],
    time: Annotated[
        float,
        Field(gt=0, description="Investment time in years (must be > 0), e.g. 10.0"),
    ],
    compounds_per_year: Annotated[
        int,
        Field(
            gt=0,
            description="Compounding frequency per year (must be > 0): 12=monthly, 365=daily",
        ),
    ] = 12,
    ctx: SkipValidation[Context | None] = None,
) -> CompoundInterestResult:
    """Calculate compound interest for investments.

    Formula: A = P(1 + r/n)^(nt)
    Where:
    - P = principal amount
    - r = annual interest rate (as decimal)
    - n = number of times interest compounds per year
    - t = time in years

    Examples:
        compound_interest(10000, 0.05, 5)  # $10,000 at 5% for 5 years → $12,762.82
        compound_interest(5000, 0.03, 10, 12)  # $5,000 at 3% compounded monthly → $6,744.25
    """
    if ctx:
        await ctx.info(
            f"Calculating compound interest: ${principal:,.2f} @ {rate * 100}% for {time} years"
        )

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
    name="calc_units",
    annotations={
        "title": "Unit Converter",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True,
    },
)
@validated_tool
async def calc_units(
    value: Annotated[float, Field(description="Numeric value to convert, e.g., 100.0")],
    from_unit: Annotated[
        str,
        Field(
            description="Source unit abbreviation. Valid units depend on unit_type: length (mm, cm, m, km, in, ft, yd, mi), weight (g, kg, oz, lb), temperature (c, f, k)",
            examples=["m", "kg", "c"],
        ),
    ],
    to_unit: Annotated[
        str,
        Field(
            description="Target unit abbreviation. Valid units depend on unit_type: length (mm, cm, m, km, in, ft, yd, mi), weight (g, kg, oz, lb), temperature (c, f, k)",
            examples=["ft", "lb", "f"],
        ),
    ],
    unit_type: Annotated[
        str,
        Field(
            description="Unit category: length, weight, or temperature",
            examples=["length", "weight", "temperature"],
        ),
    ],
    ctx: SkipValidation[Context | None] = None,
) -> UnitConversionResult:
    """Convert between different units of measurement.

    Supported unit types:
    - length: mm, cm, m, km, in, ft, yd, mi
    - weight: g, kg, oz, lb
    - temperature: c, f, k (Celsius, Fahrenheit, Kelvin)

    Examples:
        convert_units(5, "km", "mi", "length")  # 5 kilometers → 3.11 miles
        convert_units(150, "lb", "kg", "weight")  # 150 pounds → 68.04 kilograms
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

"""Visualization MCP tools for mathematical plotting and charting.

Extracted from server.py as part of the monolith decomposition (#140c).
Each tool generates PNG images using matplotlib and returns Image objects.
"""

import re
from functools import wraps
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from fastmcp.utilities.types import Image
from pydantic import BaseModel, Field, SkipValidation

from math_mcp import visualization
from math_mcp.eval import evaluate_with_timeout
from math_mcp.settings import (
    ALLOWED_TRENDS,
    MAX_ARRAY_SIZE,
    MAX_DAYS_FINANCIAL,
    MAX_EXPRESSION_LENGTH,
    MAX_GROUP_SIZE,
    MAX_GROUPS_COUNT,
    MAX_STRING_PARAM_LENGTH,
    validated_tool,
)

# --- Sub-server instance ---
visualization_mcp = FastMCP("visualization-tools")


# --- Result Models ---


class VisualizationError(BaseModel):
    """Structured error result for visualization tools.

    Used when visualization operations fail, providing typed error information
    for MCP clients instead of unstructured text responses.
    """

    message: str
    error_type: str
    difficulty: str = "intermediate"
    topic: str = "visualization"


# --- Helpers ---


def requires_matplotlib(func: Any) -> Any:
    """Decorator ensuring matplotlib is available before running visualization tools.

    Calls visualization._setup_matplotlib() to check availability.
    Returns a standardized error response if matplotlib is not installed,
    eliminating duplicated import/error-handling code across 6 tools.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Image | VisualizationError:
        try:
            visualization._setup_matplotlib()
        except ImportError:
            return VisualizationError(
                message=(
                    "**Matplotlib not available**\n\n"
                    "Install with: `pip install math-mcp-learning-server[plotting]`\n\n"
                    "Or for development: `uv sync --extra plotting`"
                ),
                error_type="missing_dependency",
            )
        return await func(*args, **kwargs)

    return wrapper


def validate_nested_array_groups(
    groups: list[list[float]],
) -> VisualizationError | None:
    """Validate nested array group sizes.

    Returns a VisualizationError if any group exceeds MAX_GROUP_SIZE, else None.
    """
    for i, group in enumerate(groups):
        if len(group) > MAX_GROUP_SIZE:
            return VisualizationError(
                message=(
                    f"Group {i} exceeds maximum size of {MAX_GROUP_SIZE} elements. "
                    f"Current size: {len(group)}"
                ),
                error_type="validation_error",
            )
    return None


def _validate_plot_range(x_range: tuple[float, float], num_points: int) -> tuple[float, float]:
    """Validate plot range and return (x_min, x_max)."""
    x_min, x_max = x_range
    if x_min >= x_max:
        raise ValueError("x_range minimum must be less than maximum")
    if num_points < 2:
        raise ValueError("num_points must be at least 2")
    return (x_min, x_max)


async def _evaluate_expression_points(
    x_values: Any, expression: str, ctx: SkipValidation[Context | None], num_points: int
) -> list[float]:
    """Evaluate expression for each x value with progress reporting."""
    y_values = []
    var_pattern = re.compile(r"\bx\b")
    for i, x in enumerate(x_values):
        if ctx and i % max(1, num_points // 10) == 0:
            await ctx.report_progress(i, num_points, f"Evaluating points: {i}/{num_points}")

        expr_with_value = var_pattern.sub(f"({x})", expression)
        try:
            y = await evaluate_with_timeout(expr_with_value)
            y_values.append(y)
        except ValueError:
            y_values.append(float("nan"))

    return y_values


# === TOOLS: VISUALIZATION OPERATIONS ===


@visualization_mcp.tool(
    name="plot_function",
    annotations={
        "title": "Function Plotter",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@validated_tool
@requires_matplotlib
async def plot_function(
    expression: Annotated[
        str,
        Field(
            max_length=MAX_EXPRESSION_LENGTH,
            description='Mathematical expression to plot, e.g., "x**2" or "sin(x)". Must be <= MAX_EXPRESSION_LENGTH characters. Example: "x**2"',
        ),
    ],
    x_range: Annotated[
        tuple[float, float], Field(description="X-axis range as (min, max), e.g., (-5.0, 5.0)")
    ],
    num_points: Annotated[
        int,
        Field(
            ge=2,
            le=MAX_ARRAY_SIZE,
            description="Number of sample points to plot along x_range, e.g., 100",
        ),
    ] = 100,
    ctx: SkipValidation[Context | None] = None,
) -> Image | VisualizationError:
    """Generate mathematical function plots (requires matplotlib).

    Examples:
        plot_function("x**2", (-5, 5))
        plot_function("sin(x)", (-3.14, 3.14))
    """

    if ctx:
        await ctx.info(f"Plotting function: {expression} over range {x_range}")

    try:
        import numpy as np

        x_min, x_max = _validate_plot_range(x_range, num_points)
        x_values = np.linspace(x_min, x_max, num_points)

        y_values = await _evaluate_expression_points(x_values, expression, ctx, num_points)

        if ctx:
            await ctx.report_progress(num_points, num_points, "Rendering plot")

        image_bytes = visualization.create_function_plot(x_values.tolist(), y_values, expression)

        return Image(data=image_bytes, format="png")

    except ValueError as e:
        if ctx:
            await ctx.error(f"Plot function error: {e}")
        return VisualizationError(
            message=f"**Plot Error:** {str(e)}\n\nPlease check your expression and x_range values.",
            error_type="plot_error",
        )
    except Exception as e:
        if ctx:
            await ctx.error(f"Plot function unexpected error: {e}")
        return VisualizationError(
            message=f"**Unexpected Error:** {str(e)}",
            error_type="unexpected_error",
        )


@visualization_mcp.tool(
    name="plot_histogram",
    annotations={
        "title": "Statistical Histogram",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@validated_tool
@requires_matplotlib
async def plot_histogram(  # noqa: C901
    data: Annotated[
        list[float],
        Field(
            max_length=MAX_ARRAY_SIZE,
            description="List of numeric values to bin, e.g., [1.0, 2.0, 2.5, 3.0]",
        ),
    ],
    bins: Annotated[int, Field(description="Number of histogram bins, e.g., 20")] = 20,
    title: Annotated[
        str,
        Field(
            max_length=MAX_STRING_PARAM_LENGTH,
            description="Chart title string, e.g., 'Data Distribution'",
        ),
    ] = "Data Distribution",
    ctx: SkipValidation[Context | None] = None,
) -> Image | VisualizationError:
    """Create statistical histograms (requires matplotlib).

    Examples:
        plot_histogram([1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0])
        plot_histogram([10, 20, 30, 40, 50], bins=5, title="Test Scores")
    """

    if bins < 1:
        return VisualizationError(
            message="bins must be at least 1",
            error_type="validation_error",
        )

    if ctx:
        await ctx.info(f"Creating histogram with {len(data)} data points and {bins} bins")

    try:
        if not data:
            raise ValueError("Cannot create histogram with empty data")
        if len(data) == 1:
            raise ValueError("Histogram requires at least 2 data points")

        import statistics as stats

        if ctx:
            await ctx.report_progress(0, 3, "Validating inputs")
            await ctx.report_progress(1, 3, "Calculating statistics")

        mean_val = stats.mean(data)
        median_val = stats.median(data)
        std_dev = stats.stdev(data)

        if ctx:
            await ctx.report_progress(2, 3, "Rendering histogram")

        image_bytes = visualization.create_histogram_chart(
            data, bins, title, mean_val, median_val, std_dev
        )

        if ctx:
            await ctx.report_progress(3, 3, "Complete")

        return Image(data=image_bytes, format="png")

    except ValueError as e:
        if ctx:
            await ctx.error(f"Histogram error: {e}")
        return VisualizationError(
            message=f"**Histogram Error:** {str(e)}\n\nPlease check your data and parameters.",
            error_type="histogram_error",
        )
    except Exception as e:
        if ctx:
            await ctx.error(f"Histogram unexpected error: {e}")
        return VisualizationError(
            message=f"**Unexpected Error:** {str(e)}",
            error_type="unexpected_error",
        )


@visualization_mcp.tool(
    name="plot_line_chart",
    annotations={
        "title": "Line Chart",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@validated_tool
@requires_matplotlib
async def plot_line_chart(
    x_data: Annotated[
        list[float],
        Field(max_length=MAX_ARRAY_SIZE, description="X-axis data points, e.g., [1, 2, 3, 4]"),
    ],
    y_data: Annotated[
        list[float],
        Field(max_length=MAX_ARRAY_SIZE, description="Y-axis data points, e.g., [1, 4, 9, 16]"),
    ],
    title: Annotated[
        str,
        Field(
            max_length=MAX_STRING_PARAM_LENGTH, description="Chart title string, e.g., 'Squares'"
        ),
    ] = "Line Chart",
    x_label: Annotated[
        str, Field(max_length=MAX_STRING_PARAM_LENGTH, description="X-axis label, e.g., 'Time'")
    ] = "X",
    y_label: Annotated[
        str, Field(max_length=MAX_STRING_PARAM_LENGTH, description="Y-axis label, e.g., 'Distance'")
    ] = "Y",
    color: Annotated[
        str | None,
        Field(
            max_length=MAX_STRING_PARAM_LENGTH,
            description="Line color (name or hex code, e.g., 'blue', '#2E86AB')",
        ),
    ] = None,
    show_grid: Annotated[bool, Field(description="Whether to display grid lines")] = True,
    ctx: SkipValidation[Context | None] = None,
) -> Image | VisualizationError:
    """Create a line chart from data points (requires matplotlib).

    Note:
        Use for general XY data. For time-series price data with optional moving average, use plot_financial_line instead.

    Examples:
        plot_line_chart([1, 2, 3, 4], [1, 4, 9, 16], title="Squares")
        plot_line_chart([0, 1, 2], [0, 1, 4], color='red', x_label='Time', y_label='Distance')
    """

    # Matplotlib is guaranteed to be available (decorator handles ImportError)
    if ctx:
        await ctx.info(f"Creating line chart with {len(x_data)} data points")

    try:
        image_bytes = visualization.create_line_chart(
            x_data=x_data,
            y_data=y_data,
            title=title,
            x_label=x_label,
            y_label=y_label,
            color=color,
            show_grid=show_grid,
        )

        return Image(data=image_bytes, format="png")

    except ValueError as e:
        return VisualizationError(
            message=f"**Line Chart Error:** {str(e)}\n\nPlease check that x_data and y_data have the same length.",
            error_type="line_chart_error",
        )
    except Exception as e:
        return VisualizationError(
            message=f"**Unexpected Error:** {str(e)}",
            error_type="unexpected_error",
        )


@visualization_mcp.tool(
    name="plot_scatter",
    annotations={
        "title": "Scatter Plot",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@validated_tool
@requires_matplotlib
async def plot_scatter(
    x_data: Annotated[
        list[float],
        Field(max_length=MAX_ARRAY_SIZE, description="X-axis data points, e.g., [1, 2, 3, 4]"),
    ],
    y_data: Annotated[
        list[float],
        Field(max_length=MAX_ARRAY_SIZE, description="Y-axis data points, e.g., [1, 4, 9, 16]"),
    ],
    title: Annotated[
        str,
        Field(
            max_length=MAX_STRING_PARAM_LENGTH,
            description="Chart title string, e.g., 'Correlation Study'",
        ),
    ] = "Scatter Plot",
    x_label: Annotated[
        str,
        Field(max_length=MAX_STRING_PARAM_LENGTH, description="X-axis label, e.g., 'Variable X'"),
    ] = "X",
    y_label: Annotated[
        str,
        Field(max_length=MAX_STRING_PARAM_LENGTH, description="Y-axis label, e.g., 'Variable Y'"),
    ] = "Y",
    color: Annotated[
        str | None,
        Field(
            max_length=MAX_STRING_PARAM_LENGTH,
            description="Point color (name or hex code, e.g., 'blue', '#2E86AB')",
        ),
    ] = None,
    point_size: Annotated[int, Field(description="Scatter point size in points^2, e.g., 50")] = 50,
    ctx: SkipValidation[Context | None] = None,
) -> Image | VisualizationError:
    """Create a scatter plot from data points (requires matplotlib).

    Examples:
        plot_scatter([1, 2, 3, 4], [1, 4, 9, 16], title="Correlation Study")
        plot_scatter([1, 2, 3], [2, 4, 5], color='purple', point_size=100)
    """

    # Matplotlib is guaranteed to be available (decorator handles ImportError)
    if ctx:
        await ctx.info(f"Creating scatter plot with {len(x_data)} data points")

    try:
        image_bytes = visualization.create_scatter_plot(
            x_data=x_data,
            y_data=y_data,
            title=title,
            x_label=x_label,
            y_label=y_label,
            color=color,
            point_size=point_size,
        )

        return Image(data=image_bytes, format="png")

    except ValueError as e:
        return VisualizationError(
            message=f"**Scatter Plot Error:** {str(e)}\n\nPlease check that x_data and y_data have the same length.",
            error_type="scatter_chart_error",
        )
    except Exception as e:
        return VisualizationError(
            message=f"**Unexpected Error:** {str(e)}",
            error_type="unexpected_error",
        )


@visualization_mcp.tool(
    name="plot_box_plot",
    annotations={
        "title": "Box Plot",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@validated_tool
@requires_matplotlib
async def plot_box_plot(
    data_groups: Annotated[
        list[list[float]],
        Field(
            max_length=MAX_GROUPS_COUNT,
            description="List of data groups to compare, e.g., [[1, 2, 3], [4, 5, 6]]",
        ),
    ],
    group_labels: Annotated[
        list[str] | None,
        Field(
            max_length=MAX_GROUPS_COUNT,
            description="Labels for each group, e.g., ['Group A', 'Group B']",
        ),
    ] = None,
    title: Annotated[
        str,
        Field(
            max_length=MAX_STRING_PARAM_LENGTH,
            description="Chart title string, e.g., 'Distribution Comparison'",
        ),
    ] = "Box Plot",
    y_label: Annotated[
        str, Field(max_length=MAX_STRING_PARAM_LENGTH, description="Y-axis label, e.g., 'Values'")
    ] = "Values",
    color: Annotated[
        str | None,
        Field(
            max_length=MAX_STRING_PARAM_LENGTH,
            description="Box color (name or hex code, e.g., 'blue', '#2E86AB')",
        ),
    ] = None,
    ctx: SkipValidation[Context | None] = None,
) -> Image | VisualizationError:
    """Create a box plot for comparing distributions (requires matplotlib).

    Examples:
        plot_box_plot([[1, 2, 3, 4, 5], [2, 4, 6, 8, 10]], group_labels=["A", "B"])
        plot_box_plot([[10, 20, 30], [15, 25, 35], [5, 15, 25]], title="Comparison")
    """

    # Validate nested array group sizes
    if err := validate_nested_array_groups(data_groups):
        return err

    # Matplotlib is guaranteed to be available (decorator handles ImportError)
    if ctx:
        await ctx.info(f"Creating box plot with {len(data_groups)} groups")

    try:
        image_bytes = visualization.create_box_plot(
            data_groups=data_groups,
            group_labels=group_labels,
            title=title,
            y_label=y_label,
            color=color,
        )

        return Image(data=image_bytes, format="png")

    except ValueError as e:
        return VisualizationError(
            message=f"**Box Plot Error:** {str(e)}\n\nPlease check your data groups and labels.",
            error_type="box_plot_error",
        )
    except Exception as e:
        return VisualizationError(
            message=f"**Unexpected Error:** {str(e)}",
            error_type="unexpected_error",
        )


@visualization_mcp.tool(
    name="plot_financial_line",
    annotations={
        "title": "Financial Line Chart",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@validated_tool
@requires_matplotlib
async def plot_financial_line(
    days: Annotated[
        int, Field(ge=2, le=MAX_DAYS_FINANCIAL, description="Number of days to generate, e.g., 30")
    ] = 30,
    trend: Annotated[
        str,
        Field(description="Market trend direction", examples=["bullish", "bearish", "volatile"]),
    ] = "bullish",
    start_price: Annotated[float, Field(description="Starting price value, e.g., 100.0")] = 100.0,
    color: Annotated[
        str | None,
        Field(
            max_length=MAX_STRING_PARAM_LENGTH,
            description="Line color (name or hex code, e.g., 'blue', '#2E86AB')",
        ),
    ] = None,
    ctx: SkipValidation[Context | None] = None,
) -> Image | VisualizationError:
    """Generate and plot synthetic financial price data (requires matplotlib).

    Creates realistic price movement patterns for educational purposes.
    Does not use real market data.

    Note:
        Use for time-series price data with optional moving average overlay. For general XY data, use plot_line_chart instead.

    Examples:
        plot_financial_line(days=60, trend='bullish')
        plot_financial_line(days=90, trend='volatile', start_price=150.0, color='orange')
    """
    # Validate trend against whitelist
    if trend not in ALLOWED_TRENDS:
        return VisualizationError(
            message=f"Invalid trend: {trend}. Allowed: {', '.join(sorted(ALLOWED_TRENDS))}",
            error_type="validation_error",
        )

    # Matplotlib is guaranteed to be available (decorator handles ImportError)
    if ctx:
        await ctx.info(f"Generating synthetic {trend} price data for {days} days")

    try:
        # Stage 0: Start
        if ctx:
            await ctx.report_progress(0, 3, "Validating parameters")

        # Stage 1: Validate and generate data
        if ctx:
            await ctx.report_progress(1, 3, "Generating synthetic data")

        # Generate synthetic data
        dates, prices = visualization.generate_synthetic_price_data(
            days=days,
            trend=trend,  # type: ignore
            start_price=start_price,
        )

        # Stage 2: Create financial chart
        if ctx:
            await ctx.report_progress(2, 3, "Creating financial chart")

        # Create financial chart
        image_bytes = visualization.create_financial_line_chart(
            dates=dates,
            prices=prices,
            title=f"Synthetic {trend.capitalize()} Price Movement ({days} days)",
            y_label="Price ($)",
            color=color,
        )

        # Stage 3: Complete
        if ctx:
            await ctx.report_progress(3, 3, "Complete")

        return Image(data=image_bytes, format="png")

    except ValueError as e:
        return VisualizationError(
            message=f"**Financial Chart Error:** {str(e)}\n\nPlease check your parameters (days >= 2, valid trend, positive start_price).",
            error_type="financial_chart_error",
        )
    except Exception as e:
        return VisualizationError(
            message=f"**Unexpected Error:** {str(e)}",
            error_type="unexpected_error",
        )

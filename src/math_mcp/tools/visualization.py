"""Visualization MCP tools for mathematical plotting and charting.

Extracted from server.py as part of the monolith decomposition (#140c).
Each tool generates base64-encoded PNG images using matplotlib.
"""

import re
from functools import wraps
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from math_mcp import visualization
from math_mcp.eval import _classify_expression_difficulty, evaluate_with_timeout
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


# --- Helpers ---


def make_annotations(difficulty: str, topic: str, **extra: Any) -> dict[str, Any]:
    """Build an annotation dict with required keys and optional extras (#144).

    Every tool response carries educational metadata. This helper enforces
    the two required keys (difficulty, topic) and merges any tool-specific
    extras, reducing inline dict construction across all visualization tools.
    """
    return {"difficulty": difficulty, "topic": topic, **extra}


def requires_matplotlib(func: Any) -> Any:
    """Decorator ensuring matplotlib is available before running visualization tools.

    Calls visualization._setup_matplotlib() to check availability.
    Returns a standardized error response if matplotlib is not installed,
    eliminating duplicated import/error-handling code across 6 tools.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            visualization._setup_matplotlib()
        except ImportError:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "**Matplotlib not available**\n\n"
                            "Install with: `pip install math-mcp-learning-server[plotting]`\n\n"
                            "Or for development: `uv sync --extra plotting`"
                        ),
                        "annotations": make_annotations(
                            "intermediate",
                            "visualization",
                            error="missing_dependency",
                            install_command="pip install math-mcp-learning-server[plotting]",
                        ),
                    }
                ]
            }
        return await func(*args, **kwargs)

    return wrapper


def validate_nested_array_groups(groups: list[list[float]]) -> list[list[float]]:
    """Validate nested array group sizes."""
    for i, group in enumerate(groups):
        if len(group) > MAX_GROUP_SIZE:
            raise ValueError(
                f"Group {i} exceeds maximum size of {MAX_GROUP_SIZE} elements. "
                f"Current size: {len(group)}"
            )
    return groups


# === TOOLS: VISUALIZATION OPERATIONS ===


@visualization_mcp.tool(
    annotations={
        "title": "Function Plotter",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
@requires_matplotlib
async def plot_function(
    expression: Annotated[str, Field(max_length=MAX_EXPRESSION_LENGTH)],
    x_range: tuple[float, float],
    num_points: Annotated[int, Field(ge=2, le=MAX_ARRAY_SIZE)] = 100,
    ctx: Context | None = None,
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

        # Generate x values and evaluate expression
        import numpy as np

        x_values = np.linspace(x_min, x_max, num_points)

        # Evaluate expression for each x value
        y_values = []
        var_pattern = re.compile(r"\bx\b")
        for i, x in enumerate(x_values):
            # Report progress at ~10% intervals
            if ctx and i % max(1, num_points // 10) == 0:
                await ctx.report_progress(i, num_points, f"Evaluating points: {i}/{num_points}")

            # Replace x in expression with actual value using word boundaries
            # to avoid corrupting function names like exp, max, hex
            expr_with_value = var_pattern.sub(f"({x})", expression)
            try:
                y = await evaluate_with_timeout(expr_with_value)
                y_values.append(y)
            except ValueError:
                # Handle domain errors (like sqrt of negative) or timeout
                y_values.append(float("nan"))

        # Report final progress
        if ctx:
            await ctx.report_progress(num_points, num_points, "Rendering plot")

        # Delegate rendering to visualization helper
        image_base64 = visualization.create_function_plot(
            x_values.tolist(), y_values, expression
        ).decode("utf-8")

        # Classify difficulty
        difficulty = _classify_expression_difficulty(expression)

        return {
            "content": [
                {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": "image/png",
                    "annotations": make_annotations(
                        difficulty,
                        "visualization",
                        expression=expression,
                        x_range=f"[{x_min}, {x_max}]",
                        num_points=num_points,
                        educational_note="Function plotting visualizes mathematical relationships",
                    ),
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Plot Error:** {str(e)}\n\nPlease check your expression and x_range values.",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="plot_error",
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="unexpected_error",
                    ),
                }
            ]
        }


@visualization_mcp.tool(
    annotations={
        "title": "Statistical Histogram",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
@requires_matplotlib
async def create_histogram(
    data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    bins: int = 20,
    title: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Data Distribution",
    ctx: Context | None = None,
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
        create_histogram([1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0])
        create_histogram([10, 20, 30, 40, 50], bins=5, title="Test Scores")
    """

    if bins < 1:
        raise ValueError("bins must be at least 1")

    # Matplotlib is guaranteed to be available (decorator handles ImportError)
    if ctx:
        await ctx.info(f"Creating histogram with {len(data)} data points and {bins} bins")

    try:
        # Validate inputs
        if not data:
            raise ValueError("Cannot create histogram with empty data")
        if len(data) == 1:
            raise ValueError("Histogram requires at least 2 data points")

        # Report initial progress
        if ctx:
            await ctx.report_progress(0, 3, "Validating inputs")

        # Stage 1: Calculate statistics
        if ctx:
            await ctx.report_progress(1, 3, "Calculating statistics")

        import statistics as stats

        mean_val = stats.mean(data)
        median_val = stats.median(data)
        std_dev = stats.stdev(data) if len(data) > 1 else 0

        # Stage 2: Render visualization
        if ctx:
            await ctx.report_progress(2, 3, "Rendering histogram")

        image_base64 = visualization.create_histogram_chart(
            data, bins, title, mean_val, median_val, std_dev
        ).decode("utf-8")

        # Stage 3: Complete
        if ctx:
            await ctx.report_progress(3, 3, "Complete")

        return {
            "content": [
                {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": "image/png",
                    "annotations": make_annotations(
                        "intermediate",
                        "statistics",
                        data_points=len(data),
                        bins=bins,
                        mean=round(mean_val, 4),
                        median=round(median_val, 4),
                        std_dev=round(std_dev, 4),
                        educational_note="Histograms show the distribution and frequency of data values",
                    ),
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Histogram Error:** {str(e)}\n\nPlease check your data and parameters.",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="histogram_error",
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="unexpected_error",
                    ),
                }
            ]
        }


@visualization_mcp.tool(
    annotations={"title": "Line Chart", "readOnlyHint": False, "openWorldHint": False}
)
@validated_tool
@requires_matplotlib
async def plot_line_chart(
    x_data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    y_data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    title: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Line Chart",
    x_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "X",
    y_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Y",
    color: Annotated[str | None, Field(max_length=MAX_STRING_PARAM_LENGTH)] = None,
    show_grid: bool = True,
    ctx: Context | None = None,
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

    # Matplotlib is guaranteed to be available (decorator handles ImportError)
    if ctx:
        await ctx.info(f"Creating line chart with {len(x_data)} data points")

    try:
        # Stage 0: Start
        if ctx:
            await ctx.report_progress(0, 2, "Validating data")

        # Stage 1: Validate data
        if ctx:
            await ctx.report_progress(1, 2, "Creating chart")

        # Stage 2: Render and complete
        if ctx:
            await ctx.report_progress(2, 2, "Complete")

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
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        chart_type="line",
                        data_points=len(x_data),
                        educational_note="Line charts show trends and changes over continuous data",
                    ),
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Line Chart Error:** {str(e)}\n\nPlease check that x_data and y_data have the same length.",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="line_chart_error",
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="unexpected_error",
                    ),
                }
            ]
        }


@visualization_mcp.tool(
    annotations={
        "title": "Scatter Plot",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
@requires_matplotlib
async def plot_scatter_chart(
    x_data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    y_data: Annotated[list[float], Field(max_length=MAX_ARRAY_SIZE)],
    title: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Scatter Plot",
    x_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "X",
    y_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Y",
    color: Annotated[str | None, Field(max_length=MAX_STRING_PARAM_LENGTH)] = None,
    point_size: int = 50,
    ctx: Context | None = None,
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

    # Matplotlib is guaranteed to be available (decorator handles ImportError)
    if ctx:
        await ctx.info(f"Creating scatter plot with {len(x_data)} data points")

    try:
        # Stage 0: Start
        if ctx:
            await ctx.report_progress(0, 2, "Validating data")

        # Stage 1: Validate data
        if ctx:
            await ctx.report_progress(1, 2, "Creating chart")

        # Stage 2: Render and complete
        if ctx:
            await ctx.report_progress(2, 2, "Complete")

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
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        chart_type="scatter",
                        data_points=len(x_data),
                        educational_note="Scatter plots reveal correlations and patterns in paired data",
                    ),
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Scatter Plot Error:** {str(e)}\n\nPlease check that x_data and y_data have the same length.",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="scatter_plot_error",
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="unexpected_error",
                    ),
                }
            ]
        }


@visualization_mcp.tool(
    annotations={"title": "Box Plot", "readOnlyHint": False, "openWorldHint": False}
)
@validated_tool
@requires_matplotlib
async def plot_box_plot(
    data_groups: Annotated[list[list[float]], Field(max_length=MAX_GROUPS_COUNT)],
    group_labels: Annotated[list[str] | None, Field(max_length=MAX_GROUPS_COUNT)] = None,
    title: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Box Plot",
    y_label: Annotated[str, Field(max_length=MAX_STRING_PARAM_LENGTH)] = "Values",
    color: Annotated[str | None, Field(max_length=MAX_STRING_PARAM_LENGTH)] = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a box plot for comparing distributions (requires matplotlib).

    Args:
        data_groups: List of data groups to compare
        group_labels: Optional labels for each group
        title: Chart title
        y_label: Y-axis label
        color: Box color (name or hex code, e.g., 'blue', '#2E86AB')
        ctx: FastMCP context for logging

    Returns:
        Dict with base64-encoded PNG image or error message

    Examples:
        plot_box_plot([[1, 2, 3, 4, 5], [2, 4, 6, 8, 10]], group_labels=["A", "B"])
        plot_box_plot([[10, 20, 30], [15, 25, 35], [5, 15, 25]], title="Comparison")
    """

    # Validate nested array group sizes
    validate_nested_array_groups(data_groups)

    # Matplotlib is guaranteed to be available (decorator handles ImportError)
    if ctx:
        await ctx.info(f"Creating box plot with {len(data_groups)} groups")

    try:
        # Stage 0: Start
        if ctx:
            await ctx.report_progress(0, 2, "Validating data")

        # Stage 1: Validate data
        if ctx:
            await ctx.report_progress(1, 2, "Creating chart")

        # Stage 2: Render and complete
        if ctx:
            await ctx.report_progress(2, 2, "Complete")

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
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        chart_type="box_plot",
                        groups=len(data_groups),
                        educational_note="Box plots display distribution quartiles, median, and outliers for comparison",
                    ),
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Box Plot Error:** {str(e)}\n\nPlease check your data groups and labels.",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="box_plot_error",
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": make_annotations(
                        "intermediate",
                        "visualization",
                        error="unexpected_error",
                    ),
                }
            ]
        }


@visualization_mcp.tool(
    annotations={
        "title": "Financial Line Chart",
        "readOnlyHint": False,
        "openWorldHint": False,
    }
)
@validated_tool
@requires_matplotlib
async def plot_financial_line(
    days: Annotated[int, Field(ge=2, le=MAX_DAYS_FINANCIAL)] = 30,
    trend: str = "bullish",
    start_price: float = 100.0,
    color: Annotated[str | None, Field(max_length=MAX_STRING_PARAM_LENGTH)] = None,
    ctx: Context | None = None,
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

        # Validate trend parameter
        if trend not in ["bullish", "bearish", "volatile"]:
            raise ValueError("trend must be 'bullish', 'bearish', or 'volatile'")

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
        image_base64 = visualization.create_financial_line_chart(
            dates=dates,
            prices=prices,
            title=f"Synthetic {trend.capitalize()} Price Movement ({days} days)",
            y_label="Price ($)",
            color=color,
        ).decode("utf-8")

        # Stage 3: Complete
        if ctx:
            await ctx.report_progress(3, 3, "Complete")

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
                    "annotations": make_annotations(
                        "advanced",
                        "financial_analysis",
                        chart_type="financial_line",
                        days=days,
                        trend=trend,
                        start_price=round(start_price, 2),
                        end_price=round(prices[-1], 2),
                        price_change_percent=round(price_change, 2),
                        volatility=round(volatility, 2),
                        educational_note="Synthetic data generated for educational purposes only - not real market data",
                    ),
                }
            ]
        }

    except ValueError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Financial Chart Error:** {str(e)}\n\nPlease check your parameters (days >= 2, valid trend, positive start_price).",
                    "annotations": make_annotations(
                        "advanced",
                        "financial_analysis",
                        error="financial_chart_error",
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**Unexpected Error:** {str(e)}",
                    "annotations": make_annotations(
                        "advanced",
                        "financial_analysis",
                        error="unexpected_error",
                    ),
                }
            ]
        }

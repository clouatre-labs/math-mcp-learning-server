#!/usr/bin/env python3
"""
Visualization module for Math MCP Server.
Handles chart generation with matplotlib, including synthetic data generation for educational purposes.
"""

import base64
import random
from datetime import datetime, timedelta
from io import BytesIO
from typing import Literal

# === INTERNAL HELPERS ===


def _setup_matplotlib():
    """Lazy import and configure matplotlib with non-interactive backend.

    Returns:
        Tuple of (matplotlib, pyplot, numpy) modules or raises ImportError
    """
    try:
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np

        return matplotlib, plt, np
    except ImportError as e:
        raise ImportError(
            "Matplotlib not available. "
            "Install with: pip install math-mcp-learning-server[plotting] "
            "or: uv sync --extra plotting"
        ) from e


def _encode_figure_to_base64(fig) -> str:
    """Encode matplotlib figure to base64 PNG string.

    Args:
        fig: Matplotlib figure object

    Returns:
        Base64-encoded PNG image string
    """
    _, plt, _ = _setup_matplotlib()
    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def _validate_color_scheme(color: str | None) -> str:
    """Validate and return a color hex code.

    Args:
        color: Color name or hex code, or None for default

    Returns:
        Valid hex color code
    """
    default_colors = {
        "blue": "#2E86AB",
        "red": "#C73E1D",
        "green": "#06A77D",
        "purple": "#A23B72",
        "orange": "#F18F01",
        "teal": "#4A90A4",
        "pink": "#D81159",
    }

    if color is None:
        return "#2E86AB"

    # Check if it's a named color
    if color.lower() in default_colors:
        return default_colors[color.lower()]

    # Check if it's already a hex code
    if color.startswith("#") and len(color) == 7:
        return color

    # Default fallback
    return "#2E86AB"


# === CHART GENERATORS ===


def create_line_chart(
    x_data: list[float],
    y_data: list[float],
    title: str = "Line Chart",
    x_label: str = "X",
    y_label: str = "Y",
    color: str | None = None,
    show_grid: bool = True,
) -> bytes:
    """Create a line chart from data points.

    Args:
        x_data: X-axis data points
        y_data: Y-axis data points
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Line color (name or hex code)
        show_grid: Whether to show grid lines

    Returns:
        Base64-encoded PNG image bytes

    Raises:
        ValueError: If x_data and y_data have different lengths
    """
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have the same length")

    if len(x_data) < 2:
        raise ValueError("Need at least 2 data points for a line chart")

    _, plt, _ = _setup_matplotlib()
    color_hex = _validate_color_scheme(color)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_data, y_data, linewidth=2, color=color_hex, marker="o", markersize=6)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")

    if show_grid:
        ax.grid(True, alpha=0.3)

    return _encode_figure_to_base64(fig).encode("utf-8")


def create_scatter_plot(
    x_data: list[float],
    y_data: list[float],
    title: str = "Scatter Plot",
    x_label: str = "X",
    y_label: str = "Y",
    color: str | None = None,
    point_size: int = 50,
) -> bytes:
    """Create a scatter plot from data points.

    Args:
        x_data: X-axis data points
        y_data: Y-axis data points
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Point color (name or hex code)
        point_size: Size of scatter points

    Returns:
        Base64-encoded PNG image bytes

    Raises:
        ValueError: If x_data and y_data have different lengths
    """
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have the same length")

    if len(x_data) < 1:
        raise ValueError("Need at least 1 data point for a scatter plot")

    _, plt, _ = _setup_matplotlib()
    color_hex = _validate_color_scheme(color)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x_data, y_data, s=point_size, color=color_hex, alpha=0.6, edgecolors="black")
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)

    return _encode_figure_to_base64(fig).encode("utf-8")


def create_box_plot(
    data_groups: list[list[float]],
    group_labels: list[str] | None = None,
    title: str = "Box Plot",
    y_label: str = "Values",
    color: str | None = None,
) -> bytes:
    """Create a box plot for comparing distributions.

    Args:
        data_groups: List of data groups to compare
        group_labels: Labels for each group (optional)
        title: Chart title
        y_label: Y-axis label
        color: Box plot color (name or hex code)

    Returns:
        Base64-encoded PNG image bytes

    Raises:
        ValueError: If data_groups is empty or contains empty lists
    """
    if not data_groups:
        raise ValueError("data_groups cannot be empty")

    if any(len(group) == 0 for group in data_groups):
        raise ValueError("All data groups must contain at least one value")

    _, plt, _ = _setup_matplotlib()
    color_hex = _validate_color_scheme(color)

    fig, ax = plt.subplots(figsize=(10, 6))

    box_parts = ax.boxplot(
        data_groups,
        tick_labels=group_labels or [f"Group {i + 1}" for i in range(len(data_groups))],
        patch_artist=True,
        notch=True,
        showmeans=True,
    )

    # Color the boxes
    for patch in box_parts["boxes"]:
        patch.set_facecolor(color_hex)
        patch.set_alpha(0.6)

    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    return _encode_figure_to_base64(fig).encode("utf-8")


# === SYNTHETIC DATA GENERATORS ===


def generate_synthetic_price_data(
    days: int = 30,
    trend: Literal["bullish", "bearish", "volatile"] = "bullish",
    start_price: float = 100.0,
) -> tuple[list[str], list[float]]:
    """Generate realistic synthetic price data for educational purposes.

    Creates price data with configurable trends and volatility patterns.
    Useful for demonstrating financial visualizations without real market data.

    Args:
        days: Number of days to generate
        trend: Market trend type ('bullish', 'bearish', or 'volatile')
        start_price: Starting price value

    Returns:
        Tuple of (date_labels, price_values)

    Raises:
        ValueError: If parameters are invalid
    """
    if days < 2:
        raise ValueError("Need at least 2 days for price data")

    if start_price <= 0:
        raise ValueError("start_price must be positive")

    if trend not in ["bullish", "bearish", "volatile"]:
        raise ValueError("trend must be 'bullish', 'bearish', or 'volatile'")

    # Generate date labels
    start_date = datetime.now()
    dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

    # Generate prices with trend and randomness
    prices = [start_price]

    # Trend parameters
    if trend == "bullish":
        daily_trend = 0.015  # 1.5% daily growth tendency
        volatility = 0.02  # 2% volatility
    elif trend == "bearish":
        daily_trend = -0.012  # 1.2% daily decline tendency
        volatility = 0.025  # 2.5% volatility
    else:  # volatile
        daily_trend = 0.0
        volatility = 0.04  # 4% high volatility

    # Generate subsequent prices
    for _ in range(1, days):
        # Random walk with trend
        daily_return = daily_trend + random.gauss(0, volatility)
        new_price = prices[-1] * (1 + daily_return)

        # Ensure price stays positive
        new_price = max(new_price, start_price * 0.1)
        prices.append(new_price)

    return dates, prices


def create_financial_line_chart(
    dates: list[str],
    prices: list[float],
    title: str = "Price Chart",
    y_label: str = "Price ($)",
    color: str | None = None,
) -> bytes:
    """Create a financial line chart with date labels.

    Args:
        dates: Date labels (ISO format strings)
        prices: Price values
        title: Chart title
        y_label: Y-axis label
        color: Line color (name or hex code)

    Returns:
        Base64-encoded PNG image bytes

    Raises:
        ValueError: If dates and prices have different lengths
    """
    if len(dates) != len(prices):
        raise ValueError("dates and prices must have the same length")

    if len(dates) < 2:
        raise ValueError("Need at least 2 data points")

    _, plt, np = _setup_matplotlib()
    color_hex = _validate_color_scheme(color)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Create x-axis indices for plotting
    x_indices = np.arange(len(dates))

    # Plot the line
    ax.plot(x_indices, prices, linewidth=2, color=color_hex, marker="o", markersize=4)

    # Configure x-axis with date labels
    # Show every nth label to avoid crowding
    label_frequency = max(1, len(dates) // 10)
    ax.set_xticks(x_indices[::label_frequency])
    ax.set_xticklabels(dates[::label_frequency], rotation=45, ha="right")

    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)

    # Add horizontal line at starting price for reference
    ax.axhline(
        y=prices[0], color="gray", linestyle="--", linewidth=1, alpha=0.5, label="Starting Price"
    )
    ax.legend()

    return _encode_figure_to_base64(fig).encode("utf-8")

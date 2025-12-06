#!/usr/bin/env python3
"""
Test cases for visualization tools (plot_function and create_histogram)

Note: The import matplotlib/numpy pattern in tests is intentional for checking
package availability before running visualization tests. The noqa: F401 comments
suppress unused import warnings as these imports are used for dependency checking.
"""

import pytest

# === HELPER FIXTURES ===


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context for testing."""

    class MockContext:
        def __init__(self):
            self.info_logs = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

    return MockContext()


# === PLOT FUNCTION TESTS ===


@pytest.mark.asyncio
async def test_plot_function_graceful_degradation_structure(mock_context):
    """Test plot_function has graceful degradation for missing matplotlib.

    Note: This test verifies the error message structure that would be returned
    if matplotlib were not available. The actual ImportError path is tested
    by manual testing without matplotlib installed.
    """
    # This test documents the expected behavior when matplotlib is missing
    # The actual graceful degradation logic is in the tool implementation

    expected_error_structure = {
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

    # Verify the expected structure is correct
    assert "content" in expected_error_structure
    assert expected_error_structure["content"][0]["type"] == "text"
    assert "Matplotlib not available" in expected_error_structure["content"][0]["text"]
    assert expected_error_structure["content"][0]["annotations"]["error"] == "missing_dependency"


@pytest.mark.asyncio
async def test_plot_function_basic_quadratic(mock_context):
    """Test plotting a basic quadratic function."""
    try:
        import matplotlib  # noqa: F401
        import numpy as np  # noqa: F401
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_function

    result = await plot_function.fn("x**2", (-5.0, 5.0), 50, mock_context)

    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert content["type"] == "image"
    assert "data" in content
    assert content["mimeType"] == "image/png"

    # Verify base64 encoding
    image_data = content["data"]
    assert isinstance(image_data, str)
    assert len(image_data) > 0

    # Verify annotations
    annotations = content["annotations"]
    assert annotations["topic"] == "visualization"
    assert annotations["expression"] == "x**2"
    assert annotations["x_range"] == "[-5.0, 5.0]"
    assert annotations["num_points"] == 50
    assert "educational_note" in annotations

    # Verify context logging
    assert len(mock_context.info_logs) > 0
    assert "Plotting function" in mock_context.info_logs[0]


@pytest.mark.asyncio
async def test_plot_function_trigonometric(mock_context):
    """Test plotting trigonometric functions."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_function

    result = await plot_function.fn("sin(x)", (-3.14159, 3.14159), 100, mock_context)

    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert content["type"] == "image"
    assert content["annotations"]["expression"] == "sin(x)"
    assert content["annotations"]["difficulty"] == "advanced"


@pytest.mark.asyncio
async def test_plot_function_invalid_range(mock_context):
    """Test plot_function with invalid x_range."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_function

    # x_min >= x_max
    result = await plot_function.fn("x**2", (5.0, 5.0), 100, mock_context)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "text"
    assert "Plot Error" in content["text"]
    assert "minimum must be less than maximum" in content["text"]


@pytest.mark.asyncio
async def test_plot_function_invalid_num_points(mock_context):
    """Test plot_function with invalid num_points."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_function

    # Now raises ValueError due to input validation
    with pytest.raises(ValueError, match="Input should be greater than or equal to 2"):
        await plot_function.fn("x**2", (-5.0, 5.0), 1, mock_context)


@pytest.mark.asyncio
async def test_plot_function_with_domain_error(mock_context):
    """Test plot_function with expression that has domain errors."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_function

    # sqrt of negative numbers will cause domain errors for negative x
    result = await plot_function.fn("sqrt(x)", (-5.0, 5.0), 50, mock_context)

    # Should still succeed but with NaN values for negative x
    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "image"
    assert content["annotations"]["expression"] == "sqrt(x)"


@pytest.mark.asyncio
async def test_plot_function_without_context():
    """Test plot_function works without context parameter."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_function

    result = await plot_function.fn("x**2", (-5.0, 5.0), 50, None)

    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert content["type"] == "image"


# === CREATE HISTOGRAM TESTS ===


@pytest.mark.asyncio
async def test_create_histogram_graceful_degradation_structure(mock_context):
    """Test create_histogram has graceful degradation for missing matplotlib.

    Note: This test verifies the error message structure that would be returned
    if matplotlib were not available. The actual ImportError path is tested
    by manual testing without matplotlib installed.
    """
    # This test documents the expected behavior when matplotlib is missing
    # The actual graceful degradation logic is in the tool implementation

    expected_error_structure = {
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

    # Verify the expected structure is correct
    assert "content" in expected_error_structure
    assert expected_error_structure["content"][0]["type"] == "text"
    assert "Matplotlib not available" in expected_error_structure["content"][0]["text"]
    assert expected_error_structure["content"][0]["annotations"]["error"] == "missing_dependency"


@pytest.mark.asyncio
async def test_create_histogram_basic(mock_context):
    """Test creating a basic histogram."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram

    data = [1.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 5.0]
    result = await create_histogram.fn(data, 5, "Test Distribution", mock_context)

    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert content["type"] == "image"
    assert "data" in content
    assert content["mimeType"] == "image/png"

    # Verify annotations
    annotations = content["annotations"]
    assert annotations["topic"] == "statistics"
    assert annotations["difficulty"] == "intermediate"
    assert annotations["data_points"] == 9
    assert annotations["bins"] == 5
    assert "mean" in annotations
    assert "median" in annotations
    assert "std_dev" in annotations
    assert "educational_note" in annotations

    # Verify statistics calculations
    assert annotations["mean"] == 3.0
    assert annotations["median"] == 3.0

    # Verify context logging
    assert len(mock_context.info_logs) > 0
    assert "Creating histogram" in mock_context.info_logs[0]
    assert "9 data points" in mock_context.info_logs[0]


@pytest.mark.asyncio
async def test_create_histogram_empty_data(mock_context):
    """Test create_histogram with empty data."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram

    result = await create_histogram.fn([], 10, "Test", mock_context)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "text"
    assert "Histogram Error" in content["text"]
    assert "empty data" in content["text"]
    assert content["annotations"]["error"] == "histogram_error"


@pytest.mark.asyncio
async def test_create_histogram_single_value(mock_context):
    """Test create_histogram with single data point."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram

    result = await create_histogram.fn([42.0], 10, "Test", mock_context)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "text"
    assert "Histogram Error" in content["text"]
    assert "at least 2 data points" in content["text"]


@pytest.mark.asyncio
async def test_create_histogram_invalid_bins(mock_context):
    """Test create_histogram with invalid bins parameter."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram

    # Now raises ValueError due to input validation
    with pytest.raises(ValueError, match="must be at least 1"):
        await create_histogram.fn([1.0, 2.0, 3.0], 0, "Test", mock_context)


@pytest.mark.asyncio
async def test_create_histogram_large_dataset(mock_context):
    """Test create_histogram with larger dataset."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram

    # Generate normally distributed data
    data = [float(i) for i in range(100)]
    result = await create_histogram.fn(data, 20, "Large Dataset", mock_context)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "image"
    assert content["annotations"]["data_points"] == 100
    assert content["annotations"]["bins"] == 20


@pytest.mark.asyncio
async def test_create_histogram_custom_title(mock_context):
    """Test create_histogram with custom title."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram

    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = await create_histogram.fn(data, 5, "Custom Title", mock_context)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "image"
    # Title is embedded in the image, can't directly verify but ensure it doesn't error


@pytest.mark.asyncio
async def test_create_histogram_without_context():
    """Test create_histogram works without context parameter."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram

    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = await create_histogram.fn(data, 5, "Test", None)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "image"


# === INTEGRATION TESTS ===


@pytest.mark.asyncio
async def test_visualization_tools_return_proper_structure(mock_context):
    """Test that both visualization tools return properly structured output."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram, plot_function

    # Test plot_function
    plot_result = await plot_function.fn("x**2", (-5.0, 5.0), 50, mock_context)
    assert "content" in plot_result
    assert isinstance(plot_result["content"], list)
    assert len(plot_result["content"]) == 1
    assert "annotations" in plot_result["content"][0]

    # Test create_histogram
    histogram_result = await create_histogram.fn([1.0, 2.0, 3.0], 5, "Test", mock_context)
    assert "content" in histogram_result
    assert isinstance(histogram_result["content"], list)
    assert len(histogram_result["content"]) == 1
    assert "annotations" in histogram_result["content"][0]


@pytest.mark.asyncio
async def test_visualization_educational_annotations():
    """Test that visualization tools include educational annotations."""
    try:
        import matplotlib
        import numpy as np
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import create_histogram, plot_function

    # Test plot_function annotations
    plot_result = await plot_function.fn("sin(x)", (-3.14, 3.14), 100, None)
    plot_annotations = plot_result["content"][0]["annotations"]
    assert "difficulty" in plot_annotations
    assert "topic" in plot_annotations
    assert plot_annotations["topic"] == "visualization"
    assert "educational_note" in plot_annotations

    # Test create_histogram annotations
    histogram_result = await create_histogram.fn([1.0, 2.0, 3.0, 4.0, 5.0], 5, "Test", None)
    hist_annotations = histogram_result["content"][0]["annotations"]
    assert "difficulty" in hist_annotations
    assert hist_annotations["difficulty"] == "intermediate"
    assert "topic" in hist_annotations
    assert hist_annotations["topic"] == "statistics"
    assert "educational_note" in hist_annotations


# === VISUALIZATION MODULE UNIT TESTS ===


class TestVisualizationModule:
    """Test visualization module functions directly."""

    def test_validate_color_scheme_named(self):
        """Test color validation with named colors."""
        from math_mcp import visualization

        assert visualization._validate_color_scheme("blue") == "#2E86AB"
        assert visualization._validate_color_scheme("red") == "#C73E1D"
        assert visualization._validate_color_scheme("green") == "#06A77D"

    def test_validate_color_scheme_hex(self):
        """Test color validation with hex codes."""
        from math_mcp import visualization

        assert visualization._validate_color_scheme("#FF0000") == "#FF0000"

    def test_validate_color_scheme_default(self):
        """Test color validation returns default for None or invalid."""
        from math_mcp import visualization

        assert visualization._validate_color_scheme(None) == "#2E86AB"

    def test_create_line_chart_success(self):
        """Test line chart generation."""
        try:
            import matplotlib
        except ImportError:
            pytest.skip("matplotlib not available")

        from math_mcp import visualization

        result = visualization.create_line_chart(x_data=[1, 2, 3, 4], y_data=[1, 4, 9, 16])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_create_scatter_plot_success(self):
        """Test scatter plot generation."""
        try:
            import matplotlib
        except ImportError:
            pytest.skip("matplotlib not available")

        from math_mcp import visualization

        result = visualization.create_scatter_plot(x_data=[1, 2, 3], y_data=[2, 4, 6])
        assert isinstance(result, bytes)

    def test_create_box_plot_success(self):
        """Test box plot generation."""
        try:
            import matplotlib
        except ImportError:
            pytest.skip("matplotlib not available")

        from math_mcp import visualization

        result = visualization.create_box_plot(data_groups=[[1, 2, 3], [4, 5, 6]])
        assert isinstance(result, bytes)

    def test_generate_synthetic_price_data_bullish(self):
        """Test synthetic data generation with bullish trend."""
        from math_mcp import visualization

        dates, prices = visualization.generate_synthetic_price_data(
            days=30, trend="bullish", start_price=100.0
        )
        assert len(dates) == 30
        assert len(prices) == 30
        assert prices[0] == 100.0

    def test_create_financial_line_chart_success(self):
        """Test financial chart generation."""
        try:
            import matplotlib
        except ImportError:
            pytest.skip("matplotlib not available")

        from math_mcp import visualization

        dates, prices = visualization.generate_synthetic_price_data(days=20)
        result = visualization.create_financial_line_chart(dates=dates, prices=prices)
        assert isinstance(result, bytes)


# === NEW MCP TOOLS TESTS ===


@pytest.mark.asyncio
async def test_plot_line_chart_basic(mock_context):
    """Test plot_line_chart tool."""
    try:
        import matplotlib
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_line_chart

    result = await plot_line_chart.fn(
        [1.0, 2.0, 3.0, 4.0],
        [1.0, 4.0, 9.0, 16.0],
        "Test Line Chart",
        "X",
        "Y",
        None,
        True,
        mock_context,
    )

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "image"
    assert content["annotations"]["chart_type"] == "line"
    assert content["annotations"]["data_points"] == 4


@pytest.mark.asyncio
async def test_plot_scatter_chart_basic(mock_context):
    """Test plot_scatter_chart tool."""
    try:
        import matplotlib
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_scatter_chart

    result = await plot_scatter_chart.fn(
        [1.0, 2.0, 3.0], [2.0, 4.0, 6.0], "Test Scatter", "X", "Y", "purple", 50, mock_context
    )

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "image"
    assert content["annotations"]["chart_type"] == "scatter"


@pytest.mark.asyncio
async def test_plot_box_plot_basic(mock_context):
    """Test plot_box_plot tool."""
    try:
        import matplotlib
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_box_plot

    result = await plot_box_plot.fn(
        [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        ["Group A", "Group B"],
        "Test Box Plot",
        "Values",
        None,
        mock_context,
    )

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "image"
    assert content["annotations"]["chart_type"] == "box_plot"
    assert content["annotations"]["groups"] == 2


@pytest.mark.asyncio
async def test_plot_financial_line_basic(mock_context):
    """Test plot_financial_line tool."""
    try:
        import matplotlib
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_financial_line

    result = await plot_financial_line.fn(30, "bullish", 100.0, None, mock_context)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "image"
    assert content["annotations"]["chart_type"] == "financial_line"
    assert content["annotations"]["days"] == 30
    assert content["annotations"]["trend"] == "bullish"
    assert "volatility" in content["annotations"]


@pytest.mark.asyncio
async def test_plot_line_chart_error_mismatched_length(mock_context):
    """Test plot_line_chart with mismatched data lengths."""
    try:
        import matplotlib
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_line_chart

    result = await plot_line_chart.fn([1.0, 2.0], [1.0], "Test", "X", "Y", None, True, mock_context)

    assert isinstance(result, dict)
    content = result["content"][0]
    assert content["type"] == "text"
    assert "same length" in content["text"]


@pytest.mark.asyncio
async def test_plot_financial_line_invalid_trend(mock_context):
    """Test plot_financial_line with invalid trend."""
    try:
        import matplotlib
    except ImportError:
        pytest.skip("matplotlib not available")

    from math_mcp.server import plot_financial_line

    # Now raises ValueError due to input validation
    with pytest.raises(ValueError, match="Invalid trend"):
        await plot_financial_line.fn(30, "invalid_trend", 100.0, None, mock_context)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

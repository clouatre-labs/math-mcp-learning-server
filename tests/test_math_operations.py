#!/usr/bin/env python3
"""
Test cases for the FastMCP Math Server
"""

import os
from unittest.mock import patch

import pytest

from math_mcp.server import (
    calculate,
    compound_interest,
    convert_temperature,
    convert_units,
    evaluate_with_timeout,
    get_math_constant,
    safe_eval_expression,
)
from math_mcp.server import statistics as stats_tool

# === SECURITY TESTS ===


def test_safe_eval_basic_operations():
    """Test basic arithmetic operations."""
    assert safe_eval_expression("2 + 3") == 5
    assert safe_eval_expression("10 - 4") == 6
    assert safe_eval_expression("6 * 7") == 42
    assert safe_eval_expression("15 / 3") == 5
    assert safe_eval_expression("2 ** 3") == 8


def test_safe_eval_complex_expressions():
    """Test more complex mathematical expressions."""
    assert safe_eval_expression("2 + 3 * 4") == 14  # Order of operations
    assert safe_eval_expression("(2 + 3) * 4") == 20  # Parentheses
    assert safe_eval_expression("2 ** 3") == 8  # Exponentiation


def test_safe_eval_math_functions():
    """Test mathematical functions."""
    assert abs(safe_eval_expression("sqrt(16)") - 4.0) < 1e-10
    assert abs(safe_eval_expression("abs(-5)") - 5.0) < 1e-10
    assert abs(safe_eval_expression("sin(0)") - 0.0) < 1e-10


def test_safe_eval_invalid_expressions():
    """Test that invalid expressions raise appropriate errors."""
    with pytest.raises(ValueError):
        safe_eval_expression("import os")  # Should be blocked

    with pytest.raises(ValueError):
        safe_eval_expression("__import__('os')")  # Should be blocked

    with pytest.raises(ValueError):
        safe_eval_expression("exec('print(1)')")  # Should be blocked


# === TEMPERATURE CONVERSION TESTS ===


def test_temperature_conversions():
    """Test temperature conversion functions."""
    # Celsius to Fahrenheit
    assert abs(convert_temperature(0, "c", "f") - 32.0) < 1e-10
    assert abs(convert_temperature(100, "c", "f") - 212.0) < 1e-10

    # Fahrenheit to Celsius
    assert abs(convert_temperature(32, "f", "c") - 0.0) < 1e-10
    assert abs(convert_temperature(212, "f", "c") - 100.0) < 1e-10

    # Celsius to Kelvin
    assert abs(convert_temperature(0, "c", "k") - 273.15) < 1e-10


# === FASTMCP TOOL TESTS ===


@pytest.mark.asyncio
async def test_calculate_tool():
    """Test the calculate tool returns structured output with annotations."""

    # Mock context for calculation history
    class MockLifespanContext:
        def __init__(self):
            self.calculation_history = []

    class MockRequestContext:
        def __init__(self):
            self.lifespan_context = MockLifespanContext()

    class MockContext:
        def __init__(self):
            self.request_context = MockRequestContext()
            self.info_logs = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

    ctx = MockContext()
    result = await calculate.fn("2 + 3", ctx)

    assert isinstance(result, dict)
    assert "content" in result
    assert len(result["content"]) == 1
    content = result["content"][0]
    assert content["type"] == "text"
    assert "2 + 3 = 5.0" in content["text"]
    assert "annotations" in content
    assert content["annotations"]["difficulty"] == "basic"
    assert content["annotations"]["topic"] == "arithmetic"


@pytest.mark.asyncio
async def test_statistics_tool():
    """Test the statistics tool with various operations."""

    # Mock context
    class MockContext:
        def __init__(self):
            self.info_logs = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

    ctx = MockContext()

    # Test mean
    result = await stats_tool.fn([1, 2, 3, 4, 5], "mean", ctx)
    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert "Mean" in content["text"]
    assert "3.0" in content["text"]
    assert content["annotations"]["topic"] == "statistics"
    assert content["annotations"]["operation"] == "mean"
    assert content["annotations"]["sample_size"] == 5

    # Test median
    result = await stats_tool.fn([1, 2, 3, 4, 5], "median", ctx)
    assert "Median" in result["content"][0]["text"]
    assert "3.0" in result["content"][0]["text"]

    # Test empty list
    with pytest.raises(ValueError, match="Cannot calculate statistics on empty list"):
        await stats_tool.fn([], "mean", ctx)

    # Test invalid operation
    with pytest.raises(ValueError, match="Invalid operation"):
        await stats_tool.fn([1, 2, 3], "invalid_op", ctx)


@pytest.mark.asyncio
async def test_compound_interest_tool():
    """Test compound interest calculations."""

    # Mock context
    class MockContext:
        def __init__(self):
            self.info_logs = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

    ctx = MockContext()
    result = await compound_interest.fn(1000.0, 0.05, 5.0, 12, ctx)

    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert "Compound Interest Calculation" in content["text"]
    assert "$1,000.00" in content["text"]
    assert content["annotations"]["topic"] == "finance"
    assert content["annotations"]["difficulty"] == "intermediate"
    assert content["annotations"]["time_years"] == 5.0

    # Test validation errors
    with pytest.raises(ValueError, match="Principal must be greater than 0"):
        await compound_interest.fn(0, 0.05, 5.0, 1, ctx)

    with pytest.raises(ValueError, match="Interest rate cannot be negative"):
        await compound_interest.fn(1000, -0.01, 5.0, 1, ctx)


@pytest.mark.asyncio
async def test_convert_units_tool():
    """Test unit conversion tool."""

    # Mock context
    class MockContext:
        def __init__(self):
            self.info_logs = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

    ctx = MockContext()

    # Test length conversion
    result = await convert_units.fn(100, "cm", "m", "length", ctx)

    assert isinstance(result, dict)
    assert "content" in result
    content = result["content"][0]
    assert "100 cm = 1 m" in content["text"]
    assert content["annotations"]["topic"] == "unit_conversion"
    assert content["annotations"]["conversion_type"] == "length"
    assert content["annotations"]["from_unit"] == "cm"
    assert content["annotations"]["to_unit"] == "m"

    # Test temperature conversion
    result = await convert_units.fn(0, "c", "f", "temperature", ctx)
    assert "32" in result["content"][0]["text"]

    # Test invalid unit type
    with pytest.raises(ValueError, match="Unknown unit type"):
        await convert_units.fn(100, "cm", "m", "invalid_type", ctx)


# === RESOURCE TESTS ===


def test_math_constants_resource():
    """Test math constants resource."""
    # Test known constant
    result = get_math_constant.fn("pi")
    assert "pi:" in result
    assert "3.14159" in result
    assert "Description:" in result

    # Test unknown constant
    result = get_math_constant.fn("unknown_constant")
    assert "Unknown constant" in result
    assert "Available constants:" in result


# === INTEGRATION TESTS ===


def test_calculation_with_math_functions():
    """Test calculations that use various math functions."""
    # Test trigonometric functions
    result = safe_eval_expression("sin(0)")
    assert abs(result - 0.0) < 1e-10

    result = safe_eval_expression("cos(0)")
    assert abs(result - 1.0) < 1e-10

    # Test square root
    result = safe_eval_expression("sqrt(25)")
    assert abs(result - 5.0) < 1e-10

    # Test logarithm
    result = safe_eval_expression("log(1)")
    assert abs(result - 0.0) < 1e-10


def test_complex_calculations():
    """Test complex mathematical expressions."""
    # Test compound expression
    result = safe_eval_expression("2 * (3 + 4) - sqrt(16)")
    expected = 2 * (3 + 4) - 4  # 14 - 4 = 10
    assert abs(result - expected) < 1e-10

    # Test with scientific notation
    result = safe_eval_expression("1e2 + 50")
    assert abs(result - 150.0) < 1e-10


@pytest.mark.asyncio
async def test_statistical_edge_cases():
    """Test statistical functions with edge cases."""

    # Mock context
    class MockContext:
        def __init__(self):
            self.info_logs = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

    ctx = MockContext()

    # Single value
    result = await stats_tool.fn([42.0], "mean", ctx)
    assert "42.0" in result["content"][0]["text"]

    # Standard deviation with single value
    result = await stats_tool.fn([42.0], "std_dev", ctx)
    assert "0" in result["content"][0]["text"]  # Should not raise error

    # Variance with single value
    result = await stats_tool.fn([42.0], "variance", ctx)
    assert "0" in result["content"][0]["text"]  # Should not raise error


@pytest.mark.asyncio
async def test_unit_conversion_edge_cases():
    """Test unit conversions with various edge cases."""

    # Mock context
    class MockContext:
        def __init__(self):
            self.info_logs = []

        async def info(self, message: str):
            """Mock info logging."""
            self.info_logs.append(message)

    ctx = MockContext()

    # Convert to same unit
    result = await convert_units.fn(100, "m", "m", "length", ctx)
    assert "100 m = 100 m" in result["content"][0]["text"]

    # Test case insensitivity
    result = await convert_units.fn(1, "M", "KM", "length", ctx)
    assert "0.001" in result["content"][0]["text"]


# === TIMEOUT TESTS ===


@pytest.mark.asyncio
async def test_evaluate_with_timeout_fast_expression():
    """Test that fast expressions complete successfully."""
    result = await evaluate_with_timeout("2 + 3")
    assert result == 5.0


@pytest.mark.asyncio
async def test_evaluate_with_timeout_slow_expression():
    """Test that slow expressions trigger timeout."""
    # Mock safe_eval_expression to simulate slow execution
    import time

    def slow_eval(expr):
        time.sleep(10)  # Exceeds default 5s timeout
        return 42.0

    with patch("math_mcp.server.safe_eval_expression", side_effect=slow_eval):
        with pytest.raises(ValueError, match="exceeded.*timeout"):
            await evaluate_with_timeout("slow_expression")


@pytest.mark.asyncio
async def test_evaluate_with_timeout_custom_timeout():
    """Test timeout configuration via environment variable."""
    with patch.dict(os.environ, {"MATH_TIMEOUT": "0.1"}):
        # Reload module to pick up new env var
        import importlib

        import math_mcp.server

        importlib.reload(math_mcp.server)

        def slow_eval(expr):
            import time

            time.sleep(0.5)  # Exceeds 0.1s timeout
            return 42.0

        with patch("math_mcp.server.safe_eval_expression", side_effect=slow_eval):
            with pytest.raises(ValueError, match="exceeded.*timeout"):
                await math_mcp.server.evaluate_with_timeout("slow")


# === RATE LIMITING TESTS ===


@pytest.mark.asyncio
async def test_rate_limit_env_var_configuration():
    """Test rate limit configuration via environment variable."""
    with patch.dict(os.environ, {"MCP_RATE_LIMIT_PER_MINUTE": "50"}):
        import importlib

        import math_mcp.server

        importlib.reload(math_mcp.server)
        assert math_mcp.server.RATE_LIMIT_PER_MINUTE == 50


@pytest.mark.asyncio
async def test_rate_limit_disabled_when_zero():
    """Test rate limiting can be disabled by setting to 0."""
    with patch.dict(os.environ, {"MCP_RATE_LIMIT_PER_MINUTE": "0"}):
        import importlib

        import math_mcp.server

        importlib.reload(math_mcp.server)
        assert math_mcp.server.RATE_LIMIT_PER_MINUTE == 0


@pytest.mark.asyncio
async def test_rate_limit_enforcement():
    """Test that rate limiting blocks excessive requests."""
    from fastmcp import FastMCP
    from fastmcp.client import Client
    from fastmcp.exceptions import ToolError
    from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
    from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware

    # Create test server with limit high enough for test setup + tool calls
    test_mcp = FastMCP("test-rate-limit")
    test_mcp.add_middleware(ErrorHandlingMiddleware())
    test_mcp.add_middleware(SlidingWindowRateLimitingMiddleware(max_requests=10, window_minutes=1))

    @test_mcp.tool()
    def test_tool() -> str:
        return "success"

    async with Client(transport=test_mcp) as client:
        # Make 8 successful tool calls (leaves room for 2 more requests)
        for _ in range(8):
            result = await client.call_tool("test_tool", {})
            assert result.content[0].text == "success"

        # Next request should exceed limit (10 total including setup calls)
        with pytest.raises(ToolError, match="Rate limit exceeded"):
            await client.call_tool("test_tool", {})


@pytest.mark.asyncio
async def test_rate_limit_default_value():
    """Test default rate limit is 100 requests per minute."""
    # Clear env var to test default
    with patch.dict(os.environ, {}, clear=True):
        import importlib

        import math_mcp.server

        importlib.reload(math_mcp.server)
        assert math_mcp.server.RATE_LIMIT_PER_MINUTE == 100


# === INPUT SIZE VALIDATION TESTS ===


@pytest.mark.asyncio
async def test_expression_length_validation():
    """Test expression length validation."""
    from math_mcp.server import MAX_EXPRESSION_LENGTH

    # Mock context
    class MockLifespanContext:
        def __init__(self):
            self.calculation_history = []

    class MockRequestContext:
        def __init__(self):
            self.lifespan_context = MockLifespanContext()

    class MockContext:
        def __init__(self):
            self.request_context = MockRequestContext()

        async def info(self, message: str):
            pass

    ctx = MockContext()

    # Valid: below limit (off-by-one boundary test)
    # Create expression like "1+1+1+1..." that's exactly MAX_EXPRESSION_LENGTH - 1 chars
    below_limit_expr = "+".join(["1"] * ((MAX_EXPRESSION_LENGTH) // 2))[: MAX_EXPRESSION_LENGTH - 1]
    result = await calculate.fn(below_limit_expr, ctx)
    assert "content" in result

    # Valid: at limit (use a valid expression that's exactly at the limit)
    # Create expression like "1+1+1+1..." that's exactly MAX_EXPRESSION_LENGTH chars
    valid_expr = "+".join(["1"] * ((MAX_EXPRESSION_LENGTH + 1) // 2))[:MAX_EXPRESSION_LENGTH]
    result = await calculate.fn(valid_expr, ctx)
    assert "content" in result

    # Invalid: exceeds limit
    # Create expression like "1+1+1+1..." that exceeds MAX_EXPRESSION_LENGTH
    invalid_expr = "+".join(["1"] * ((MAX_EXPRESSION_LENGTH + 2) // 2))[: MAX_EXPRESSION_LENGTH + 1]
    with pytest.raises(
        ValueError, match=f"String should have at most {MAX_EXPRESSION_LENGTH} characters"
    ):
        await calculate.fn(invalid_expr, ctx)


@pytest.mark.asyncio
async def test_array_size_validation():
    """Test array size validation."""
    from math_mcp.server import MAX_ARRAY_SIZE

    # Mock context
    class MockContext:
        async def info(self, message: str):
            pass

    ctx = MockContext()

    # Valid: at limit
    valid_array = [1.0] * MAX_ARRAY_SIZE
    result = await stats_tool.fn(valid_array, "mean", ctx)
    assert "content" in result

    # Invalid: exceeds limit
    invalid_array = [1.0] * (MAX_ARRAY_SIZE + 1)
    with pytest.raises(ValueError, match=f"List should have at most {MAX_ARRAY_SIZE} items"):
        await stats_tool.fn(invalid_array, "mean", ctx)


@pytest.mark.asyncio
async def test_operation_whitelist_validation():
    """Test operation whitelist validation."""

    # Mock context
    class MockContext:
        async def info(self, message: str):
            pass

    ctx = MockContext()

    # Valid operations
    for op in ["mean", "median", "mode", "std_dev", "variance"]:
        result = await stats_tool.fn([1.0, 2.0, 3.0], op, ctx)
        assert "content" in result

    # Invalid operation
    with pytest.raises(ValueError, match="Invalid operation"):
        await stats_tool.fn([1.0, 2.0, 3.0], "invalid_op", ctx)


@pytest.mark.asyncio
async def test_variable_name_validation():
    """Test variable name validation."""
    from math_mcp.server import MAX_VARIABLE_NAME_LENGTH, save_calculation

    # Mock context
    class MockLifespanContext:
        def __init__(self):
            self.calculation_history = []

    class MockRequestContext:
        def __init__(self):
            self.lifespan_context = MockLifespanContext()

    class MockContext:
        def __init__(self):
            self.request_context = MockRequestContext()

        async def info(self, message: str):
            pass

    ctx = MockContext()

    # Valid: alphanumeric with underscore and hyphen
    result = await save_calculation.fn("valid_name-123", "2+2", 4.0, ctx)
    assert "content" in result

    # Valid: at limit
    valid_name = "a" * MAX_VARIABLE_NAME_LENGTH
    result = await save_calculation.fn(valid_name, "2+2", 4.0, ctx)
    assert "content" in result

    # Invalid: exceeds length
    invalid_name = "a" * (MAX_VARIABLE_NAME_LENGTH + 1)
    with pytest.raises(
        ValueError, match=f"String should have at most {MAX_VARIABLE_NAME_LENGTH} characters"
    ):
        await save_calculation.fn(invalid_name, "2+2", 4.0, ctx)

    # Invalid: empty
    with pytest.raises(ValueError, match="cannot be empty"):
        await save_calculation.fn("", "2+2", 4.0, ctx)

    # Invalid: special characters
    with pytest.raises(ValueError, match="only letters, numbers, underscores, and hyphens"):
        await save_calculation.fn("invalid@name", "2+2", 4.0, ctx)


@pytest.mark.asyncio
async def test_string_param_validation():
    """Test string parameter validation."""
    from math_mcp.server import MAX_STRING_PARAM_LENGTH, create_histogram

    # Valid: at limit
    valid_title = "a" * MAX_STRING_PARAM_LENGTH
    result = await create_histogram.fn([1.0, 2.0, 3.0], 10, valid_title, None)
    # Should return matplotlib not available or success
    assert "content" in result

    # Invalid: exceeds limit
    invalid_title = "a" * (MAX_STRING_PARAM_LENGTH + 1)
    with pytest.raises(
        ValueError, match=f"String should have at most {MAX_STRING_PARAM_LENGTH} characters"
    ):
        await create_histogram.fn([1.0, 2.0, 3.0], 10, invalid_title, None)


@pytest.mark.asyncio
async def test_nested_array_validation():
    """Test nested array validation for plot_box_plot."""
    from math_mcp.server import MAX_GROUP_SIZE, MAX_GROUPS_COUNT, plot_box_plot

    # Valid: at group limit
    valid_groups = [[1.0, 2.0]] * MAX_GROUPS_COUNT
    result = await plot_box_plot.fn(valid_groups, None, "Test", "Y", None, None)
    assert "content" in result

    # Invalid: exceeds group count
    invalid_groups = [[1.0, 2.0]] * (MAX_GROUPS_COUNT + 1)
    with pytest.raises(ValueError, match=f"List should have at most {MAX_GROUPS_COUNT} items"):
        await plot_box_plot.fn(invalid_groups, None, "Test", "Y", None, None)

    # Valid: at group size limit
    valid_large_group = [[1.0] * MAX_GROUP_SIZE]
    result = await plot_box_plot.fn(valid_large_group, None, "Test", "Y", None, None)
    assert "content" in result

    # Invalid: exceeds group size
    invalid_large_group = [[1.0] * (MAX_GROUP_SIZE + 1)]
    with pytest.raises(ValueError, match=f"exceeds maximum size of {MAX_GROUP_SIZE}"):
        await plot_box_plot.fn(invalid_large_group, None, "Test", "Y", None, None)


@pytest.mark.asyncio
async def test_days_validation():
    """Test days validation for plot_financial_line."""
    from math_mcp.server import MAX_DAYS_FINANCIAL, plot_financial_line

    # Valid: at limit
    result = await plot_financial_line.fn(MAX_DAYS_FINANCIAL, "bullish", 100.0, None, None)
    assert "content" in result

    # Invalid: exceeds limit
    with pytest.raises(
        ValueError, match=f"Input should be less than or equal to {MAX_DAYS_FINANCIAL}"
    ):
        await plot_financial_line.fn(MAX_DAYS_FINANCIAL + 1, "bullish", 100.0, None, None)

    # Invalid: too small
    with pytest.raises(ValueError, match="Input should be greater than or equal to 2"):
        await plot_financial_line.fn(1, "bullish", 100.0, None, None)


@pytest.mark.asyncio
async def test_trend_whitelist_validation():
    """Test trend whitelist validation."""
    from math_mcp.server import plot_financial_line

    # Valid trends
    for trend in ["bullish", "bearish", "volatile"]:
        result = await plot_financial_line.fn(30, trend, 100.0, None, None)
        assert "content" in result

    # Invalid trend
    with pytest.raises(ValueError, match="Invalid trend"):
        await plot_financial_line.fn(30, "invalid_trend", 100.0, None, None)


@pytest.mark.asyncio
async def test_num_points_validation():
    """Test num_points validation for plot_function."""
    from math_mcp.server import MAX_ARRAY_SIZE, plot_function

    # Valid: at limit
    result = await plot_function.fn("x**2", (-5, 5), MAX_ARRAY_SIZE, None)
    assert "content" in result

    # Invalid: exceeds limit
    with pytest.raises(ValueError, match=f"Input should be less than or equal to {MAX_ARRAY_SIZE}"):
        await plot_function.fn("x**2", (-5, 5), MAX_ARRAY_SIZE + 1, None)

    # Invalid: too small
    with pytest.raises(ValueError, match="Input should be greater than or equal to 2"):
        await plot_function.fn("x**2", (-5, 5), 1, None)


@pytest.mark.asyncio
async def test_bins_validation():
    """Test bins validation for create_histogram."""
    from math_mcp.server import create_histogram

    # Valid: positive bins
    result = await create_histogram.fn([1.0, 2.0, 3.0], 10, "Test", None)
    assert "content" in result

    # Invalid: zero bins
    with pytest.raises(ValueError, match="must be at least 1"):
        await create_histogram.fn([1.0, 2.0, 3.0], 0, "Test", None)

    # Invalid: negative bins
    with pytest.raises(ValueError, match="must be at least 1"):
        await create_histogram.fn([1.0, 2.0, 3.0], -1, "Test", None)


@pytest.mark.asyncio
async def test_empty_input_validation():
    """Test validation with empty inputs."""

    # Mock context
    class MockContext:
        async def info(self, message: str):
            pass

    ctx = MockContext()

    # Empty array should fail at business logic level (not size validation)
    with pytest.raises(ValueError, match="Cannot calculate statistics on empty list"):
        await stats_tool.fn([], "mean", ctx)


@pytest.mark.asyncio
async def test_validation_error_messages():
    """Test that validation error messages are clear and include limits."""
    from math_mcp.server import MAX_EXPRESSION_LENGTH

    # Mock context
    class MockContext:
        async def info(self, message: str):
            pass

    ctx = MockContext()

    # Test error message includes max value (Pydantic format)
    invalid_expr = "1" * (MAX_EXPRESSION_LENGTH + 1)
    try:
        await calculate.fn(invalid_expr, ctx)
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        error_msg = str(e)
        # Pydantic error format: "String should have at most 500 characters"
        assert str(MAX_EXPRESSION_LENGTH) in error_msg
        assert "String should have at most" in error_msg


@pytest.mark.asyncio
async def test_env_var_configuration():
    """Test that size limits can be configured via environment variables."""
    with patch.dict(os.environ, {"MAX_EXPRESSION_LENGTH": "100"}):
        import importlib

        import math_mcp.server

        importlib.reload(math_mcp.server)
        assert math_mcp.server.MAX_EXPRESSION_LENGTH == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

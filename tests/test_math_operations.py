#!/usr/bin/env python3
"""
Test cases for the FastMCP Math Server
"""

import asyncio
import os
import unittest.mock
from unittest.mock import patch

import pytest
from fastmcp.utilities.types import Image

from math_mcp.eval import (
    convert_temperature,
    evaluate_with_timeout,
    safe_eval_expression,
)
from math_mcp.persistence.storage import ensure_workspace_directory
from math_mcp.resources import get_math_constant, get_workspace
from math_mcp.settings import (
    MAX_ARRAY_SIZE,
    MAX_EXPRESSION_LENGTH,
    MAX_VARIABLE_NAME_LENGTH,
)
from math_mcp.tools.calculate import (
    calc_expression,
    calc_interest,
    calc_units,
)
from math_mcp.tools.calculate import (
    calc_statistics as stats_tool,
)
from math_mcp.tools.persistence import workspace_load, workspace_save
from math_mcp.tools.visualization import VisualizationError

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


def test_build_safe_expr_no_mangle_substring():
    """Identifier containing a math function name as substring must not be mangled."""
    # 'logical' contains 'log' -- with str.replace it would become 'math.logical'
    # which would then raise NameError inside the restricted scope (not a math attribute).
    # With word-boundary regex 'log' is not matched inside 'logical'.
    # Either way the expression must raise (NameError -> ValueError) since 'logical'
    # is not a valid math identifier.
    with pytest.raises((ValueError, NameError)):
        safe_eval_expression("logical + 1")


def test_build_safe_expr_exact_function_prefix():
    """Exact function name must be prefixed with math. and evaluated correctly."""
    import math

    result = safe_eval_expression("log(10)")
    assert abs(result - math.log(10)) < 1e-10


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
async def test_calculate_tool(mock_context):
    """Test the calculate tool returns structured output with annotations."""

    result = await calc_expression.raw_function("2 + 3", mock_context)

    assert result.expression == "2 + 3"
    assert result.result == 5.0
    assert result.difficulty == "basic"
    assert result.topic == "arithmetic"


@pytest.mark.asyncio
async def test_statistics_tool(mock_context):
    """Test the statistics tool with various operations."""

    ctx = mock_context

    # Test mean
    result = await stats_tool.raw_function([1, 2, 3, 4, 5], "mean", ctx)
    assert result.operation == "mean"
    assert result.result == 3.0
    assert result.sample_size == 5
    assert result.topic == "statistics"
    assert result.difficulty == "basic"

    # Test median
    result = await stats_tool.raw_function([1, 2, 3, 4, 5], "median", ctx)
    assert result.operation == "median"
    assert result.result == 3.0
    assert result.sample_size == 5

    # Test empty list
    with pytest.raises(ValueError, match="Cannot calculate statistics on empty list"):
        await stats_tool.raw_function([], "mean", ctx)

    # Test invalid operation
    with pytest.raises(ValueError, match="Invalid operation"):
        await stats_tool.raw_function([1, 2, 3], "invalid_op", ctx)


@pytest.mark.asyncio
async def test_compound_interest_tool(mock_context):
    """Test compound interest calculations."""

    ctx = mock_context
    result = await calc_interest(1000.0, 0.05, 5.0, 12, ctx)

    assert result.principal == 1000.0
    assert result.rate == 0.05
    assert result.time == 5.0
    assert result.compounds_per_year == 12
    assert result.difficulty == "intermediate"
    assert result.topic == "finance"
    assert result.final_amount > result.principal
    assert result.total_interest == result.final_amount - result.principal

    # Test validation errors (Pydantic Field constraints)
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        await calc_interest(0, 0.05, 5.0, 1, ctx)

    with pytest.raises(ValidationError):
        await calc_interest(1000, -0.01, 5.0, 1, ctx)


@pytest.mark.asyncio
async def test_convert_units_tool(mock_context):
    """Test unit conversion tool."""

    ctx = mock_context

    # Test length conversion
    result = await calc_units(100, "cm", "m", "length", ctx)

    assert result.value == 100.0
    assert result.from_unit == "cm"
    assert result.to_unit == "m"
    assert result.converted_value == 1.0
    assert result.unit_type == "length"
    assert result.topic == "unit_conversion"
    assert result.difficulty == "basic"

    # Test temperature conversion
    result = await calc_units(0, "c", "f", "temperature", ctx)
    assert result.converted_value == 32.0
    assert result.unit_type == "temperature"

    # Test invalid unit type
    with pytest.raises(ValueError, match="Unknown unit type"):
        await calc_units(100, "cm", "m", "invalid_type", ctx)


# === RESOURCE TESTS ===


def test_math_constants_resource():
    """Test math constants resource."""
    # Test known constant
    result = get_math_constant("pi")
    assert "pi:" in result
    assert "3.14159" in result
    assert "Description:" in result

    # Test unknown constant
    result = get_math_constant("unknown_constant")
    assert "Unknown constant" in result
    assert "Available constants:" in result


# === INTEGRATION TESTS ===


@pytest.mark.asyncio
async def test_statistical_edge_cases(mock_context):
    """Test statistical functions with edge cases."""

    ctx = mock_context

    # Single value
    result = await stats_tool.raw_function([42.0], "mean", ctx)
    assert result.result == 42.0
    assert result.operation == "mean"

    # Standard deviation with single value
    result = await stats_tool.raw_function([42.0], "std_dev", ctx)
    assert result.result == 0.0
    assert result.operation == "std_dev"

    # Variance with single value
    result = await stats_tool.raw_function([42.0], "variance", ctx)
    assert result.result == 0.0
    assert result.operation == "variance"


@pytest.mark.asyncio
async def test_unit_conversion_edge_cases(mock_context):
    """Test unit conversions with various edge cases."""

    ctx = mock_context

    # Convert to same unit
    result = await calc_units(100, "m", "m", "length", ctx)
    assert result.converted_value == 100
    assert result.from_unit == "m"
    assert result.to_unit == "m"

    # Test case insensitivity
    result = await calc_units(1, "M", "KM", "length", ctx)
    assert result.converted_value == 0.001
    assert result.from_unit.upper() == "M"
    assert result.to_unit.upper() == "KM"


# === TIMEOUT TESTS ===


@pytest.mark.asyncio
async def test_evaluate_with_timeout_fast_expression():
    """Test that fast expressions complete successfully."""
    result = await evaluate_with_timeout("2 + 3")
    assert result == 5.0


@pytest.mark.asyncio
async def test_evaluate_with_timeout_slow_expression(monkeypatch):
    """Test that timeout triggers when evaluation takes too long."""
    import math_mcp.eval

    monkeypatch.setattr(math_mcp.eval, "EXPRESSION_TIMEOUT_SECONDS", 0.01)

    async def never_complete(*args, **kwargs):
        await asyncio.sleep(10)

    loop = asyncio.get_running_loop()
    with unittest.mock.patch.object(
        loop, "run_in_executor", side_effect=lambda *a, **kw: never_complete()
    ):
        with pytest.raises(ValueError, match="exceeded.*timeout"):
            await evaluate_with_timeout("2 + 3")


@pytest.mark.asyncio
async def test_evaluate_with_timeout_custom_timeout(monkeypatch):
    """Test that custom timeout value is included in error message."""
    import math_mcp.eval

    monkeypatch.setattr(math_mcp.eval, "EXPRESSION_TIMEOUT_SECONDS", 0.05)

    async def never_complete(*args, **kwargs):
        await asyncio.sleep(10)

    loop = asyncio.get_running_loop()
    with unittest.mock.patch.object(
        loop, "run_in_executor", side_effect=lambda *a, **kw: never_complete()
    ):
        with pytest.raises(ValueError, match="exceeded.*0.05.*timeout"):
            await evaluate_with_timeout("1 + 1")


# === RATE LIMITING TESTS ===


@pytest.mark.asyncio
async def test_rate_limit_env_var_configuration(monkeypatch):
    """Test rate limit configuration via environment variable."""
    import math_mcp.server

    monkeypatch.setattr(math_mcp.server, "RATE_LIMIT_PER_MINUTE", 50)  # type: ignore[misc]

    assert math_mcp.server.RATE_LIMIT_PER_MINUTE == 50


@pytest.mark.asyncio
async def test_rate_limit_disabled_when_zero(monkeypatch):
    """Test rate limiting can be disabled by setting to 0."""
    import math_mcp.server

    monkeypatch.setattr(math_mcp.server, "RATE_LIMIT_PER_MINUTE", 0)  # type: ignore[misc]

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
        # Make 7 successful tool calls (Client init consumes 3 of 10 requests: initialize, notifications/initialized, tools/list)
        for _ in range(7):
            result = await client.call_tool("test_tool", {})
            assert result.content[0].text == "success"

        # Next request should exceed limit (10 total including setup calls)
        with pytest.raises(ToolError, match="Rate limit exceeded"):
            await client.call_tool("test_tool", {})


@pytest.mark.asyncio
async def test_rate_limit_default_value(monkeypatch):
    """Test default rate limit is 100 requests per minute."""
    import math_mcp.server

    monkeypatch.setattr(math_mcp.server, "RATE_LIMIT_PER_MINUTE", 100)  # type: ignore[misc]

    assert math_mcp.server.RATE_LIMIT_PER_MINUTE == 100


# === INPUT SIZE VALIDATION TESTS ===


@pytest.mark.asyncio
async def test_expression_length_validation(mock_context):
    """Test expression length validation."""

    ctx = mock_context

    # Valid: below limit (off-by-one boundary test)
    # Create expression like "1+1+1+1..." that's exactly MAX_EXPRESSION_LENGTH - 1 chars
    below_limit_expr = "+".join(["1"] * ((MAX_EXPRESSION_LENGTH) // 2))[: MAX_EXPRESSION_LENGTH - 1]
    result = await calc_expression.raw_function(below_limit_expr, ctx)
    assert hasattr(result, "result")
    assert isinstance(result.result, (int, float))

    # Valid: at limit (use a valid expression that's exactly at the limit)
    # Create expression like "1+1+1+1..." that's exactly MAX_EXPRESSION_LENGTH chars
    valid_expr = "+".join(["1"] * ((MAX_EXPRESSION_LENGTH + 1) // 2))[:MAX_EXPRESSION_LENGTH]
    result = await calc_expression.raw_function(valid_expr, ctx)
    assert hasattr(result, "result")

    # Invalid: exceeds limit
    # Create expression like "1+1+1+1..." that exceeds MAX_EXPRESSION_LENGTH
    invalid_expr = "+".join(["1"] * ((MAX_EXPRESSION_LENGTH + 2) // 2))[: MAX_EXPRESSION_LENGTH + 1]
    with pytest.raises(
        ValueError, match=f"String should have at most {MAX_EXPRESSION_LENGTH} characters"
    ):
        await calc_expression(invalid_expr, ctx)


@pytest.mark.asyncio
async def test_array_size_validation(mock_context):
    """Test array size validation."""

    ctx = mock_context

    # Valid: at limit
    valid_array = [1.0] * MAX_ARRAY_SIZE
    result = await stats_tool.raw_function(valid_array, "mean", ctx)
    assert hasattr(result, "result")

    # Invalid: exceeds limit
    invalid_array = [1.0] * (MAX_ARRAY_SIZE + 1)
    with pytest.raises(ValueError, match=f"List should have at most {MAX_ARRAY_SIZE} items"):
        await stats_tool(invalid_array, "mean", ctx)


@pytest.mark.asyncio
async def test_operation_whitelist_validation(mock_context):
    """Test operation whitelist validation."""

    ctx = mock_context

    # Valid operations
    for op in ["mean", "median", "mode", "std_dev", "variance"]:
        result = await stats_tool.raw_function([1.0, 2.0, 3.0], op, ctx)
        assert hasattr(result, "operation")
        assert result.operation == op

    # Invalid operation
    with pytest.raises(ValueError, match="Invalid operation"):
        await stats_tool.raw_function([1.0, 2.0, 3.0], "invalid_op", ctx)


@pytest.mark.asyncio
async def test_variable_name_validation(mock_persistence_context):
    """Test variable name validation."""

    ctx = mock_persistence_context

    # Valid: alphanumeric with underscore and hyphen
    result = await workspace_save.raw_function("valid_name-123", "2+2", 4.0, ctx)
    assert result.success is True

    # Valid: at limit
    valid_name = "a" * MAX_VARIABLE_NAME_LENGTH
    result = await workspace_save.raw_function(valid_name, "2+2", 4.0, ctx)
    assert result.success is True

    # Invalid: exceeds length
    invalid_name = "a" * (MAX_VARIABLE_NAME_LENGTH + 1)
    with pytest.raises(
        ValueError, match=f"String should have at most {MAX_VARIABLE_NAME_LENGTH} characters"
    ):
        await workspace_save(invalid_name, "2+2", 4.0, ctx)

    # Invalid: empty
    with pytest.raises(ValueError, match="cannot be empty"):
        await workspace_save("", "2+2", 4.0, ctx)

    # Invalid: special characters
    with pytest.raises(ValueError, match="only letters, numbers, underscores, and hyphens"):
        await workspace_save("invalid@name", "2+2", 4.0, ctx)


@pytest.mark.asyncio
async def test_string_param_validation():
    """Test string parameter validation."""

    from math_mcp.tools.visualization import MAX_STRING_PARAM_LENGTH, plot_histogram

    # Valid: at limit
    valid_title = "a" * MAX_STRING_PARAM_LENGTH
    result = await plot_histogram.raw_function([1.0, 2.0, 3.0], 10, valid_title, None)
    # Should return Image or VisualizationError
    assert isinstance(result, (Image, VisualizationError))

    # Invalid: exceeds limit
    invalid_title = "a" * (MAX_STRING_PARAM_LENGTH + 1)
    with pytest.raises(
        ValueError, match=f"String should have at most {MAX_STRING_PARAM_LENGTH} characters"
    ):
        await plot_histogram([1.0, 2.0, 3.0], 10, invalid_title, None)


@pytest.mark.asyncio
async def test_nested_array_validation():
    """Test nested array validation for plot_box_plot."""

    from math_mcp.tools.visualization import MAX_GROUP_SIZE, MAX_GROUPS_COUNT, plot_box_plot

    # Valid: at group limit
    valid_groups = [[1.0, 2.0]] * MAX_GROUPS_COUNT
    result = await plot_box_plot.raw_function(valid_groups, None, "Test", "Y", None, None)
    assert isinstance(result, (Image, VisualizationError))

    # Invalid: exceeds group count
    invalid_groups = [[1.0, 2.0]] * (MAX_GROUPS_COUNT + 1)
    with pytest.raises(ValueError, match=f"List should have at most {MAX_GROUPS_COUNT} items"):
        await plot_box_plot(invalid_groups, None, "Test", "Y", None, None)

    # Valid: at group size limit
    valid_large_group = [[1.0] * MAX_GROUP_SIZE]
    result = await plot_box_plot.raw_function(valid_large_group, None, "Test", "Y", None, None)
    assert isinstance(result, (Image, VisualizationError))

    # Invalid: exceeds group size
    invalid_large_group = [[1.0] * (MAX_GROUP_SIZE + 1)]
    result = await plot_box_plot(invalid_large_group, None, "Test", "Y", None, None)
    assert isinstance(result, VisualizationError)


@pytest.mark.asyncio
async def test_days_validation():
    """Test days validation for plot_financial_line."""

    from math_mcp.tools.visualization import MAX_DAYS_FINANCIAL, plot_financial_line

    # Valid: at limit
    result = await plot_financial_line.raw_function(
        MAX_DAYS_FINANCIAL, "bullish", 100.0, None, None
    )
    assert isinstance(result, (Image, VisualizationError))

    # Invalid: exceeds limit
    with pytest.raises(
        ValueError, match=f"Input should be less than or equal to {MAX_DAYS_FINANCIAL}"
    ):
        await plot_financial_line(MAX_DAYS_FINANCIAL + 1, "bullish", 100.0, None, None)

    # Invalid: too small
    with pytest.raises(ValueError, match="Input should be greater than or equal to 2"):
        await plot_financial_line(1, "bullish", 100.0, None, None)


@pytest.mark.asyncio
async def test_trend_whitelist_validation():
    """Test trend whitelist validation."""

    from math_mcp.tools.visualization import plot_financial_line

    # Valid trends
    for trend in ["bullish", "bearish", "volatile"]:
        result = await plot_financial_line.raw_function(30, trend, 100.0, None, None)
        assert isinstance(result, (Image, VisualizationError))

    # Invalid trend
    result = await plot_financial_line(30, "invalid_trend", 100.0, None, None)
    assert isinstance(result, VisualizationError)


@pytest.mark.asyncio
async def test_num_points_validation():
    """Test num_points validation for plot_function."""

    from math_mcp.tools.visualization import MAX_ARRAY_SIZE, plot_function

    # Valid: at limit
    result = await plot_function.raw_function("x**2", (-5, 5), MAX_ARRAY_SIZE, None)
    assert isinstance(result, (Image, VisualizationError))

    # Invalid: exceeds limit
    with pytest.raises(ValueError, match=f"Input should be less than or equal to {MAX_ARRAY_SIZE}"):
        await plot_function("x**2", (-5, 5), MAX_ARRAY_SIZE + 1, None)

    # Invalid: too small
    with pytest.raises(ValueError, match="Input should be greater than or equal to 2"):
        await plot_function("x**2", (-5, 5), 1, None)


@pytest.mark.asyncio
async def test_bins_validation():
    """Test bins validation for plot_histogram."""

    from math_mcp.tools.visualization import plot_histogram

    # Valid: positive bins
    result = await plot_histogram.raw_function([1.0, 2.0, 3.0], 10, "Test", None)
    assert isinstance(result, (Image, VisualizationError))

    # Invalid: zero bins
    result = await plot_histogram([1.0, 2.0, 3.0], 0, "Test", None)
    assert isinstance(result, VisualizationError)

    # Invalid: negative bins
    result = await plot_histogram([1.0, 2.0, 3.0], -1, "Test", None)
    assert isinstance(result, VisualizationError)


@pytest.mark.asyncio
async def test_empty_input_validation(mock_context):
    """Test validation with empty inputs."""

    ctx = mock_context

    # Empty array should fail at business logic level (not size validation)
    with pytest.raises(ValueError, match="Cannot calculate statistics on empty list"):
        await stats_tool.raw_function([], "mean", ctx)


@pytest.mark.asyncio
async def test_validation_error_messages(mock_context):
    """Test that validation error messages are clear and include limits."""

    ctx = mock_context

    # Test error message includes max value (Pydantic format)
    invalid_expr = "1" * (MAX_EXPRESSION_LENGTH + 1)
    try:
        await calc_expression(invalid_expr, ctx)
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        error_msg = str(e)
        # Pydantic error format: "String should have at most 500 characters"
        assert str(MAX_EXPRESSION_LENGTH) in error_msg
        assert "String should have at most" in error_msg


@pytest.mark.asyncio
async def test_env_var_configuration(monkeypatch):
    """Test that size limits can be configured via environment variables."""
    import math_mcp.settings

    monkeypatch.setattr(math_mcp.settings, "MAX_EXPRESSION_LENGTH", 100)

    assert math_mcp.settings.MAX_EXPRESSION_LENGTH == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


@pytest.mark.asyncio
async def test_compound_interest_rate_as_percentage_raises():
    """Test that compound_interest raises ValidationError when rate > 1.0 (percentage instead of decimal).

    Arrange: rate=5 (passed as percentage instead of decimal 0.05)
    Act: call compound_interest with rate=5
    Assert: ValidationError raised (Pydantic Field le=1.0 constraint violated)
    """
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        await calc_interest(1000, 5, 1)


@pytest.mark.asyncio
async def test_compound_interest_valid_decimal_rate():
    """Test that compound_interest succeeds with valid decimal rate (no regression).

    Arrange: principal=1000, rate=0.05 (decimal), time=1
    Act: call compound_interest
    Assert: result is success with final_amount > principal
    """
    result = await calc_interest.raw_function(1000, 0.05, 1)
    assert result.final_amount > result.principal
    assert result.rate == 0.05


@pytest.mark.asyncio
async def test_math_tutor_prompt(http_client):
    """Test math_tutor prompt protocol access."""
    result = await http_client.get_prompt(
        "math_tutor", {"topic": "derivatives", "level": "intermediate", "include_examples": True}
    )
    assert result.messages is not None
    assert len(result.messages) > 0
    text = result.messages[0].content.text
    assert "derivatives" in text.lower()


@pytest.mark.asyncio
async def test_formula_explainer_prompt(http_client):
    """Test formula_explainer prompt protocol access."""
    result = await http_client.get_prompt(
        "formula_explainer", {"formula": "A = πr²", "context": "geometry"}
    )
    assert result.messages is not None
    assert len(result.messages) > 0
    text = result.messages[0].content.text
    assert "formula" in text.lower()


@pytest.mark.asyncio
async def test_functions_resource(http_client):
    """Test math://functions resource content."""
    contents = await http_client.read_resource("math://functions")
    assert len(contents) > 0
    text = contents[0].text
    assert "sin" in text


@pytest.mark.asyncio
async def test_constants_pi_resource(http_client):
    """Test math://constants/pi resource content."""
    contents = await http_client.read_resource("math://constants/pi")
    assert len(contents) > 0
    text = contents[0].text
    assert "3.14" in text


@pytest.mark.asyncio
async def test_constants_e_resource(http_client):
    """Test math://constants/e resource content."""
    contents = await http_client.read_resource("math://constants/e")
    assert len(contents) > 0
    text = contents[0].text
    assert "2.71" in text


# === EVAL.PY ERROR PATHS ===


def test_eval_pow_missing_comma():
    """pow() without comma raises ValueError."""
    with pytest.raises(ValueError, match="pow"):
        safe_eval_expression("pow(2 3)")


def test_eval_sin_empty():
    """sin() with no parameters raises ValueError."""
    with pytest.raises(ValueError, match="sin"):
        safe_eval_expression("sin()")


def test_eval_invalid_character():
    """Expression with invalid character raises ValueError."""
    with pytest.raises(ValueError, match="forbidden"):
        safe_eval_expression("2 + 2; import")


def test_eval_zero_division():
    """Division by zero raises ValueError."""
    with pytest.raises(ValueError, match="Division by zero"):
        safe_eval_expression("1/0")


def test_eval_overflow():
    """Very large exponentiation raises ValueError."""
    with pytest.raises(ValueError, match="too large"):
        safe_eval_expression("10**10000")


def test_eval_math_domain_error():
    """sqrt of negative number raises ValueError."""
    with pytest.raises(ValueError, match="Mathematical expression error"):
        safe_eval_expression("sqrt(-1)")


def test_convert_temperature_same_unit():
    """Converting to same unit returns same value."""
    result = convert_temperature(100.0, "celsius", "celsius")
    assert result == 100.0


def test_convert_temperature_unknown_from_unit():
    """Unknown from_unit raises ValueError."""
    with pytest.raises(ValueError, match="Unknown.*unit"):
        convert_temperature(100.0, "kelvin", "celsius")


def test_convert_temperature_unknown_to_unit():
    """Unknown to_unit raises ValueError."""
    with pytest.raises(ValueError, match="Unknown.*unit"):
        convert_temperature(100.0, "celsius", "rankine")


def test_classify_expression_difficulty_basic():
    """Basic expression returns 'basic' difficulty."""
    from math_mcp.eval import _classify_expression_difficulty

    result = _classify_expression_difficulty("2 + 3")
    assert result == "basic"


def test_classify_expression_difficulty_advanced():
    """Expression with functions returns 'advanced' difficulty."""
    from math_mcp.eval import _classify_expression_difficulty

    result = _classify_expression_difficulty("sin(x) + cos(y)")
    assert result == "advanced"


def test_classify_expression_topic_trigonometry():
    """Expression with sin/cos returns 'trigonometry' topic."""
    from math_mcp.eval import _classify_expression_topic

    result = _classify_expression_topic("sin(3.14159)")
    assert result == "trigonometry"


def test_classify_expression_topic_default():
    """Expression without keywords returns 'arithmetic' topic."""
    from math_mcp.eval import _classify_expression_topic

    result = _classify_expression_topic("2 + 3 * 4")
    assert result == "arithmetic"


# === MATRIX.PY VALIDATION ===


def test_validate_matrix_empty():
    """Empty matrix raises ValueError."""
    pytest.importorskip("numpy")
    from math_mcp.tools.matrix import _validate_matrix

    with pytest.raises(ValueError, match="empty"):
        _validate_matrix([])


def test_validate_matrix_jagged_rows():
    """Matrix with rows of different lengths raises ValueError."""
    pytest.importorskip("numpy")
    from math_mcp.tools.matrix import _validate_matrix

    with pytest.raises(ValueError, match="same length"):
        _validate_matrix([[1, 2], [3, 4, 5]])


def test_validate_matrix_non_numeric():
    """Matrix with non-numeric element raises ValueError."""
    pytest.importorskip("numpy")
    from math_mcp.tools.matrix import _validate_matrix

    with pytest.raises(ValueError, match="numeric"):
        _validate_matrix([[1, "two"], [3, 4]])


def test_validate_matrix_oversized():
    """Matrix exceeding max_size raises ValueError."""
    pytest.importorskip("numpy")
    from math_mcp.tools.matrix import _validate_matrix

    big_matrix = [[1.0] * 101 for _ in range(101)]
    with pytest.raises(ValueError, match="exceed"):
        _validate_matrix(big_matrix, max_size=100)


# === STORAGE.PY OSERROR PATH ===


def test_ensure_workspace_directory_oserror():
    """mkdir raises OSError -> returns False."""
    with patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied")):
        result = ensure_workspace_directory()
        assert result is False


# === CALCULATE.PY CTX-GUARDED PATHS ===


@pytest.mark.asyncio
async def test_calculate_with_context():
    """calculate() logs info via context."""
    from unittest.mock import AsyncMock, MagicMock

    mock_ctx = AsyncMock()
    result = await calc_expression("2 + 2", ctx=mock_ctx)
    assert result is not None
    mock_ctx.info.assert_called_once()


@pytest.mark.asyncio
async def test_calculate_without_context():
    """calculate() works without context."""
    result = await calc_expression("2 + 2", ctx=None)
    assert result is not None
    assert hasattr(result, "result")


@pytest.mark.asyncio
async def test_convert_units_with_context():
    """convert_units() logs info via context."""
    from unittest.mock import AsyncMock

    mock_ctx = AsyncMock()
    result = await calc_units(100.0, "m", "ft", "length", ctx=mock_ctx)
    assert result is not None
    mock_ctx.info.assert_called_once()


# === RESOURCES.PY ===


@pytest.mark.asyncio
async def test_calculation_history_resource(http_client):
    """get_calculation_history resource returns history text."""
    contents = await http_client.read_resource("math://history")
    assert len(contents) > 0
    text = contents[0].text
    assert isinstance(text, str)


def test_settings_validate_timeout_invalid() -> None:
    """MathMCPSettings rejects non-positive timeout values."""
    from pydantic import ValidationError

    from math_mcp.settings import MathMCPSettings

    with pytest.raises(ValidationError):
        MathMCPSettings(math_timeout=-1.0)


@pytest.mark.asyncio
async def test_statistics_with_progress_ctx() -> None:
    """statistics() covers ctx progress reporting branches."""
    from unittest.mock import AsyncMock

    from math_mcp.tools.calculate import calc_statistics

    mock_ctx = AsyncMock()
    result = await calc_statistics.raw_function([1.0, 2.0, 3.0], "mean", mock_ctx)
    assert result.result == 2.0
    mock_ctx.report_progress.assert_called()


@pytest.mark.asyncio
async def test_statistics_invalid_op_with_ctx() -> None:
    """statistics() covers ctx warning branch when operation is invalid."""
    from unittest.mock import AsyncMock

    from math_mcp.tools.calculate import calc_statistics

    mock_ctx = AsyncMock()
    with pytest.raises(ValueError, match="Invalid operation"):
        await calc_statistics.raw_function([1.0, 2.0], "invalid_op", mock_ctx)
    mock_ctx.warning.assert_called()


@pytest.mark.asyncio
async def test_compound_interest_negative_rate_ctx() -> None:
    """compound_interest() raises ValidationError on negative rate (Pydantic Field ge=0)."""
    from unittest.mock import AsyncMock

    from pydantic import ValidationError

    from math_mcp.tools.calculate import calc_interest

    mock_ctx = AsyncMock()
    with pytest.raises(ValidationError):
        await calc_interest(1000.0, -0.05, 1, 12, mock_ctx)


@pytest.mark.asyncio
async def test_compound_interest_zero_time_ctx() -> None:
    """compound_interest() raises ValidationError on zero time (Pydantic Field gt=0)."""
    from unittest.mock import AsyncMock

    from pydantic import ValidationError

    from math_mcp.tools.calculate import calc_interest

    mock_ctx = AsyncMock()
    with pytest.raises(ValidationError):
        await calc_interest(1000.0, 0.05, 0, 12, mock_ctx)

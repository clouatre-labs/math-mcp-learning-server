"""HTTP transport integration tests for math-mcp server.

These tests verify the server works correctly over HTTP transport,
mimicking real-world deployment scenarios like fastmcp.cloud.
Run conditionally on release tags only.
"""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError


async def test_http_ping(http_client: Client) -> None:
    """Test server responds to ping over HTTP."""
    result = await http_client.ping()
    assert result is True


async def test_http_calculate_basic(http_client: Client) -> None:
    """Test basic calculation over HTTP."""
    result = await http_client.call_tool("calculate", {"expression": "2 + 2"})
    assert len(result.content) > 0
    assert "2 + 2 = 4.0" in result.content[0].text


async def test_http_calculate_complex(http_client: Client) -> None:
    """Test complex calculation over HTTP."""
    result = await http_client.call_tool("calculate", {"expression": "sqrt(16) * 3"})
    assert len(result.content) > 0
    assert "12.0" in result.content[0].text


async def test_http_calculate_invalid_expression(http_client: Client) -> None:
    """Test error handling for invalid expression over HTTP."""
    with pytest.raises(ToolError):
        await http_client.call_tool("calculate", {"expression": "invalid syntax"})


async def test_http_statistics_mean(http_client: Client) -> None:
    """Test statistics calculation over HTTP."""
    result = await http_client.call_tool(
        "statistics", {"operation": "mean", "numbers": [1, 2, 3, 4, 5]}
    )
    assert len(result.content) > 0
    assert "3.0" in result.content[0].text


async def test_http_statistics_median(http_client: Client) -> None:
    """Test median calculation over HTTP."""
    result = await http_client.call_tool(
        "statistics", {"operation": "median", "numbers": [1, 2, 3, 4, 5]}
    )
    assert len(result.content) > 0
    assert "3.0" in result.content[0].text


async def test_http_compound_interest(http_client: Client) -> None:
    """Test compound interest calculation over HTTP."""
    result = await http_client.call_tool(
        "compound_interest",
        {"principal": 1000, "rate": 5, "time": 10, "compounds_per_year": 12},
    )
    assert len(result.content) > 0
    text = result.content[0].text
    assert "Final Amount" in text or "final" in text.lower()


async def test_http_convert_units_length(http_client: Client) -> None:
    """Test unit conversion over HTTP."""
    result = await http_client.call_tool(
        "convert_units", {"value": 1, "from_unit": "m", "to_unit": "cm", "unit_type": "length"}
    )
    assert len(result.content) > 0
    assert "100" in result.content[0].text


async def test_http_convert_units_invalid(http_client: Client) -> None:
    """Test error handling for invalid unit conversion over HTTP."""
    with pytest.raises(ToolError):
        await http_client.call_tool(
            "convert_units",
            {"value": 1, "from_unit": "invalid", "to_unit": "m", "unit_type": "length"},
        )


async def test_http_resource_math_constants(http_client: Client) -> None:
    """Test resource access over HTTP."""
    resources = await http_client.list_resources()
    resource_uris = [str(r.uri) for r in resources]
    assert "math://test" in resource_uris
    assert "math://functions" in resource_uris


async def test_http_read_resource(http_client: Client) -> None:
    """Test reading resource content over HTTP."""
    content = await http_client.read_resource("math://test")
    assert len(content) > 0
    assert hasattr(content[0], "text")
    assert "Test resource working successfully" in content[0].text


@pytest.mark.parametrize(
    "expression,expected_in_text",
    [
        ("1 + 1", "2.0"),
        ("10 - 5", "5.0"),
        ("3 * 4", "12.0"),
        ("15 / 3", "5.0"),
        ("2 ** 3", "8.0"),
    ],
)
async def test_http_calculate_parametrized(
    http_client: Client, expression: str, expected_in_text: str
) -> None:
    """Test multiple calculations with parametrization over HTTP."""
    result = await http_client.call_tool("calculate", {"expression": expression})
    assert len(result.content) > 0
    assert expected_in_text in result.content[0].text


async def test_http_list_tools(http_client: Client) -> None:
    """Test listing available tools over HTTP."""
    tools = await http_client.list_tools()
    tool_names = [t.name for t in tools]
    assert "calculate" in tool_names
    assert "statistics" in tool_names
    assert "compound_interest" in tool_names


async def test_http_response_serialization(http_client: Client) -> None:
    """Test that responses serialize correctly over HTTP."""
    result = await http_client.call_tool(
        "statistics", {"operation": "std_dev", "numbers": [1, 2, 3, 4, 5]}
    )
    assert len(result.content) > 0
    text = result.content[0].text
    assert text is not None
    assert len(text) > 0

"""HTTP transport integration tests for math-mcp server.

These tests verify the server works correctly over HTTP transport,
mimicking real-world deployment scenarios like fastmcp.cloud.
Run conditionally on release tags only.
"""

import json

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError


async def test_http_liveness(http_client: Client) -> None:
    """Test server liveness over HTTP by listing tools."""
    tools = await http_client.list_tools()
    assert len(tools) > 0


async def test_http_calculate_basic(http_client: Client) -> None:
    """Test basic calculation over HTTP."""
    result = await http_client.call_tool("calc_expression", {"expression": "2 + 2"})
    assert len(result.content) > 0
    text = result.content[0].text
    data = json.loads(text)
    assert data["expression"] == "2 + 2"
    assert data["result"] == 4.0


async def test_http_calculate_complex(http_client: Client) -> None:
    """Test complex calculation over HTTP."""
    result = await http_client.call_tool("calc_expression", {"expression": "sqrt(16) * 3"})
    assert len(result.content) > 0
    text = result.content[0].text
    data = json.loads(text)
    assert data["result"] == 12.0


async def test_http_calculate_invalid_expression(http_client: Client) -> None:
    """Test error handling for invalid expression over HTTP."""
    with pytest.raises(ToolError):
        await http_client.call_tool("calc_expression", {"expression": "invalid syntax"})


async def test_http_statistics_mean(http_client: Client) -> None:
    """Test statistics calculation over HTTP."""
    result = await http_client.call_tool(
        "calc_statistics", {"operation": "mean", "numbers": [1, 2, 3, 4, 5]}
    )
    assert len(result.content) > 0
    text = result.content[0].text
    data = json.loads(text)
    assert data["result"] == 3.0
    assert data["operation"] == "mean"


async def test_http_statistics_median(http_client: Client) -> None:
    """Test median calculation over HTTP."""
    result = await http_client.call_tool(
        "calc_statistics", {"operation": "median", "numbers": [1, 2, 3, 4, 5]}
    )
    assert len(result.content) > 0
    text = result.content[0].text
    data = json.loads(text)
    assert data["result"] == 3.0
    assert data["operation"] == "median"


async def test_http_compound_interest(http_client: Client) -> None:
    """Test compound interest calculation over HTTP."""
    result = await http_client.call_tool(
        "calc_interest",
        {"principal": 1000, "rate": 0.05, "time": 10, "compounds_per_year": 12},
    )
    assert len(result.content) > 0
    text = result.content[0].text
    data = json.loads(text)
    assert "final_amount" in data
    assert data["principal"] == 1000


async def test_http_convert_units_length(http_client: Client) -> None:
    """Test unit conversion over HTTP."""
    result = await http_client.call_tool(
        "calc_units", {"value": 1, "from_unit": "m", "to_unit": "cm", "unit_type": "length"}
    )
    assert len(result.content) > 0
    text = result.content[0].text
    data = json.loads(text)
    assert data["converted_value"] == 100.0


async def test_http_convert_units_invalid(http_client: Client) -> None:
    """Test error handling for invalid unit conversion over HTTP."""
    with pytest.raises(ToolError):
        await http_client.call_tool(
            "calc_units",
            {"value": 1, "from_unit": "invalid", "to_unit": "m", "unit_type": "length"},
        )


async def test_http_resource_math_constants(http_client: Client) -> None:
    """Test resource access over HTTP."""
    resources = await http_client.list_resources()
    resource_uris = [str(r.uri) for r in resources]
    assert "math://functions" in resource_uris


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
    result = await http_client.call_tool("calc_expression", {"expression": expression})
    assert len(result.content) > 0
    assert expected_in_text in result.content[0].text


async def test_http_list_tools(http_client: Client) -> None:
    """Test listing available tools over HTTP."""
    tools = await http_client.list_tools()
    tool_names = [t.name for t in tools]
    assert "calc_expression" in tool_names
    assert "calc_statistics" in tool_names
    assert "calc_interest" in tool_names


async def test_http_response_serialization(http_client: Client) -> None:
    """Test that responses serialize correctly over HTTP."""
    result = await http_client.call_tool(
        "calc_statistics", {"operation": "std_dev", "numbers": [1, 2, 3, 4, 5]}
    )
    assert len(result.content) > 0
    text = result.content[0].text
    assert text is not None
    assert len(text) > 0

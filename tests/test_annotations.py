"""Annotation quality regression tests.

These tests catch missing tool descriptions, missing parameter descriptions,
and missing examples on enum-like parameters at test time -- preventing
silent regressions when tools or parameters are added.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from math_mcp.server import mcp


async def _get_tools() -> list:
    async with Client(mcp) as client:
        return await client.list_tools()


@pytest.mark.asyncio
async def test_all_tools_have_descriptions() -> None:
    """Every tool must have a non-empty description string."""
    tools = await _get_tools()
    violations = [t.name for t in tools if not (t.description or "").strip()]
    assert violations == [], f"Tools missing description: {violations}"


@pytest.mark.asyncio
async def test_all_params_have_descriptions() -> None:
    """Every parameter of every tool must have a non-empty description.

    An empty description means the parameter was added without a Field(description=...)
    annotation, which degrades LLM tool-calling accuracy.
    """
    tools = await _get_tools()
    violations: list[str] = []
    for tool in tools:
        schema = tool.inputSchema or {}
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        for param_name, param_def in props.items():
            desc = param_def.get("description", "")
            if not desc or not desc.strip():
                kind = "required" if param_name in required else "optional"
                violations.append(f"{tool.name}.{param_name} ({kind})")
    assert violations == [], (
        f"Parameters missing description ({len(violations)} total):\n"
        + "\n".join(f"  - {v}" for v in sorted(violations))
    )


@pytest.mark.asyncio
async def test_no_bare_string_params_without_description() -> None:
    """String-typed parameters must always have a description.

    This is a tighter regression guard: bare `param: str` without
    Field(description=...) produces only {'type': 'string'} in the schema
    with no guidance for the LLM.
    """
    tools = await _get_tools()
    violations: list[str] = []
    for tool in tools:
        schema = tool.inputSchema or {}
        props = schema.get("properties", {})
        for param_name, param_def in props.items():
            if param_def.get("type") == "string" and not param_def.get("description", "").strip():
                violations.append(f"{tool.name}.{param_name}")
    assert violations == [], (
        f"String params without description ({len(violations)} total):\n"
        + "\n".join(f"  - {v}" for v in sorted(violations))
    )


@pytest.mark.asyncio
async def test_enum_like_params_have_examples() -> None:
    """Parameters that accept a fixed set of string values must have examples or enum.

    These are the known enum-like params. Any new param accepting a restricted set
    of values should be added to this list.
    """
    enum_like_params = {
        "calc_statistics": ["operation"],
        "calc_units": ["from_unit", "to_unit", "unit_type"],
        "plot_financial_line": ["trend"],
    }
    tools = await _get_tools()
    tool_map = {t.name: t for t in tools}
    violations: list[str] = []
    for tool_name, params in enum_like_params.items():
        tool = tool_map.get(tool_name)
        if tool is None:
            violations.append(f"{tool_name} (tool not found)")
            continue
        props = (tool.inputSchema or {}).get("properties", {})
        for param_name in params:
            param_def = props.get(param_name, {})
            has_examples = bool(param_def.get("examples"))
            has_enum = bool(param_def.get("enum"))
            if not has_examples and not has_enum:
                violations.append(f"{tool_name}.{param_name}")
    assert violations == [], (
        f"Enum-like params missing examples or enum ({len(violations)} total):\n"
        + "\n".join(f"  - {v}" for v in sorted(violations))
    )


async def _get_prompts() -> list:
    async with Client(mcp) as client:
        return await client.list_prompts()


@pytest.mark.asyncio
async def test_all_prompts_have_titles_and_descriptions() -> None:
    """Every prompt must have a non-empty title and a non-empty description string."""
    prompts = await _get_prompts()
    violations: list[str] = []
    for p in prompts:
        title = (getattr(p, "title", None) or "").strip()
        description = (p.description or "").strip()
        if not title:
            violations.append(f"{p.name}: missing title")
        if not description:
            violations.append(f"{p.name}: missing description")
    assert violations == [], f"Prompt annotation violations: {violations}"

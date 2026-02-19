#!/usr/bin/env python3
"""
Math MCP Server - FastMCP 2.0 Implementation
Educational MCP server demonstrating all three MCP pillars: Tools, Resources, and Prompts.
Uses FastMCP 2.0 patterns with structured output and multi-transport support.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
from fastmcp.server.middleware.rate_limiting import (
    RateLimitError,
    SlidingWindowRateLimitingMiddleware,
)
from starlette.responses import JSONResponse

from math_mcp.agent_card import AgentCard, AgentSkill
from math_mcp.resources import resources_mcp
from math_mcp.settings import RATE_LIMIT_PER_MINUTE
from math_mcp.tools import calculate_mcp, matrix_mcp, persistence_mcp, visualization_mcp

# === APPLICATION CONTEXT ===


@dataclass
class AppContext:
    """Application context with calculation history."""

    calculation_history: list[dict[str, Any]]


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with calculation history."""
    # Initialize calculation history
    calculation_history: list[dict[str, Any]] = []
    try:
        yield AppContext(calculation_history=calculation_history)
    finally:
        # Could save history to file here
        pass


# === FASTMCP SERVER SETUP ===

mcp = FastMCP(
    name="Math Learning Server",
    lifespan=app_lifespan,
    instructions="A comprehensive math server demonstrating MCP fundamentals with tools, resources, and prompts for educational purposes.",
)

# Mount sub-server tools using FastMCP composition pattern
mcp.mount(calculate_mcp)
mcp.mount(matrix_mcp)
mcp.mount(persistence_mcp)
mcp.mount(visualization_mcp)
mcp.mount(resources_mcp)


# === RATE LIMITING MIDDLEWARE ===


def _log_rate_limit_violation(error: Exception, context) -> None:
    """Log rate limit violations for monitoring."""
    if isinstance(error, RateLimitError):
        logging.warning(f"Rate limit exceeded: method={context.method}")


# Add middleware in correct order: StructuredLogging -> ErrorHandling -> RateLimiting
# Logging middleware placed first to capture all requests before other processing
mcp.add_middleware(StructuredLoggingMiddleware(include_payloads=True))
mcp.add_middleware(ErrorHandlingMiddleware(error_callback=_log_rate_limit_violation))
if RATE_LIMIT_PER_MINUTE > 0:
    mcp.add_middleware(
        SlidingWindowRateLimitingMiddleware(max_requests=RATE_LIMIT_PER_MINUTE, window_minutes=1)
    )
    logging.info(f"Rate limiting enabled: {RATE_LIMIT_PER_MINUTE} requests/minute")


# === AGENT CARD ENDPOINT ===


async def build_agent_card() -> AgentCard:
    """Build A2A v0.3 agent card with dynamic tool introspection.

    Introspects the MCP server's tools and builds a complete agent card
    that describes this server's capabilities, skills, and interfaces.
    This enables agent discovery and capability advertisement per A2A spec.

    Returns:
        AgentCard: Complete A2A v0.3 agent card with all required fields.
    """
    # Introspect tools from the MCP server
    tools = (await mcp.get_tools()).values()

    # Build skills from tools
    skills: list[AgentSkill] = []
    for tool in tools:
        skill = AgentSkill.model_validate(
            {
                "id": tool.name,
                "name": tool.name.replace("_", " ").title(),
                "description": tool.description or f"Tool: {tool.name}",
                "tags": ["mcp", "tool"],
                "inputModes": ["application/json"],
                "outputModes": ["application/json", "text/plain"],
            }
        )
        skills.append(skill)

    # Get dynamic version from package metadata
    try:
        version = pkg_version("math-mcp-learning-server")
    except PackageNotFoundError:
        # Fallback if package metadata is unavailable
        version = "0.10.3"

    # Build agent card with server metadata
    agent_card = AgentCard.model_validate(
        {
            "protocolVersion": "1.0",
            "name": "Math Learning Server",
            "description": "Educational MCP server demonstrating FastMCP 2.0 best practices for math operations, visualization, and persistent workspaces.",
            "version": version,
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False,
            },
            "defaultInputModes": ["application/json"],
            "defaultOutputModes": ["application/json", "text/plain", "image/png"],
            "skills": [s.model_dump(by_alias=True) for s in skills],
            "documentationUrl": "https://github.com/clouatre-labs/math-mcp-learning-server",
            "supportsExtendedAgentCard": False,
        }
    )

    return agent_card


# === A2A AGENT CARD ENDPOINT ===


@mcp.custom_route("/.well-known/agent-card.json", methods=["GET"])
async def agent_card_endpoint(request) -> JSONResponse:
    """Serve A2A v0.3 agent card for server discovery.

    This endpoint implements the A2A (Agent-to-Agent) v0.3 specification
    for agent discovery. It provides metadata about the MCP server's
    capabilities, skills, and interfaces in a standardized format.

    The response uses camelCase JSON serialization as required by the
    A2A specification, with Pydantic model_dump_json(by_alias=True).

    Args:
        request: Starlette Request object (unused but required by route handler).

    Returns:
        JSONResponse: A2A v0.3 agent card with server metadata and skills.
    """
    card = await build_agent_card()
    # Use model_dump with by_alias=True for camelCase JSON serialization
    return JSONResponse(card.model_dump(by_alias=True, mode="json"))


# === MAIN ENTRY POINT ===


def main() -> None:
    """Main entry point supporting multiple transports.

    Supports stdio and streamable-http transports. The A2A agent
    card endpoint is automatically registered via @mcp.custom_route()
    and available on all HTTP-based transports.
    """
    import sys
    from typing import Literal, cast

    # Parse command line arguments for transport type
    transport: Literal["stdio", "streamable-http"] = "stdio"  # default
    if len(sys.argv) > 1:
        if sys.argv[1] in ["stdio", "streamable-http"]:
            transport = cast(Literal["stdio", "streamable-http"], sys.argv[1])

    # Run the MCP server with the specified transport
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()

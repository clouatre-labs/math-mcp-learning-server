"""Shared test fixtures for all tests."""

import asyncio

import pytest
from fastmcp import Client, FastMCP
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
from fastmcp.utilities.tests import find_available_port

from math_mcp.resources import resources_mcp
from math_mcp.server import mcp
from math_mcp.tools import calculate_mcp, matrix_mcp, persistence_mcp, visualization_mcp


@pytest.fixture
async def http_server() -> str:
    """Start MCP server in-process with HTTP transport for testing.

    This fixture creates a real HTTP server instance, allowing tests
    to verify behavior over the actual HTTP transport layer.
    Mimics how fastmcp.cloud deploys the server.

    Yields:
        str: Server URL (e.g., "http://127.0.0.1:8000/mcp")
    """
    port = find_available_port()
    host = "127.0.0.1"
    url = f"http://{host}:{port}/mcp"

    # Start server in background task
    server_task = asyncio.create_task(
        mcp.run_http_async(host=host, port=port, show_banner=False, log_level="error")
    )

    # Give server time to start
    await asyncio.sleep(0.5)

    try:
        yield url
    finally:
        # Cleanup: cancel server task
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Reset rate limiting middleware state between tests.

    The global mcp instance has rate limiting middleware that maintains
    state across tests. This fixture resets that state to prevent test
    interference from rate limit exhaustion.
    """
    # Find and reset the rate limiting middleware
    for middleware in mcp.middleware:
        if type(middleware).__name__ == "SlidingWindowRateLimitingMiddleware":
            # Reset the internal state of the rate limiter
            if hasattr(middleware, "limiters"):
                middleware.limiters.clear()
    yield


@pytest.fixture
async def http_client(http_server: str) -> Client:
    """Connect to HTTP server via StreamableHttpTransport.

    Args:
        http_server: Server URL from http_server fixture

    Yields:
        Client: Connected MCP client instance
    """
    async with Client(transport=StreamableHttpTransport(http_server)) as client:
        yield client


@pytest.fixture
async def http_server_high_limit() -> str:
    """Start MCP server without rate limiting for edge case tests.

    Creates a separate FastMCP instance without rate limiting middleware
    to avoid exhaustion during edge case testing.

    Yields:
        str: Server URL (e.g., "http://127.0.0.1:8000/mcp")
    """
    port = find_available_port()
    host = "127.0.0.1"
    url = f"http://{host}:{port}/mcp"

    # Create separate mcp instance without rate limiting
    mcp_no_limit = FastMCP(
        name="math-mcp-no-limit",
        instructions="Math operations server without rate limiting for testing",
    )

    # Add middleware (logging and error handling, but no rate limiting)
    mcp_no_limit.add_middleware(StructuredLoggingMiddleware(include_payloads=True))
    mcp_no_limit.add_middleware(ErrorHandlingMiddleware())

    # Mount all tool and resource sub-servers (same as main server)
    mcp_no_limit.mount(calculate_mcp)
    mcp_no_limit.mount(matrix_mcp)
    mcp_no_limit.mount(persistence_mcp)
    mcp_no_limit.mount(visualization_mcp)
    mcp_no_limit.mount(resources_mcp)

    # Start server in background task
    server_task = asyncio.create_task(
        mcp_no_limit.run_http_async(host=host, port=port, show_banner=False, log_level="error")
    )

    # Give server time to start
    await asyncio.sleep(0.5)

    try:
        yield url
    finally:
        # Cleanup: cancel server task
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.fixture
async def http_client_high_limit(http_server_high_limit: str) -> Client:
    """Connect to high-limit HTTP server.

    Args:
        http_server_high_limit: Server URL from http_server_high_limit fixture

    Yields:
        Client: Connected MCP client instance
    """
    async with Client(transport=StreamableHttpTransport(http_server_high_limit)) as client:
        yield client

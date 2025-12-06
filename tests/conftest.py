"""Shared test fixtures for all tests."""

import asyncio

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.utilities.tests import find_available_port

from math_mcp.server import mcp


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

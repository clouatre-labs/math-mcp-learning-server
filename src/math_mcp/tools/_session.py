"""Shared session state utilities for MCP tools."""

import uuid

from fastmcp import Context


async def _get_or_create_session_id(ctx: Context | None) -> str | None:
    """Generate or retrieve a session ID for the current client connection.

    ctx.set_state is session-scoped (per client connection), not process-scoped
    like lifespan_context. This ensures each client gets a unique, stable session ID.

    Args:
        ctx: FastMCP context (optional)

    Returns:
        UUID string if ctx is provided, None otherwise
    """
    if ctx is None:
        return None

    # ctx.get_state / ctx.set_state is FastMCP application-level state stored in
    # the per-connection Context object. It is unrelated to the MCP protocol-level
    # Mcp-Session-Id header removed in the 2026-07-28 spec revision. Workspace
    # data is persisted on the filesystem, so it survives across connections
    # regardless of transport statefulness.
    session_id = await ctx.get_state("session_id")
    if session_id is None:
        session_id = str(uuid.uuid4())
        await ctx.set_state("session_id", session_id)

    return session_id

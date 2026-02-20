# ADR-003: FastMCP 3.0 Upgrade

## Status
Accepted

## Context
The project was originally built on FastMCP 2.x, which lacked composition APIs and structured context patterns. As the codebase grew modular (ADR-002), the team needed FastMCP 3.0's new capabilities to support the mount pattern and middleware stack. The upgrade was necessary to enable the architecture described in ADR-002.

## Decision
Upgrade to FastMCP 3.0 (specified in pyproject.toml, line 24: `fastmcp>=3.0.0`). This unlocks three key features:

1. **Composition API**: `mcp.mount()` enables mounting sub-servers into a root server (used in ADR-002)
2. **Session-scoped state**: `ctx.set_state()` / `ctx.get_state()` for cross-tool state sharing within a session
3. **Middleware stack**: Built-in middleware support (StructuredLogging, ErrorHandling, RateLimiting)
4. **Optional context pattern**: `ctx: SkipValidation[Context | None] = None` allows tools to work with or without MCP runtime context

**Optional context signature** (all tools in src/math_mcp/tools/):
```python
ctx: SkipValidation[Context | None] = None
```

Must be guarded before use:
```python
if ctx:
    await ctx.info("message")
```

## Consequences

**Gained:**
- Modular composition via mount pattern (enables ADR-002)
- Middleware stack for cross-cutting concerns (logging, error handling, rate limiting)
- Session-scoped state for stateful operations (e.g., workspace persistence)
- Tools can work standalone or with full MCP context

**Changed:**
- Provider/Transform architecture (internal; no user-facing impact)
- Context injection pattern (optional, not required)
- Middleware ordering matters (applied in registration order)

**Removed/Deprecated:**
- FastMCP 2.x APIs (no longer supported)

Reference: https://gofastmcp.com/changelog for full 3.0 release notes.

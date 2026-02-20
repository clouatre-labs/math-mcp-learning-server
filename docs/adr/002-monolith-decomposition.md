# ADR-002: Monolith-then-Modules Decomposition

## Status
Accepted

## Context
The project began as a single `server.py` file containing all tools, resources, and middleware. As functionality grew (calculate, matrix, persistence, visualization), the monolith became harder to test independently and reason about. The team needed a decomposition strategy that preserved the single entry point while enabling modular development.

## Decision
Decompose into a composition root pattern using FastMCP's `mcp.mount()` API. The root server (`server.py`) remains the composition root; each tool category becomes an independent FastMCP sub-server mounted into the root.

**Composition pattern** (server.py, lines 54-65):
```python
mcp = FastMCP(
    name="Math Learning Server",
    lifespan=app_lifespan,
    instructions="...",
)

# Mount sub-server tools using FastMCP composition pattern
mcp.mount(calculate_mcp)
mcp.mount(matrix_mcp)
mcp.mount(persistence_mcp)
mcp.mount(visualization_mcp)
mcp.mount(resources_mcp)
```

Middleware (StructuredLogging, ErrorHandling, RateLimiting) is applied once at the root level (lines 77-81); all mounted sub-servers inherit them automatically.

## Consequences

**Gained:**
- Independent testing per module (each sub-server can be tested in isolation)
- Clear separation of concerns (calculate, matrix, persistence, visualization are independent)
- Easier to extend (new tool categories can be added as new sub-servers)
- Single middleware stack applied once; no duplication

**Trade-offs:**
- Slightly more boilerplate (each sub-server needs its own FastMCP instance)
- Debugging requires understanding the mount hierarchy
- Middleware ordering matters; incorrect order can cause unexpected behavior

This approach balances simplicity (single entry point) with modularity (independent sub-servers).

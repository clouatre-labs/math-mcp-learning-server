# ADR-003: FastMCP 3.0 Early Adoption

## Status
Accepted

## Context
The project was built on FastMCP 2.x. The monolith decomposition (ADR-002) was completed on Feb 14-15,
2026 using FastMCP 2.x APIs. FastMCP 3.0 released on Feb 18, 2026, introducing a stable `mcp.mount()`
composition API, a first-class middleware stack, and the optional context injection pattern. There were
no blocking issues with 2.x; the upgrade was opportunistic.

## Decision
Adopt FastMCP 3.0 on release day (Feb 19, 2026). The project targets the latest stable abstraction
rather than maintaining compatibility with superseded APIs. FastMCP is the high-level framework of
choice; upgrading immediately avoids accumulating 2.x idioms that would require migration later.

Key gains over 2.x:

- `mcp.mount()` is now the stable composition API (used in `server.py`, lines 54-65)
- Middleware stack is first-class; ordering is explicit and documented
- `SkipValidation[Context | None]` optional context pattern enables tools to run standalone or
  with full MCP context without branching the function signature

## Consequences

**Gained:**
- No legacy 2.x patterns in the codebase; clean baseline for future upgrades
- Middleware applied once at root; all sub-servers inherit automatically
- Tools are testable without an MCP runtime (optional context, never required)

**Accepted:**
- FastMCP 3.0 drops 2.x APIs; no backward compatibility with 2.x clients
- Early adoption means relying on a freshly released version; mitigated by FastMCP's
  active maintenance and the project's comprehensive test suite (154 tests)

Reference: https://gofastmcp.com/changelog

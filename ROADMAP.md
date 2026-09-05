# Roadmap

Ideas and direction for the Math MCP Learning Server. Not a commitment schedule.

## Core Principle

Build capabilities LLMs lack natively: **persistent state**, **visual output**, and **high-performance computing**. LLMs already excel at math explanations and reasoning -- we focus on what they can't do.

## Completed

- **Persistent Workspace** (v0.2.0) -- Cross-session state management, transport-agnostic
- **Visualization** (v0.6.0--v0.7.0) -- Function plots, histograms, scatter/line/box/financial charts
- **Production Hardening** (v0.9.0) -- Rate limiting, input validation, structured logging, CI matrix
- **Matrix Operations** (v0.10.0) -- Multiply, transpose, determinant, inverse, eigenvalues via NumPy
- **FastMCP Upgrade** (v0.11.0) -- Upgraded to FastMCP 3.0; migrated to [PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp); adopted streamable-http transport
- **Test Coverage >90%** (v0.11.x) -- Annotation tests, prompts testing, and 90% code coverage enforced in CI
- **MCP Resources and Prompts Testing** (v0.11.x) -- Complete protocol validation via test_annotations.py and test_agent_card.py

## Upcoming

### FastMCP Features

New capabilities available with the 3.0 upgrade:

- ResponseLimitingMiddleware for output size control
- `ctx.transport` for transport-aware tool behavior
- Lifespan composition for modular startup/shutdown
- OpenTelemetry instrumentation support

### Production Hardening

- Load testing and memory profiling
- Performance regression detection

## Future Considerations

- Monte Carlo simulations
- Advanced optimization algorithms
- Real-time data integration (deferred -- unclear educational benefit)

## Architecture Principles

- **Single server** -- one focused MCP, not multiple servers
- **Transport agnostic** -- same functionality across stdio/HTTP (streamable-http)
- **Progressive enhancement** -- advanced features are optional extras
- **Minimal core dependencies** -- keep base installation lightweight
- **Graceful degradation** -- clear errors when optional features are unavailable

## What We Won't Build

- Math explanations, step-by-step solving, proofs (LLMs do this better)
- Multiple separate servers (overengineering)
- Heavy core dependencies (use optional extras)
- Transport-specific implementations

## Decision Framework

**Include a feature if it:**

- Provides capability LLMs can't achieve natively
- Works identically across all transports
- Uses optional dependencies (not core)

**Skip a feature if it:**

- Duplicates existing LLM capabilities
- Only works with specific transports
- Adds complexity without unique value

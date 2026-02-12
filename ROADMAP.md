# Roadmap

Ideas and direction for the Math MCP Learning Server. Not a commitment schedule.

## Core Principle

Build capabilities LLMs lack natively: **persistent state**, **visual output**, and **high-performance computing**. LLMs already excel at math explanations and reasoning -- we focus on what they can't do.

## Completed

- **Persistent Workspace** (v0.2.0) -- Cross-session state management, transport-agnostic
- **Visualization** (v0.6.0--v0.7.0) -- Function plots, histograms, scatter/line/box/financial charts
- **Production Hardening** (v0.9.0) -- Rate limiting, input validation, structured logging, CI matrix
- **Matrix Operations** (v0.10.0) -- Multiply, transpose, determinant, inverse, eigenvalues via NumPy

## Upcoming

### FastMCP 3.0 Upgrade

**Status:** Waiting for stable release (beta 2 released Feb 8, 2026).

FastMCP 3.0 is designed as a low-friction upgrade. Per the [official upgrade guide](https://gofastmcp.com/development/upgrade-guide), most servers need no code changes. Our codebase uses none of the affected breaking changes (WSTransport, auth provider env vars, component enable/disable API, listing-methods-as-dicts, PromptMessage, sync ctx.set_state/get_state).

New capabilities available after upgrade:
- Providers and Transforms (component-level composition and filtering)
- Per-component authorization and versioning
- Hot reload during development
- OpenTelemetry instrumentation
- Decorated functions remain directly callable (useful for testing)

**Migration scope:** Likely minimal. Our middleware (`add_middleware()`) is unchanged in 3.0. Primary effort is testing, not rewriting.

**Action:** Track [FastMCP releases](https://github.com/jlowin/fastmcp/releases). Upgrade when stable lands.

### Test Coverage Expansion

- MCP resources and prompts testing (currently untested via protocol)
- End-to-end workflow tests (calculate, save, load, visualize)
- Property-based testing with Hypothesis

### Production Hardening

- Load testing and memory profiling
- Test coverage reporting (target: >90%)
- Performance regression detection

## Future Considerations

- Monte Carlo simulations
- Advanced optimization algorithms
- Real-time data integration (deferred -- unclear educational benefit)

## Architecture Principles

- **Single server** -- one focused MCP, not multiple servers
- **Transport agnostic** -- same functionality across stdio/HTTP/SSE
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

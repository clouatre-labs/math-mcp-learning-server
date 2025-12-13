# Roadmap

This document tracks the evolution from a basic math calculator to a persistent quantitative workspace that does what LLMs can't: maintain state, generate visuals, and perform high-performance computing.

## Core Principle

Build capabilities LLMs lack natively:
- **Persistent state** across sessions
- **Visual output** (plots, charts)
- **High-performance computing** (matrix operations, simulations)

LLMs already excel at math explanations and reasoning. We focus on what they can't do.

## Implementation Status

### Phase 1: Persistent Workspace ✅ COMPLETE (v0.2.0)

Cross-session state management with transport-agnostic architecture. Works identically across stdio, HTTP, and SSE.

**Tools:**
- `save_calculation` - Persist calculations across sessions
- `load_variable` - Access saved values
- `math://workspace` resource - View all saved data

**Storage:** `~/.math-mcp/workspace.json` (Windows: `%LOCALAPPDATA%`)

### Phase 2: Visualization ✅ COMPLETE (v0.9.0)

Mathematical and statistical visualization capabilities.

**Tools:**
- `plot_function` - Function plots
- `plot_histogram` - Statistical histograms  
- `plot_line_chart` - Time series and trends
- `plot_scatter_chart` - Correlation analysis
- `plot_box_plot` - Distribution comparison
- `plot_financial_chart` - Financial data visualization

**Installation:** `uv pip install math-mcp-learning-server[plotting]`

### Phase 3: Real-Time Data Integration ⏭️ DEFERRED

Real-time API integration deferred to maintain project focus on educational MCP fundamentals.

**Rationale:**
- Current feature set (12 tools, 1 resource, 2 prompts) already demonstrates core MCP concepts
- API integration adds complexity without clear educational benefit for math-focused learning
- Existing tools provide sufficient examples of MCP patterns

**Deferred until:** Community feedback indicates clear need for external data integration

### Phase 4: Matrix Operations ✅ COMPLETE

**Status**: Complete (2025-12-13)  
**Duration**: 3 PRs implementing TDD cycle

**Delivered:**
- 5 matrix operation tools (multiply, transpose, determinant, inverse, eigenvalues)
- 21 comprehensive test cases (TDD RED → GREEN → REFACTOR)
- NumPy integration with optional `[scientific]` extra
- Complete documentation with examples and error handling
- DoS prevention (100x100 matrix size limit)

**PRs:**
- #106: Dependencies setup (NumPy as optional extra)
- #108: TDD RED phase (test specifications)
- #109: TDD GREEN phase (implementation)
- #110: Documentation phase (this PR)

**Technical highlights:**
- FastMCP ToolError pattern for error handling
- Complex eigenvalue formatting (real and imaginary)
- Input validation (structure, types, dimensions, size limits)
- Zero regressions (126/126 tests passing)

## Architecture Principles

- **Single server design** - One focused MCP, not multiple servers
- **Transport agnostic** - Same functionality across stdio/HTTP/SSE
- **Progressive enhancement** - Advanced features are optional
- **Minimal core dependencies** - Keep base installation lightweight
- **Graceful degradation** - Clear error messages when optional features unavailable

## Installation Patterns

```bash
# Basic (core math only)
uv pip install math-mcp-learning-server

# With visualization
uv pip install math-mcp-learning-server[plotting]

# Development
git clone https://github.com/clouatre-labs/math-mcp-learning-server
cd math-mcp-learning-server
uv sync --all-extras
uv run fastmcp dev src/math_mcp/server.py

# Cloud deployment
# Visit https://math-mcp-learning.fastmcp.app/mcp
```

## What We Won't Build

**Avoid duplicating LLM strengths:**
- Complex mathematical explanations (LLMs do this better)
- Step-by-step problem solving (LLMs excel here)
- Mathematical reasoning and proofs (native LLM capability)

**Avoid MCP anti-patterns:**
- Multiple separate servers (overengineering)
- Heavy core dependencies (use optional-dependencies)
- Transport-specific implementations (violates MCP principles)

## Decision Framework

**Include a feature if it:**
- Provides capability LLMs can't achieve natively
- Works identically across all transports
- Maintains educational value while adding real utility
- Uses optional dependencies (not core)

**Skip a feature if it:**
- Duplicates existing LLM capabilities
- Only works with specific transports
- Adds complexity without unique value

## Next Steps

### v0.11.0 - Enhanced Test Coverage & Stability

**Focus:** Complete MCP protocol testing and integration workflows

#### Testing Improvements
- [ ] **MCP Resources Testing**
  - [ ] Test `math://test` resource
  - [ ] Test `math://constants/pi` resource
  - [ ] Test `math://constants/e` resource
  - [ ] Test `math://functions` resource
  - [ ] Test `math://workspace` resource

- [ ] **MCP Prompts Testing**
  - [ ] Test `math_tutor` prompt (all topic/level combinations)
  - [ ] Test `formula_explainer` prompt (various formulas)

- [ ] **Integration Workflows**
  - [ ] Add end-to-end workflow tests (calculate → save → load → visualize)
  - [ ] Add matrix operation chain tests
  - [ ] Add statistical analysis workflow tests

- [ ] **Performance Benchmarks**
  - [ ] Matrix multiplication scaling benchmarks
  - [ ] Visualization generation benchmarks
  - [ ] Rate limiting behavior tests

- [ ] **Documentation**
  - [ ] Automate README example validation
  - [ ] Verify EXAMPLES.md accuracy

**Estimated Effort:** 10-15 hours
**Target:** Q1 2025

---

### v0.12.0 - Production Hardening

**Focus:** Advanced testing and reliability improvements

#### Advanced Testing
- [ ] Load testing (concurrent users)
- [ ] Memory profiling (large datasets)
- [ ] Fuzzing tests (random inputs)
- [ ] Property-based testing with hypothesis

#### Monitoring & Observability
- [ ] Test coverage reporting (target: >90%)
- [ ] Performance regression detection
- [ ] Automated test report generation

**Estimated Effort:** 15-20 hours
**Target:** Q2 2025

---

### Future Considerations

**Computational features:**
- Monte Carlo simulations
- Advanced optimization algorithms
- Community-requested features

**Testing enhancements:**
- Documentation validation (automated example testing)
- Load testing at scale
- Fuzzing with property-based testing

---

*This roadmap transforms a basic calculator into a persistent quantitative workspace that does what LLMs can't: maintain state, generate visuals, and perform high-performance matrix computations.*

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

### Phase 4: Matrix Operations 🎯 NEXT (v0.10.0)

High-performance matrix operations beyond LLM computational capabilities.

**Planned tools:**
```python
matrix_multiply(matrix_a, matrix_b)
matrix_inverse(matrix)
matrix_determinant(matrix)
matrix_eigenvalues(matrix)
matrix_transpose(matrix)
solve_linear_system(coefficients, constants)
```

**Installation:** `uv pip install math-mcp-learning-server[scientific]`

**Dependencies:** NumPy for optimized numerical computation

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

**Immediate (v0.10.0):**
- Phase 4: Matrix operations implementation
- Add linear algebra capabilities (multiply, inverse, determinant, eigenvalues)
- Maintain educational focus while adding high-performance computing

**Future considerations:**
- Monte Carlo simulations
- Advanced optimization algorithms
- Community-requested features

---

*This roadmap transforms a basic calculator into a persistent quantitative workspace that does what LLMs can't: maintain state, generate visuals, and perform high-performance matrix computations.*

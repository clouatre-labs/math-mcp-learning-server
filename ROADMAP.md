# Roadmap

This document tracks the evolution from a basic math calculator to a persistent quantitative workspace that does what LLMs can't: maintain state, generate visuals, and access real-time data.

## Core Principle

Build capabilities LLMs lack natively:
- **Persistent state** across sessions
- **Visual output** (plots, charts)
- **Real-time data** via APIs
- **High-performance computing**

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

### Phase 3: Real-Time Data Integration 🎯 NEXT

Access live data LLMs can't reach directly.

**Potential APIs:**
- **Financial:** Alpha Vantage, Twelvedata, Yahoo Finance
- **Weather:** OpenWeatherMap (1M free calls/month, 100M for education)
- **Economic:** FRED (Federal Reserve), World Bank Open Data
- **Scientific:** NASA APIs, Open-Meteo

**Example tools:**
```python
get_stock_price(symbol, provider="alpha_vantage")
calculate_portfolio_value(holdings)
get_weather_data(location, provider="openweather")
get_economic_indicators(indicator, source="fred")
```

**Installation:** `uv pip install math-mcp-learning-server[data]`

### Phase 4: High-Performance Computing 🔮 FUTURE

Computational capabilities beyond LLM scope.

**Example tools:**
```python
matrix_operations(operation, matrices)
monte_carlo_simulation(params, iterations)
optimize_portfolio(returns, risks, constraints)
```

**Installation:** `uv pip install math-mcp-learning-server[scientific]`

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
- Evaluate Phase 3 priority: Do we need real-time data integration?
- Consider if current feature set meets educational goals
- Gather user feedback on visualization tools

**Future (if needed):**
- Phase 3: Real-time data APIs (financial, weather, economic)
- Phase 4: High-performance computing (matrix ops, simulations)

---

*This roadmap transforms a basic calculator into a persistent quantitative workspace that does what LLMs can't: maintain state, generate visuals, and potentially access real-time data.*
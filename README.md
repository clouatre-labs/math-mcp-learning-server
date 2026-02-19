<!-- mcp-name: io.github.clouatre-labs/math-mcp-learning-server -->

# Math MCP Learning Server

[![PyPI version](https://badge.fury.io/py/math-mcp-learning-server.svg)](https://pypi.org/project/math-mcp-learning-server/)
[![Python](https://img.shields.io/pypi/pyversions/math-mcp-learning-server)](https://pypi.org/project/math-mcp-learning-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Educational MCP server with 17 tools, persistent workspace, and cloud hosting. Built with [FastMCP 3.0](https://github.com/PrefectHQ/fastmcp) and the official [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk).

**Available on:**
- [Official MCP Registry](https://registry.modelcontextprotocol.io/) - `io.github.clouatre-labs/math-mcp-learning-server`
- [PyPI](https://pypi.org/project/math-mcp-learning-server/) - `math-mcp-learning-server`

## Requirements

Requires an MCP client:

- **Claude Desktop** - Anthropic's desktop app
- **Claude Code** - Command-line MCP client
- **Goose** - Open-source AI agent framework
- **OpenCode** - Open-source MCP client by SST
- **Kiro** - AWS's AI assistant
- **Gemini CLI** - Google's command-line tool
- Any MCP-compatible client

## Quick Start

### Cloud (No Installation)

Connect your MCP client to the hosted server:

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "math-cloud": {
      "transport": "http",
      "url": "https://math-mcp.fastmcp.app/mcp"
    }
  }
}
```

### Local Installation

**Automatic with uvx** (recommended):

```json
{
  "mcpServers": {
    "math": {
      "command": "uvx",
      "args": ["math-mcp-learning-server"]
    }
  }
}
```

**Manual installation:**
```bash
# Basic installation
uv tool install math-mcp-learning-server

# With matrix operations support
uv tool install math-mcp-learning-server[scientific]

# With visualization support
uv tool install math-mcp-learning-server[plotting]

# All features
uv tool install math-mcp-learning-server[scientific,plotting]
```

## Tools

| Category | Tool | Description |
|----------|------|-------------|
| **Workspace** | `save_calculation` | Save calculations to persistent storage |
| | `load_variable` | Retrieve previously saved calculations |
| **Math** | `calculate` | Safely evaluate mathematical expressions |
| | `statistics` | Statistical analysis (mean, median, mode, std_dev, variance) |
| | `compound_interest` | Calculate compound interest for investments |
| | `convert_units` | Convert between units (length, weight, temperature) |
| **Matrix** | `matrix_multiply` | Multiply two matrices |
| | `matrix_transpose` | Transpose a matrix |
| | `matrix_determinant` | Calculate matrix determinant |
| | `matrix_inverse` | Calculate matrix inverse |
| | `matrix_eigenvalues` | Calculate eigenvalues |
| **Visualization** | `plot_function` | Plot mathematical functions |
| | `create_histogram` | Create statistical histograms |
| | `plot_line_chart` | Create line charts |
| | `plot_scatter_chart` | Create scatter plots |
| | `plot_box_plot` | Create box plots |
| | `plot_financial_line` | Create financial line charts |

## Resources

- `math://workspace` - Persistent calculation workspace summary
- `math://history` - Chronological calculation history
- `math://functions` - Available mathematical functions reference
- `math://constants/{constant}` - Mathematical constants (pi, e, golden_ratio, etc.)
- `math://test` - Server health check

## Prompts

- `math_tutor` - Structured tutoring prompts (configurable difficulty)
- `formula_explainer` - Formula explanation with step-by-step breakdowns

See [Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md) for detailed examples.

## Development

```bash
# Clone and setup
git clone https://github.com/clouatre-labs/math-mcp-learning-server.git
cd math-mcp-learning-server
uv sync --extra dev --extra plotting

# Test server locally
uv run fastmcp dev src/math_mcp/server.py
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific test category
uv run pytest tests/test_matrix_operations.py -v
```

**Test Suite:** 122 tests across 6 categories (Agent Card, HTTP Integration, Math, Matrix, Persistence, Visualization)

### Code Quality

```bash
# Linting
uv run ruff check

# Formatting
uv run ruff format --check

# Type checking
uv run pyright src/

# Security checks
uv run ruff check --select S
```

## Security

The `calculate` tool uses restricted `eval()` with a whitelist of allowed characters and functions, restricted global scope (only `math` module and `abs`), and no access to dangerous built-ins or imports. All tool inputs are validated with Pydantic models. File operations are restricted to the designated workspace directory. Complete type hints and validation are enforced for all operations.

## Links

- [Cloud Deployment Guide](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/CLOUD_DEPLOYMENT.md)
- [Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md)
- [Contributing Guidelines](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md)
- [Maintainer Guide](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/MAINTAINER_GUIDE.md)
- [Roadmap](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/ROADMAP.md)
- [Code of Conduct](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CODE_OF_CONDUCT.md)
- [License](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/LICENSE)

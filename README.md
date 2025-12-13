# Math MCP Learning Server

[![PyPI version](https://badge.fury.io/py/math-mcp-learning-server.svg)](https://pypi.org/project/math-mcp-learning-server/)
[![Python](https://img.shields.io/pypi/pyversions/math-mcp-learning-server)](https://pypi.org/project/math-mcp-learning-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/clouatre-labs/math-mcp-learning-server/actions/workflows/ci.yml/badge.svg)](https://github.com/clouatre-labs/math-mcp-learning-server/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- mcp-name: io.github.clouatre-labs/math-mcp-learning-server -->

Educational MCP server demonstrating persistent workspace patterns and mathematical operations. Built with [FastMCP 2.0](https://github.com/jlowin/fastmcp) and the official [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk).

**Available on:**
- [Official MCP Registry](https://registry.modelcontextprotocol.io/) - `io.github.clouatre-labs/math-mcp-learning-server`
- [PyPI](https://pypi.org/project/math-mcp-learning-server/) - `math-mcp-learning-server`
- [FastMCP Cloud](https://math-mcp.fastmcp.app/mcp) - No installation required

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
uv pip install math-mcp-learning-server

# With matrix operations support
uv pip install math-mcp-learning-server[scientific]

# With visualization support
uv pip install math-mcp-learning-server[plotting]

# All features
uv pip install math-mcp-learning-server[scientific,plotting]
```

## Features

- **Cross-Session Persistence**: Variables survive server restarts and session changes
- **Safe Expression Evaluation**: Secure mathematical expression parsing with security logging
- **Statistical Analysis**: Mean, median, mode, standard deviation, variance
- **Financial Calculations**: Compound interest with formatted output
- **Unit Conversions**: Length, weight, temperature
- **Function Plotting**: Base64-encoded PNG plots (matplotlib)
- **Statistical Histograms**: Distribution visualization with indicators
- **Type Safety**: Full Pydantic validation for all inputs
- **Comprehensive Testing**: Complete coverage with security validation
- **Cross-Platform Storage**: Windows, macOS, Linux support

## MCP Implementation

**Primitives:**
- **Tools**: 17 tools for mathematical operations, persistence, visualization, and matrix operations
- **Resources**: 1 resource (`math://workspace`) for viewing persistent workspace
- **Prompts**: 2 prompts (`math_tutor`, `formula_explainer`) for educational interactions

**Transports:**
- **stdio** - Standard input/output for local clients
- **HTTP/SSE** - Server-Sent Events for cloud/web clients

Workspace persists across all transport modes and sessions.

## Available Tools

### Persistent Workspace Tools
- `save_calculation`: Save calculations to persistent storage for cross-session access
- `load_variable`: Access previously saved calculations from any MCP client session

### Mathematical Tools
- `calculate`: Safely evaluate mathematical expressions (supports basic ops and math functions)
- `statistics`: Perform statistical calculations (mean, median, mode, std_dev, variance)
- `compound_interest`: Calculate compound interest for investments
- `convert_units`: Convert between units (length, weight, temperature)

### Visualization Tools
- `plot_function`: Generate mathematical function plots (base64-encoded PNG)
- `create_histogram`: Create statistical histograms with distribution analysis
- `plot_line_chart`: Create line charts for sequential data visualization
- `plot_scatter_chart`: Create scatter plots for relationship analysis
- `plot_box_plot`: Create box plots for statistical distribution comparison
- `plot_financial_line`: Create financial trend plots with bullish/bearish/volatile patterns

### Matrix Operations (requires `[scientific]` extra)
- `matrix_multiply`: Multiply two matrices with dimension validation
- `matrix_transpose`: Transpose a matrix (swap rows and columns)
- `matrix_determinant`: Calculate determinant of square matrices
- `matrix_inverse`: Compute matrix inverse with singular matrix detection
- `matrix_eigenvalues`: Calculate eigenvalues (supports complex numbers)

**Note**: Matrix operations require NumPy. Install with `uv pip install math-mcp-learning-server[scientific]`

See [Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md) for detailed examples of each tool.

## Available Prompts

### Educational Prompts
- `math_tutor`: Generate structured tutoring prompts for mathematical concepts (configurable difficulty level)
- `formula_explainer`: Generate comprehensive formula explanation prompts with step-by-step breakdowns

See [Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md) for detailed examples of each prompt.

## Available Resources

### `math://workspace`
View your complete persistent workspace with all saved calculations, metadata, and statistics.

**Returns:**
- All saved variables with expressions and results
- Educational metadata (difficulty, topic)
- Workspace statistics (total calculations, session count)
- Timestamps for tracking calculation history

## Development

```bash
# Clone and setup
git clone https://github.com/clouatre-labs/math-mcp-learning-server.git
cd math-mcp-learning-server
uv sync --extra dev --extra plotting

# Run tests and checks
uv run pytest tests/ -v
uv run ruff check
uv run ruff format --check

# Test server locally
uv run fastmcp dev src/math_mcp/server.py
```

See [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md) for detailed guidelines.

## Documentation

- **[Cloud Deployment Guide](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/CLOUD_DEPLOYMENT.md)**: FastMCP Cloud deployment instructions and configuration
- **[Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md)**: Practical examples for all tools and resources
- **[Contributing Guidelines](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md)**: Development workflow, code standards, and testing procedures
- **[Roadmap](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/ROADMAP.md)**: Planned features and enhancement opportunities
- **[Code of Conduct](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CODE_OF_CONDUCT.md)**: Community guidelines and expectations

## Security

### Safe Expression Evaluation

The `calculate` tool uses restricted `eval()` with:
- Whitelist of allowed characters and functions
- Restricted global scope (only `math` module and `abs`)
- No access to dangerous built-ins or imports
- Security logging for potentially dangerous attempts

### MCP Security Best Practices

- **Input Validation**: All tool inputs validated with Pydantic models
- **Error Handling**: Structured errors without exposing sensitive information
- **Least Privilege**: File operations restricted to designated workspace directory
- **Type Safety**: Complete type hints and validation for all operations

## Contributing

We welcome contributions! See [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md) for development workflow, code standards, and testing procedures.

For maintainers: See [MAINTAINER_GUIDE.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/MAINTAINER_GUIDE.md) for release procedures.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to hugues+mcp-coc@linux.com.

## License

[MIT License](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/LICENSE) - Full license details available in the LICENSE file.

# Math MCP Learning Server

[![PyPI version](https://badge.fury.io/py/math-mcp-learning-server.svg)](https://pypi.org/project/math-mcp-learning-server/)

**Cloud hosted:** Connect any MCP client to [https://math-mcp-learning.fastmcp.app/mcp](https://math-mcp-learning.fastmcp.app/mcp) (MCP client required, no local server install needed)

A persistent quantitative workspace built as a Model Context Protocol (MCP) server. This project demonstrates enterprise-grade patterns for MCP development, featuring cross-session state persistence - a unique capability that most LLMs cannot achieve natively.

Perfect for learning MCP fundamentals, demonstrating professional patterns, and serving as a foundation for advanced mathematical workflows.

Built with [FastMCP 2.0](https://github.com/jlowin/fastmcp) and the official [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk).

## Requirements

**This is an MCP server** - it requires an MCP client to use. Supported clients include:

- **Claude Desktop** - Anthropic's desktop app with native MCP support
- **Claude Code** - Command-line MCP client from Anthropic
- **OpenCode** - Open-source MCP client
- **Amazon Q** - AWS's AI assistant with MCP support
- **Codex CLI** - GitHub Codex command-line interface
- **Gemini CLI** - Google's Gemini command-line tool
- Any other MCP-compatible client

**Cannot run standalone** - The server must be connected through an MCP client.

## Quick Start

### Option 1: Try it Now (Cloud)

Connect your MCP client to the hosted server - no local installation required!

**Claude Desktop:**
```json
{
  "mcpServers": {
    "math-cloud": {
      "transport": "http",
      "url": "https://math-mcp-learning.fastmcp.app/mcp"
    }
  }
}
```

**Claude Code:**
```bash
claude mcp add math-cloud https://math-mcp-learning.fastmcp.app/mcp
```

### Option 2: Run Locally

Choose one of two installation methods:

**Method A: Automatic with uvx (recommended)**

Configure your MCP client to use `uvx` - no manual installation needed:

**Claude Desktop:**
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

**Claude Code:**
```bash
claude mcp add math uvx math-mcp-learning-server
```

**Method B: Manual installation**

1. Install the package:
```bash
uv pip install math-mcp-learning-server
```

2. Configure your MCP client:

**Claude Desktop:**
```json
{
  "mcpServers": {
    "math": {
      "command": "math-mcp-learning-server"
    }
  }
}
```

**Claude Code:**
```bash
claude mcp add math math-mcp-learning-server
```

## Features

### Persistent Workspace
- **Cross-Session State**: Save calculations and access them across different MCP client sessions
- **Persistent Storage**: Variables survive server restarts and session changes
- **Cross-Platform**: Works on Windows (`%LOCALAPPDATA%`), macOS, and Linux (`~/.math-mcp`)
- **Thread-Safe**: Concurrent access with atomic file operations

### Mathematical Operations
- **Safe Expression Evaluation**: Securely evaluate mathematical expressions with enhanced error handling
- **Statistical Analysis**: Calculate mean, median, mode, standard deviation, and variance
- **Financial Calculations**: Compound interest calculations with formatted output
- **Unit Conversions**: Length, weight, and temperature conversions

### Visual Learning
- **Function Plotting**: Generate mathematical function plots with base64-encoded PNG output
- **Statistical Histograms**: Visualize data distributions with mean and median indicators
- **Cloud Deployment**: Visualization tools (matplotlib) are included in the cloud deployment
- **Local Usage**: Install with `uv pip install math-mcp-learning-server[plotting]` for local usage with plotting features

### Enterprise-Grade Quality
- **Security Logging**: Monitor and log potentially dangerous expression attempts
- **Type Safety**: Full Pydantic validation for inputs and structured content responses
- **Comprehensive Testing**: Complete test coverage with security and edge case validation
- **Zero Core Dependencies**: Core persistence features use only Python stdlib

## MCP Architecture

This server implements the following MCP primitives:

- **Tools**: 8 tools for mathematical operations, persistence, and visualization
- **Resources**: 1 resource (`math://workspace`) for viewing the persistent workspace
- **Prompts**: 0 (future enhancement opportunity)

## Transport Support

This server implements **all official MCP transport modes** per the [MCP specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports):

- **stdio** - Standard input/output for local clients (Claude Desktop, Claude Code)
- **HTTP/SSE** - Streamable HTTP with Server-Sent Events for cloud/web clients

**Transport-agnostic workspace:** Your saved calculations persist across all transport modes and sessions.

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

See [Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md) for detailed examples of each tool.

## Available Resources

### `math://workspace`
View your complete persistent workspace with all saved calculations, metadata, and statistics.

**Returns:**
- All saved variables with expressions and results
- Educational metadata (difficulty, topic)
- Workspace statistics (total calculations, session count)
- Timestamps for tracking calculation history

## Development

### Project Structure
```
math-mcp-learning-server/
├── src/math_mcp/
│   ├── server.py          # Main MCP server implementation
│   └── persistence/       # Persistent workspace functionality
├── tests/
│   ├── test_math_operations.py
│   └── test_persistence.py
├── docs/
│   ├── CLOUD_DEPLOYMENT.md
│   └── EXAMPLES.md
├── pyproject.toml
└── README.md
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/clouatre-labs/math-mcp-learning-server.git
cd math-mcp-learning-server

# Install dependencies (includes plotting support)
uv sync --extra dev --extra plotting

# Run tests
uv run pytest tests/ -v

# Run type checking
uv run mypy src/

# Run linting
uv run ruff check

# Test the MCP server with FastMCP dev mode
uv run fastmcp dev src/math_mcp/server.py
# Then connect via MCP client (Claude Desktop, Claude Code, etc.)
```

### Adding New Tools

1. Define input/output models with Pydantic
2. Add `@mcp.tool()` decorated function in `src/math_mcp/server.py`
3. Implement tool logic with proper validation
4. Add corresponding tests in `tests/`

See [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md) for detailed guidelines.

## Documentation

- **[Cloud Deployment Guide](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/CLOUD_DEPLOYMENT.md)**: FastMCP Cloud deployment instructions and configuration
- **[Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md)**: Practical examples for all tools and resources
- **[Contributing Guidelines](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md)**: Development workflow, code standards, and testing procedures
- **[Future Improvements](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/FUTURE_IMPROVEMENTS.md)**: Roadmap and enhancement opportunities
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

## Publishing

This package is published to PyPI via GitHub Actions workflow. The workflow is triggered on:
- New releases (tags matching `v*`)
- Manual workflow dispatch

**Publishing workflow:**
1. Create and push a version tag: `git tag v0.6.7 && git push origin v0.6.7`
2. GitHub Actions automatically builds and publishes to PyPI
3. Release notes are generated from commit messages

The package follows semantic versioning and includes comprehensive metadata for discoverability on PyPI.

## Contributing

We welcome contributions! This project follows a fast and minimal philosophy while maintaining educational value and professional standards.

**Quick Start for Contributors:**
1. Fork the repository
2. Set up development environment: `uv sync --extra dev --extra plotting`
3. Create feature branch: `git checkout -b feature/your-feature`
4. Make changes and add tests
5. Run quality checks: `uv run pytest && uv run mypy src/ && uv run ruff check`
6. Submit a pull request

See [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md) for detailed guidelines including:
- Development workflow and Git practices
- Code standards and security requirements
- Testing procedures and quality assurance
- Architecture guidelines and best practices

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to hugues+mcp-coc@linux.com.

## License

[MIT License](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/LICENSE) - Full license details available in the LICENSE file.

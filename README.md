<!-- mcp-name: io.github.clouatre-labs/math-mcp-learning-server -->

<h1 align="center">math-mcp-learning-server</h1>

<p align="center">
  <a href="https://pypi.org/project/math-mcp-learning-server/"><img alt="PyPI" src="https://img.shields.io/pypi/v/math-mcp-learning-server?style=for-the-badge&color=3b82f6" height="20"></a>
  <a href="https://pypi.org/project/math-mcp-learning-server/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/math-mcp-learning-server?style=for-the-badge" height="20"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-blue.svg?style=for-the-badge" height="20"></a>
  <a href="https://api.reuse.software/info/github.com/clouatre-labs/math-mcp-learning-server"><img alt="REUSE" src="https://img.shields.io/reuse/compliance/github.com/clouatre-labs/math-mcp-learning-server?style=for-the-badge" height="20"></a>
  <a href="https://www.bestpractices.dev/projects/12334"><img alt="OpenSSF Best Practices" src="https://img.shields.io/cii/level/12334?style=for-the-badge" height="20"></a>
</p>

<p align="center"><strong>Educational MCP server with 17 tools, persistent workspace, and cloud hosting.</strong> Built with <a href="https://gofastmcp.com">FastMCP</a> and the official <a href="https://github.com/modelcontextprotocol/python-sdk">Model Context Protocol Python SDK</a>.</p>

<p align="center">
  Available on the <a href="https://registry.modelcontextprotocol.io/">MCP Registry</a> (<code>io.github.clouatre-labs/math-mcp-learning-server</code>) and <a href="https://pypi.org/project/math-mcp-learning-server/">PyPI</a>.
</p>

## Demo

![math-mcp Demo](https://raw.githubusercontent.com/clouatre-labs/math-mcp-learning-server/main/assets/demo.gif)

See [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md#demo-gif) for instructions to record your own demo.

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

```json
{
  "mcpServers": {
    "math": {
      "command": "uvx",
      "args": ["math-mcp-learning-server[scientific,plotting]"]
    }
  }
}
```

For other installation options (basic, scientific-only, plotting-only), see [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md).

## Tools

| Category | Tool | Description |
|----------|------|-------------|
| **Workspace** | `workspace_save` | Save calculations to persistent storage |
| | `workspace_load` | Retrieve previously saved calculations |
| **Math** | `calc_expression` | Safely evaluate mathematical expressions |
| | `calc_statistics` | Statistical analysis (mean, median, mode, std_dev, variance) |
| | `calc_interest` | Calculate compound interest for investments |
| | `calc_units` | Convert between units (length, weight, temperature) |
| **Matrix** | `matrix_multiply` | Multiply two matrices |
| | `matrix_transpose` | Transpose a matrix |
| | `matrix_determinant` | Calculate matrix determinant |
| | `matrix_inverse` | Calculate matrix inverse |
| | `matrix_eigenvalues` | Calculate eigenvalues |
| **Visualization** | `plot_function` | Plot mathematical functions |
| | `plot_histogram` | Create statistical histograms |
| | `plot_line_chart` | Create line charts |
| | `plot_scatter` | Create scatter plots |
| | `plot_box_plot` | Create box plots |
| | `plot_financial_line` | Create financial line charts |

## Resources

- `math://workspace` - Persistent calculation workspace summary
- `math://history` - Chronological calculation history
- `math://functions` - Available mathematical functions reference
- `math://constants/{constant}` - Mathematical constants (pi, e, golden_ratio, etc.)
- `math://catalog/tools` - Tool catalog with metadata and usage examples
- `math://variables` - Active variables in the current workspace
- `math://test` - Server health check

## Prompts

- `math_tutor` - Structured tutoring prompts (configurable difficulty)
- `formula_explainer` - Formula explanation with step-by-step breakdowns

See [Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md) for detailed examples.

## Development

See [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md) for development setup, testing, and contribution guidelines.

## Security

- **OpenSSF Best Practices Silver** - Fewer than 1% of open source projects reach this level
- **REUSE/SPDX** - License compliance for all files
- **Signed Commits** - GPG-signed commits required
- **Dependency Scanning** - Automated updates via Renovate
- **pip-audit CVE Scanning** - Automated dependency vulnerability checks
- **gitleaks Secret Scanning** - Detects secrets in code and history
- **zizmor GitHub Actions Security** - Workflow security scanning
- **commitlint Enforcement** - Conventional commit validation in CI
- **OpenSSF Scorecard** - Continuous open source security assessment

<details>
<summary><strong>calc_expression safety</strong></summary>

The `calc_expression` tool uses restricted `eval()` with a whitelist of allowed characters and functions, restricted global scope (only `math` module and `abs`), and no access to dangerous built-ins or imports. All tool inputs are validated with Pydantic models. File operations are restricted to the designated workspace directory. Complete type hints and validation are enforced for all operations.

</details>

## Documentation

- [Architecture](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/ARCHITECTURE.md)
- [Cloud Deployment Guide](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/CLOUD_DEPLOYMENT.md)
- [Usage Examples](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/docs/EXAMPLES.md)
- [Contributing Guidelines](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md)
- [Maintainer Guide](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/MAINTAINER_GUIDE.md)
- [Roadmap](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/ROADMAP.md)
- [Code of Conduct](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CODE_OF_CONDUCT.md)
- [License](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/LICENSE)

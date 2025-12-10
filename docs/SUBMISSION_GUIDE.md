# MCP Server Publication Guide

Educational MCP server with 12 math/stats tools, persistent workspace, and cloud hosting. Demonstrates FastMCP 2.0 best practices with 86% test coverage.

**Links:** [PyPI](https://pypi.org/project/math-mcp-learning-server/) | [Cloud](https://math-mcp.fastmcp.app/mcp) | [GitHub](https://github.com/clouatre-labs/math-mcp-learning-server)

---

## Official MCP Registry

**URL:** https://registry.modelcontextprotocol.io/  
**Docs:** https://github.com/modelcontextprotocol/registry/tree/main/docs

```bash
# Install CLI
brew install mcp-publisher

# Authenticate
mcp-publisher login github

# Publish (requires server.json in repo root)
mcp-publisher publish

# Verify
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.clouatre-labs/math-mcp-learning-server"
```

**Requirements:**
- PyPI package published
- `<!-- mcp-name: io.github.clouatre-labs/math-mcp-learning-server -->` in README.md
- `server.json` in repository root (see repo for template)

---

## Community Registries

### modelcontextprotocol/servers
**URL:** https://github.com/modelcontextprotocol/servers  
**Method:** Pull Request to README

```markdown
- **[Math MCP Learning](https://github.com/clouatre-labs/math-mcp-learning-server)** - Educational MCP with 12 math/stats tools, persistent workspace, cloud hosting. Demonstrates FastMCP 2.0 best practices.
```

### Awesome MCP Servers
**URL:** https://github.com/mctrinh/awesome-mcp-servers  
**Method:** Pull Request

### Awesome Remote MCP Servers
**URL:** https://github.com/sylviangth/awesome-remote-mcp-servers  
**Method:** Pull Request (cloud-focused)

### FastMCP Showcase
**URL:** https://github.com/jlowin/fastmcp/blob/main/docs/community/showcase.mdx  
**Method:** Pull Request to `docs/community/showcase.mdx`

### ToolSDK MCP Registry
**URL:** https://github.com/toolsdk-ai/toolsdk-mcp-registry  
**Method:** Check repository for submission process

---

## Social

**Reddit:** r/LLM, r/LocalLLaMA, r/ClaudeAI  
**Discord:** [FastMCP](https://discord.com/invite/aGsSC3yDF4)  
**X/Twitter:** #MCP hashtag

---

## Status

| Platform | Status | Date | Notes |
|----------|--------|------|-------|
| Official MCP Registry | 🔧 Ready | 2025-12-10 | Files prepared |
| AWSome MCP | ✅ Done | 2025-12-10 | Form submitted |
| Community MCP Servers | ⏳ Pending | - | PR needed |
| Awesome Remote MCP | ⏳ Pending | - | PR needed |
| FastMCP Showcase | ⏳ Pending | - | PR needed |
| ToolSDK Registry | ⏳ Pending | - | Check process |
| Awesome MCP Servers | ⏳ Pending | - | PR needed |


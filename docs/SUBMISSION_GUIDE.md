# MCP Server Publication Guide

Educational MCP server with 17 tools, persistent workspace, and cloud hosting. Demonstrates FastMCP best practices.

**Links:** [PyPI](https://pypi.org/project/math-mcp-learning-server/) | [GitHub](https://github.com/clouatre-labs/math-mcp-learning-server)

---

## Official MCP Registry

**URL:** <https://registry.modelcontextprotocol.io/>  
**Docs:** <https://github.com/modelcontextprotocol/registry/tree/main/docs>

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

## Smithery

**URL:** <https://smithery.ai/servers/clouatre-labs/math-mcp>  
**Docs:** <https://smithery.ai/docs/build/project-config/smithery-yaml>  
**API:** <https://registry.smithery.ai> (Bearer token auth via `SMITHERY_API_TOKEN`)

### Scoring

Smithery scores servers on a 0-100 scale that directly affects search ranking and discoverability. As of 2026-04-01 we score **98/100**. The two configuration metrics below were worth **25 points combined** and required a one-line file change to unlock.

| Metric | Points | Requirement |
|--------|--------|-------------|
| Config schema | 10 | `configSchema` in `smithery.yaml` has at least one property |
| Optional config | 15 | All properties in `configSchema` are optional (no `required` array) |
| Verified | bonus | Granted by Smithery staff; not self-serve |

Other scored dimensions: server deployed and reachable, tools with descriptions, resources, prompts, custom icon.

### `smithery.yaml`

This file lives in the repository root and is read by Smithery when building/deploying the server. The critical fields are `configSchema` and `commandFunction`.

**`configSchema`** must be a valid JSON Schema object. Properties without a `required` array are all optional, which earns the full 15-point bonus. Each property should have `title`, `description`, and `default` for the UI to render a usable configuration form.

**`commandFunction`** is a JS arrow function (evaluated by Smithery) that maps the config object to a `{ command, args, env }` launch spec. Spread the env vars conditionally so unset properties do not override server defaults:

```yaml
startCommand:
  type: stdio
  configSchema:
    type: object
    properties:
      math_timeout:
        type: number
        title: "Expression Timeout (seconds)"
        description: "Maximum time allowed to evaluate a math expression."
        default: 5.0
        minimum: 0.1
        maximum: 60.0
      mcp_rate_limit_per_minute:
        type: integer
        title: "Rate Limit (requests/minute)"
        description: "Maximum number of tool calls per minute. Set to 0 to disable."
        default: 100
        minimum: 0
  commandFunction: |-
    (config) => ({
      command: "uvx",
      args: ["math-mcp-learning-server"],
      env: {
        ...(config.math_timeout !== undefined && { MATH_TIMEOUT: String(config.math_timeout) }),
        ...(config.mcp_rate_limit_per_minute !== undefined && { MCP_RATE_LIMIT_PER_MINUTE: String(config.mcp_rate_limit_per_minute) }),
      }
    })
```

**Config → env var mapping:** Smithery passes config values as env vars; `pydantic-settings` reads them automatically because `MathMCPSettings` has no `env_prefix`. The env var names must match the field names in `MathMCPSettings` (case-insensitive).

### Checking your score via API

```bash
# List your server (score is null when browsing; non-null only in search results)
curl -s "https://registry.smithery.ai/servers?namespace=clouatre-labs" \
  -H "Authorization: Bearer $SMITHERY_API_TOKEN" | jq '.servers[] | {qualifiedName, score, useCount, verified, isDeployed}'

# Full server detail including connections and tools
curl -s "https://registry.smithery.ai/servers/clouatre-labs/math-mcp" \
  -H "Authorization: Bearer $SMITHERY_API_TOKEN" | jq '{connections, toolCount: (.tools | length)}'

# Recent deployments
curl -s "https://registry.smithery.ai/servers/clouatre-labs%2Fmath-mcp/releases?pageSize=3" \
  -H "Authorization: Bearer $SMITHERY_API_TOKEN" | jq '.releases[] | {id, status, type, upstreamUrl}'
```

Note: the registry API is cached by Cloudflare (TTL ~14 400 s). Score changes from a new release may not be reflected immediately in the API response.

---

## Community Registries

### modelcontextprotocol/servers

**URL:** <https://github.com/modelcontextprotocol/servers>  
**Method:** Pull Request to README

```markdown
- **[Math MCP Learning](https://github.com/clouatre-labs/math-mcp-learning-server)** - Educational MCP with 17 tools, persistent workspace, cloud hosting. Demonstrates FastMCP best practices.
```

### Awesome MCP Servers

**URL:** <https://github.com/mctrinh/awesome-mcp-servers>  
**Method:** Pull Request

### Awesome Remote MCP Servers

**URL:** <https://github.com/sylviangth/awesome-remote-mcp-servers>  
**Method:** Pull Request (cloud-focused)

### FastMCP Showcase

**URL:** <https://github.com/jlowin/fastmcp/blob/main/docs/community/showcase.mdx>  
**Method:** Pull Request to `docs/community/showcase.mdx`

### ToolSDK MCP Registry

**URL:** <https://github.com/toolsdk-ai/toolsdk-mcp-registry>  
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
| Official MCP Registry | ✅ Done | 2025-12-10 | Published v0.9.1 via `mcp-publisher publish` |
| mcp.so | ✅ Done | 2026-03-30 | Auto-crawled; live at mcp.so/server/math-mcp-learning-server |
| AWSome MCP | ✅ Done | 2025-12-10 | Form submitted |
| Smithery | ✅ Done | 2026-03-30 | 98/100 score as of 2026-04-01 |
| Community MCP Servers | ⏳ Pending | - | PR needed |
| Awesome Remote MCP | ⏳ Pending | - | PR needed |
| FastMCP Showcase | ⏳ Pending | - | PR needed |
| ToolSDK Registry | ⏳ Pending | - | Check process |
| Awesome MCP Servers (punkpeye) | ⏳ Pending | - | PR must be opened from browser (GitHub fork permission issue) |

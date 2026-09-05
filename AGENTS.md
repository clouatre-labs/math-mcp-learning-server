# Math MCP Learning Server - Python MCP Server [Production]

Educational MCP server for math operations, visualization, and persistent workspaces.

Restricted `eval()` with character/function whitelist; Pydantic validation on all inputs; KISS.

## Stack

Python 3.14 + FastMCP 3.0 + Pydantic + uv + Ruff + Pyright

## Structure

```text
src/math_mcp/
  server.py          # composition root, middleware, lifespan
  tools/             # calculate, matrix, persistence, visualization
  persistence/       # models, storage, workspace
  resources.py       # MCP resources
  eval.py            # restricted eval (math module + abs only)
  visualization.py   # chart helpers
  settings.py
tests/               # math, matrix, persistence, visualization, HTTP integration
docs/ARCHITECTURE.md # Mermaid diagrams
docs/adr/            # ADRs (NNN-title.md)
```

## Commands

```bash
uv run pytest -v
uv run pyright src/
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Project-Specific Patterns

- All tools use `@mcp.tool()` with comprehensive docstrings and educational metadata
- Optional context in tools: `ctx: SkipValidation[Context | None] = None` -- never required, always guarded with `if ctx:`
- Required context in resources: `ctx: Context` (always called by MCP runtime)
- All ctx usage guarded: `if ctx: await ctx.info(...)`, `if ctx: await ctx.report_progress(...)`
- `eval()` scope is restricted to `math` module and `abs`; no arbitrary code execution

## Runtime Constraints

- Deploys to FastMCP Cloud (Lambda); no module-level process spawning
- `asyncio.to_thread()` for sync offloading; never `ProcessPoolExecutor` or `multiprocessing`

## Docs Conventions

- `ARCHITECTURE.md`: Mermaid only; no `classDef` or `linkStyle`; `TD` for all diagrams; short labels (3-5 words)
- ADRs: lightweight format (Status / Context / Decision / Consequences); ~100 lines max
- No duplication of CONTRIBUTING.md content; link to it instead

## Do not

- Use `eval()` outside `eval.py`
- Add dependencies without justification in the PR description
- Implement features not specified in the assigned issue
- Use `gh release create`; bump `pyproject.toml` version, GPG-sign the tag `v*.*.*`, and push -- the workflow publishes to PyPI and MCP Registry

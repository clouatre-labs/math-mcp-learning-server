# Cloud Deployment Guide

## FastMCP Cloud Deployment

Deploy this server to [FastMCP Cloud](https://fastmcp.cloud) for hosted, production-ready access without local setup.

### Deployment Configuration

This server includes a `fastmcp.json` configuration file for seamless cloud deployment:

```json
{
  "source": {
    "type": "filesystem",
    "path": "src/math_mcp/server.py",
    "entrypoint": "mcp"
  },
  "environment": {
    "type": "uv",
    "python": ">=3.11",
    "dependencies": [
      "fastmcp>=2.0.0",
      "pydantic>=2.11.9",
      "matplotlib>=3.8.0",
      "numpy>=1.26.0"
    ]
  },
  "deployment": {
    "transport": "http",
    "log_level": "INFO"
  }
}
```

### Deploy to FastMCP Cloud

1. **Navigate to**: [FastMCP Cloud Dashboard](https://fastmcp.cloud)
2. **Connect GitHub Repository**: `clouatre-labs/math-mcp-learning-server`
3. **Deploy**: FastMCP Cloud auto-detects `fastmcp.json` configuration
4. **Access via MCP Client**: Connect your MCP client to `https://math-mcp.fastmcp.app/mcp`

### Cloud Storage Considerations

**Persistent Workspace Behavior in Cloud:**
- The persistent workspace (`save_calculation`, `load_variable`) uses ephemeral storage in cloud deployments
- Saved calculations persist during active sessions but reset on container restart
- This is standard cloud/serverless behavior and suitable for educational/demonstration purposes

**For production use cases requiring true persistence:**
- Integrate external storage (S3, database, Redis)
- Use environment variables for cloud credentials
- Modify `src/math_mcp/persistence/storage.py` accordingly

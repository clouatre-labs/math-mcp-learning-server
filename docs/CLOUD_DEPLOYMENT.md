# Cloud Deployment Guide

## Prefect Horizon Deployment

Deploy this server to [Prefect Horizon](https://horizon.prefect.io) for hosted, production-ready access without local setup.

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
    "python": ">=3.14",
    "dependencies": [
      "fastmcp>=3.0.0",
      "pydantic>=2.12.0",
      "pydantic-settings>=2.0.0",
      "matplotlib>=3.10.6",
      "numpy>=2.3.3"
    ]
  },
  "deployment": {
    "transport": "http",
    "log_level": "INFO"
  }
}
```

### Deploy to Prefect Horizon

1. **Navigate to**: [Prefect Horizon Dashboard](https://horizon.prefect.io)
2. **Connect GitHub Repository**: `clouatre-labs/math-mcp-learning-server`
3. **Deploy**: Prefect Horizon auto-detects `fastmcp.json` configuration
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

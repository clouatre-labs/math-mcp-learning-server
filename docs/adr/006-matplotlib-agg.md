# ADR-006: Matplotlib + Agg Backend for Visualization

## Status
Accepted

## Context
The server runs on FastMCP Cloud (AWS Lambda). Lambda provides no display server, no GPU, and
no GUI toolkit. Visualization tools must produce self-contained output that an MCP client can
render without a live connection back to the server.

Alternatives considered:

- **Plotly / Altair**: produce interactive HTML/JavaScript. Requires a browser runtime on the
  client; MCP tools return structured data, not HTML pages. Not suitable.
- **Seaborn**: a Matplotlib wrapper. Adds a dependency without adding capability relevant here.
- **Matplotlib + Agg**: Agg (Anti-Grain Geometry) is a pure-software raster renderer. No display
  server required. Renders to an in-memory PNG buffer; output is base64-encoded and returned as
  a string, a self-contained artifact any MCP client can handle.

## Decision
Use Matplotlib with the Agg backend, explicitly set before any other import:

```python
# visualization.py
import matplotlib

matplotlib.use("Agg")  # Must precede pyplot import; no display server on Lambda
import matplotlib.pyplot as plt
```

Charts are rendered to a `BytesIO` buffer and returned as base64-encoded PNG strings. The client
is responsible for decoding and displaying; the server has no display dependency.

## Consequences

**Gained:**
- Runs headless on Lambda and any serverless runtime with no configuration
- Output is a plain string; no streaming, no file I/O, no client-side JavaScript required
- Matplotlib is the de facto standard for scientific Python visualization; well-documented,
  stable API, no additional dependencies beyond what the project already uses

**Accepted:**
- Static PNG only; no interactivity (zoom, hover, pan)
- Agg must be set before `pyplot` is imported; order-sensitive import is a known footgun,
  mitigated by the explicit comment in `visualization.py`

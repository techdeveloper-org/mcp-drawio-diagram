# mcp-drawio-diagram — Claude Project Context

**Type:** FastMCP Server
**Transport:** stdio
**Python:** 3.8+

---

## What This Server Does

Generate editable .drawio files for all SDLC diagram types. Produces mxGraph XML that opens directly in draw.io/diagrams.net without any API key or Graphviz install. Generates shareable app.diagrams.net URLs and supports GitHub raw URL embedding.

---

## Entry Point

```
server.py
```

Run via `python server.py` — communicates over stdio using the MCP protocol.

---

## Available Tools

- `generate_drawio_diagram` — Generate a .drawio file for a specified diagram type
- `generate_all_drawio` — Generate all SDLC diagram types as .drawio files
- `get_shareable_url` — Generate app.diagrams.net URL for an existing .drawio file
- `list_drawio_diagrams` — List all generated .drawio files with last modified dates
- `convert_mermaid_to_drawio` — Convert Mermaid diagram markup to .drawio format

---

## Shared Utilities (in this repo)

- `base/` — Shared MCP infrastructure package (response builder, decorators, persistence, clients)
- `mcp_errors.py` — Structured error response helpers
- `input_validator.py` — Null-byte strip, length limits, prompt injection detection
- `rate_limiter.py` — Token bucket rate limiter (enable via ENABLE_RATE_LIMITING=1)

## Engine Dependency

Depends on scripts/langgraph_engine/diagrams/ package and call_graph_builder.py from claude-workflow-engine

Set PYTHONPATH to include the workflow engine scripts directory before running:

```bash
export PYTHONPATH=/path/to/claude-workflow-engine/scripts:$PYTHONPATH
```

---

## Environment Variables

- `DRAWIO_OUTPUT_DIR` — Output directory for .drawio files (default: docs/diagrams/)
- `GITHUB_RAW_BASE_URL` — GitHub raw URL base for shareable URL generation

---

## Development

### Running locally

```bash
# Install deps
pip install -r requirements.txt

# Run the MCP server (stdio mode)
python server.py
```

### Testing a tool call manually

```python
import subprocess, json

proc = subprocess.Popen(
    ["python", "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)
# Send MCP initialize + tool call via stdin
```

### File structure

```
mcp-drawio-diagram/
+-- server.py          # Main FastMCP server (entry point)
+-- base/              # Shared base package (response, decorators, persistence, clients)
+-- mcp_errors.py      # Error helpers
+-- input_validator.py # Input validation
+-- rate_limiter.py    # Rate limiting
+-- requirements.txt
+-- .gitignore
+-- README.md
+-- CLAUDE.md
```

---

## Key Rules

1. Do NOT edit `base/` directly — it is a copy from `mcp-base` repo
2. To update shared utilities, edit in `mcp-base` and re-copy
3. Keep `server.py` as the single entry point
4. All tool handlers must use `@mcp_tool_handler` decorator for consistent error handling
5. All responses must use `success()` / `error()` / `MCPResponse` builder from `base.response`

---

**Last Updated:** 2026-03-31

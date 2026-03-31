# mcp-drawio-diagram

A FastMCP server providing **Drawio Diagram** capabilities for Claude Code workflows.

---

## Overview

Generate editable .drawio files for all SDLC diagram types. Produces mxGraph XML that opens directly in draw.io/diagrams.net without any API key or Graphviz install. Generates shareable app.diagrams.net URLs and supports GitHub raw URL embedding.

---

## Tools

| Tool | Description |
|------|-------------|
| `generate_drawio_diagram` | Generate a .drawio file for a specified diagram type |
| `generate_all_drawio` | Generate all SDLC diagram types as .drawio files |
| `get_shareable_url` | Generate app.diagrams.net URL for an existing .drawio file |
| `list_drawio_diagrams` | List all generated .drawio files with last modified dates |
| `convert_mermaid_to_drawio` | Convert Mermaid diagram markup to .drawio format |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/techdeveloper-org/mcp-drawio-diagram.git
cd mcp-drawio-diagram
```

### 2. Install dependencies

```bash
pip install mcp fastmcp
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

---

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DRAWIO_OUTPUT_DIR` | Output directory for .drawio files (default: docs/diagrams/) |
| `GITHUB_RAW_BASE_URL` | GitHub raw URL base for shareable URL generation |

---

## Usage in Claude Code

Add to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "drawio-diagram": {
      "command": "python",
      "args": [
        "/path/to/mcp-drawio-diagram/server.py"
      ],
      "env": {}
    }
  }
}
```

## Engine Dependency

> **Note:** This server depends on `claude-workflow-engine` internals.
>
> Depends on scripts/langgraph_engine/diagrams/ package and call_graph_builder.py from claude-workflow-engine
>
> Ensure `claude-workflow-engine` is cloned alongside this repo and its
> `scripts/` directory is on your `PYTHONPATH`.

```bash
export PYTHONPATH=/path/to/claude-workflow-engine/scripts:$PYTHONPATH
```

---

## Benefits

- Fully editable diagrams — stakeholders can open in draw.io and customize
- No API key needed — mxGraph XML is generated locally
- Shareable URLs work without exporting images (open directly in browser)
- Mermaid conversion bridges LLM-generated diagrams to editable format

---

## Requirements

- Python 3.8+
- `mcp fastmcp`
- See `requirements.txt` for pinned versions

---

## Project Context

This MCP server is part of the **Claude Workflow Engine** ecosystem — a LangGraph-based
orchestration pipeline for automating Claude Code development workflows.

Related repos:
- [`claude-workflow-engine`](https://github.com/techdeveloper-org/claude-workflow-engine) — Main pipeline
- [`mcp-base`](https://github.com/techdeveloper-org/mcp-base) — Shared base utilities used by all MCP servers

---

## License

Private — techdeveloper-org

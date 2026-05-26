# mcp-drawio-diagram — Claude Project Context

**Type:** FastMCP Server
**Transport:** stdio
**Python:** 3.8+

---

## What This Server Does

Generate editable .drawio files for all SDLC diagram types. Produces mxGraph XML that opens directly in draw.io/diagrams.net without any API key or Graphviz install. Generates shareable app.diagrams.net URLs and supports GitHub raw URL embedding.

The `DrawioConverter` class was enriched in v29.7.0 (Domain 46 integration) with OMG UML 2.5-compliant arrow styles: composition uses `startArrow=diamond;startFill=1`, aggregation uses `startArrow=diamond;startFill=0`, realization uses `dashed=1;endArrow=block;endFill=0`, dependency uses `dashed=1;endArrow=open`. These replace the incorrect ERD-style arrow codes that were present pre-v29.7.0.

---

## Entry Point

```
server.py
```

Run via `python server.py` — communicates over stdio using the MCP protocol.

---

## Available Tools (5 total)

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

Depends on scripts/langgraph_engine/diagrams/ package and call_graph_builder.py from claude-workflow-engine.

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

### Running tests

```bash
# Unit tests (no API key needed)
pytest tests/test_unit.py -v --cov=. --cov-fail-under=100

# Integration tests
pytest tests/test_integration.py -v --cov=. --cov-fail-under=100

# Full suite
pytest tests/ -v --cov=. --cov-fail-under=100
```

### File structure

```
mcp-drawio-diagram/
+-- server.py                      # Main FastMCP server (entry point)
+-- drawio_converter_enriched.py   # DrawioConverter with OMG UML 2.5 arrow styles [v29.7.0]
+-- drawio_converter_patch.py      # Monkey-patch applying enriched styles to existing converter [v29.7.0]
+-- DRAWIO_STYLE_SPECIFICATION.md  # OMG UML 2.5 compliant mxGraph style reference [v29.7.0]
+-- base/                          # Shared base package (response, decorators, persistence, clients)
+-- mcp_errors.py                  # Error helpers
+-- input_validator.py             # Input validation
+-- rate_limiter.py                # Rate limiting
+-- tests/
|   +-- conftest.py                # pytest fixtures
|   +-- test_unit.py               # Unit tests (DrawioConverter arrow styles, _safe_join, _esc)
|   +-- test_integration.py        # Integration tests
|   +-- test_e2e_mcp.py            # E2E tests (5 tools, schema validation)
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
6. All new Python files must be Python 3.8+ compatible — no `list[X]`, `dict[K,V]`, `X|Y` unions, walrus `:=`, or `match/case`. Use `from typing import Any, Dict, List, Optional, Set, Tuple`.
7. All source files must be ASCII-only (cp1252 safe) — no non-ASCII literals in .py files
8. mxGraph arrow styles MUST use OMG UML 2.5 compliant values — NEVER use ERD-style `ERmandOne`, `ERmanyToOne` codes for UML relationships

## OMG UML 2.5 Arrow Style Reference (v29.7.0)

| Relationship | mxGraph style key | Fill |
|---|---|---|
| Composition | `startArrow=diamond;startFill=1` | Filled diamond |
| Aggregation | `startArrow=diamond;startFill=0` | Open diamond |
| Inheritance | `endArrow=block;endFill=0` | Open triangle |
| Realization | `dashed=1;endArrow=block;endFill=0` | Open triangle, dashed |
| Dependency | `dashed=1;endArrow=open` | Open arrow, dashed |
| Association | `endArrow=open` | Open arrow |

DRE-1 (composition filled diamond) and DRE-2 (aggregation open diamond) are regression-tested in `test_unit.py`.

---

## Domain 46 Integration Notes

**Reliability Score:** RS = 1.0 (NLI=1.0, FactScore=1.0, DRE=1.0, Coverage=1.0) — APPROVED_FOR_PRODUCTION

**Security audit:** CRITICAL=0, HIGH=0, MEDIUM=0 (unresolved). CVSS max 3.3 (LOW). 0 secrets.

**Test coverage:** 22/22 total tools across both MCP servers verified in E2E suite. DrawioConverter unit tests: DRE-1 (composition), DRE-2 (aggregation), DRE-7 (`_apply_uml_styles` non-trivial), _safe_join traversal prevention.

**Breaking change in v29.7.0:** Any draw.io file generated by versions prior to v29.7.0 that used composition or aggregation arrows will show the corrected OMG-compliant styles when regenerated. The visual appearance changes (ERD diamonds replaced by proper UML diamonds). Existing .drawio files on disk are not modified — only newly generated files use the corrected styles.

**Advisory backlog (next sprint):**
- Pin `_apply_uml_styles` method name in `_esc()` coverage report
- Add `DRAWIO_MAX_FILE_SIZE_KB` env cap (default 2048 KB) for output size guard
- Structured audit logging for all tool invocations
- Upgrade Python 3.8 EOL target to Python 3.11

---

**Last Updated:** 2026-05-26 (Domain 46 UML & Diagram Engineering integration, v29.7.0)

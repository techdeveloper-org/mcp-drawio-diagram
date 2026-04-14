# mcp-drawio-diagram

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Part of claude-workflow-engine](https://img.shields.io/badge/Part%20of-claude--workflow--engine-blueviolet)

Generate fully editable `.drawio` files for all 12 SDLC UML diagram types — no external API, no Graphviz, no rendering service required. Produces pure mxGraph XML that opens directly in draw.io desktop, [app.diagrams.net](https://app.diagrams.net), or VS Code. Also generates shareable `app.diagrams.net` URLs for instant collaboration.

> **How this differs from [mcp-uml-diagram](https://github.com/techdeveloper-org/mcp-uml-diagram):**
> `mcp-drawio-diagram` produces editable `.drawio` XML files that stakeholders can open and modify in draw.io. `mcp-uml-diagram` renders read-only images via Kroki.io using Mermaid/PlantUML syntax. Use this server when you need editable, shareable diagrams; use `mcp-uml-diagram` when you need rendered image output.

---

## Features

- **12 UML diagram types** covering the complete SDLC (class, sequence, activity, state, component, package, deployment, use case, object, communication, composite, interaction)
- **Editable output** — `.drawio` files open directly in draw.io desktop, `app.diagrams.net`, or the VS Code draw.io extension
- **No external API required** — mxGraph XML is generated locally from AST and call graph analysis
- **Shareable URLs** — generates `app.diagrams.net/?url=` links (GitHub-hosted) or encoded `#H` fragment URLs that work immediately without committing
- **AST + CallGraph analysis** — analyzes project source code to generate diagrams with real class names, methods, and relationships
- **Mermaid conversion** — re-generates draw.io equivalents from existing Mermaid `.md` files without re-running the full pipeline
- **Pipeline integration** — used in Step 13 of the claude-workflow-engine SDLC automation pipeline; output goes to the `drawio/` project directory

---

## Tool Reference

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `generate_drawio_diagram` | Generate a single UML diagram as an editable `.drawio` file. Analyzes the project with AST/CallGraph and produces mxGraph XML. | `diagram_type` (required), `project_path` (required), `output_dir` (default: `docs/drawio`), `github_repo`, `github_branch` |
| `generate_all_drawio` | Generate all 12 SDLC diagram types as `.drawio` files in a single call. Analyzes the project once and writes 12 files. | `project_path` (required), `output_dir` (default: `docs/drawio`), `github_repo`, `github_branch` |
| `get_shareable_url` | Get a shareable `app.diagrams.net` URL for an existing `.drawio` file. Returns a GitHub-hosted `?url=` link or an encoded `#H` fragment URL. | `drawio_file_path` (required), `github_repo`, `github_branch`, `project_path` |
| `list_drawio_diagrams` | List all existing `.drawio` files in the output directory with file names, paths, sizes, and last-modified timestamps. | `project_path` (required), `output_dir` (default: `docs/drawio`) |
| `convert_mermaid_to_drawio` | Re-generate `.drawio` files for all existing Mermaid UML `.md` files in the project. Re-analyzes the project rather than parsing Mermaid text. | `project_path` (required), `uml_dir` (default: `docs/uml`), `output_dir` (default: `docs/drawio`), `github_repo`, `github_branch` |

---

## Supported Diagram Types

| Type Key | UML Diagram | SDLC Use |
|----------|-------------|----------|
| `class` | Class diagram | Domain model, object-oriented design |
| `sequence` | Sequence diagram | Request/response flows, API interactions |
| `activity` | Activity diagram | Business process flows, workflows |
| `state` | State machine diagram | Object lifecycle, finite state machines |
| `component` | Component diagram | Module boundaries, service interfaces |
| `package` | Package diagram | Codebase structure, namespace organization |
| `deployment` | Deployment diagram | Infrastructure, containers, environments |
| `usecase` | Use case diagram | User stories, actor-system interactions |
| `object` | Object diagram | Concrete instances at a point in time |
| `communication` | Communication diagram | Object collaborations, message passing |
| `composite` | Composite structure diagram | Internal structure, ports and connectors |
| `interaction` | Interaction overview diagram | High-level flow combining sequence fragments |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/techdeveloper-org/mcp-drawio-diagram.git
cd mcp-drawio-diagram
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `mcp>=1.0.0` — Model Context Protocol runtime
- `fastmcp>=0.1.0` — FastMCP server framework

### 3. Set up the engine dependency

This server analyzes project source code using `langgraph_engine` from the parent `claude-workflow-engine` repository. Ensure that repo is cloned and its `scripts/` directory is on your `PYTHONPATH`:

```bash
git clone https://github.com/techdeveloper-org/claude-workflow-engine.git
export PYTHONPATH=/path/to/claude-workflow-engine/scripts:$PYTHONPATH
```

On Windows (PowerShell):

```powershell
$env:PYTHONPATH = "C:\path\to\claude-workflow-engine\scripts;$env:PYTHONPATH"
```

### 4. Configure in Claude Code

Add the server to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "drawio-diagram": {
      "command": "python",
      "args": [
        "/path/to/mcp-drawio-diagram/server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/claude-workflow-engine/scripts"
      }
    }
  }
}
```

---

## Configuration

| Environment Variable | Default | Description |
|----------------------|---------|-------------|
| `DRAWIO_OUTPUT_DIR` | `drawio/` | Default output directory for generated `.drawio` files when used inside the claude-workflow-engine pipeline (Step 13). Individual tool calls override this with the `output_dir` parameter. |

When running inside the claude-workflow-engine pipeline, set `DRAWIO_OUTPUT_DIR` to point to the project-root `drawio/` directory:

```bash
export DRAWIO_OUTPUT_DIR=/path/to/project/drawio
```

---

## Usage Examples

### Generate a single class diagram

```
Use generate_drawio_diagram to create a class diagram for this project.
diagram_type: class
project_path: /path/to/my-project
output_dir: drawio
github_repo: my-org/my-project
github_branch: main
```

The tool returns:
```json
{
  "diagram_type": "class",
  "format": "drawio",
  "output_file": "/path/to/my-project/drawio/class-diagram.drawio",
  "shareable_url": "https://app.diagrams.net/?url=https://raw.githubusercontent.com/my-org/my-project/main/drawio/class-diagram.drawio",
  "file_size_bytes": 4812,
  "open_hint": "Open in: draw.io desktop, https://app.diagrams.net, or VS Code draw.io extension"
}
```

### Generate all 12 diagram types in one call

```
Use generate_all_drawio to generate all SDLC diagrams.
project_path: /path/to/my-project
output_dir: drawio
github_repo: my-org/my-project
```

The tool analyzes the project once and writes 12 `.drawio` files:
```
drawio/class-diagram.drawio
drawio/sequence-diagram.drawio
drawio/activity-diagram.drawio
drawio/state-diagram.drawio
drawio/component-diagram.drawio
drawio/package-diagram.drawio
drawio/deployment-diagram.drawio
drawio/usecase-diagram.drawio
drawio/object-diagram.drawio
drawio/communication-diagram.drawio
drawio/composite-diagram.drawio
drawio/interaction-diagram.drawio
```

### Get a shareable URL for an existing diagram

```
Use get_shareable_url to get a link I can share with the team.
drawio_file_path: /path/to/my-project/drawio/sequence-diagram.drawio
github_repo: my-org/my-project
project_path: /path/to/my-project
```

Returns a GitHub-hosted URL (`url_type: "github"`) when `github_repo` is provided, or an encoded fragment URL (`url_type: "encoded"`) that works immediately without committing.

### Convert existing Mermaid diagrams to draw.io

```
Use convert_mermaid_to_drawio to convert all existing Mermaid UML files to draw.io format.
project_path: /path/to/my-project
uml_dir: uml
output_dir: drawio
```

Scans `uml/` for `*-diagram.md` files and re-generates `.drawio` equivalents by re-analyzing the project. Useful when you already have Mermaid diagrams from `mcp-uml-diagram` and want editable draw.io versions.

---

## Pipeline Integration

`mcp-drawio-diagram` is used in **Step 13** (Documentation Update + UML Diagram Generation) of the [claude-workflow-engine](https://github.com/techdeveloper-org/claude-workflow-engine) LangGraph pipeline.

```
Step 13: Documentation Update
    |
    |-- mcp-uml-diagram   --> renders Mermaid/PlantUML images via Kroki.io  --> uml/
    |-- mcp-drawio-diagram --> generates editable .drawio XML files          --> drawio/
```

The pipeline sets `DRAWIO_OUTPUT_DIR` to point to the `drawio/` directory at project root (configured via the `UML_OUTPUT_DIR` / `DRAWIO_OUTPUT_DIR` environment variables added in v1.16.1).

Both diagram servers run from the same step and complement each other: `mcp-uml-diagram` for rendered image outputs, `mcp-drawio-diagram` for editable stakeholder-facing diagrams.

---

## Project Context

This server is one of 13 MCP servers in the **Claude Workflow Engine** ecosystem — a LangGraph-based orchestration pipeline for automating Claude Code development workflows across the full SDLC.

| Related Repo | Purpose |
|---|---|
| [claude-workflow-engine](https://github.com/techdeveloper-org/claude-workflow-engine) | Main pipeline — LangGraph orchestration, 8 active steps, call graph intelligence |
| [mcp-base](https://github.com/techdeveloper-org/mcp-base) | Shared base package — `MCPResponse` builder, `@mcp_tool_handler` decorator, `AtomicJsonStore`, `LazyClient` |
| [mcp-uml-diagram](https://github.com/techdeveloper-org/mcp-uml-diagram) | Sibling diagram server — 13 diagram types, Kroki.io rendering, Mermaid/PlantUML, image output |

All 13 MCP servers are registered in `~/.claude/settings.json` and invoked by Claude Code during pipeline execution.

---

## Contributing

1. Fork the repository and create a feature branch.
2. Follow PEP 8 conventions. Use `snake_case` for functions, `PascalCase` for classes.
3. Keep all Python source files ASCII-safe (UTF-8 encoding, no non-ASCII literals).
4. Add tests for any new tools or diagram types.
5. Open a pull request against `main` — the pipeline's Step 11 will run code review automatically.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

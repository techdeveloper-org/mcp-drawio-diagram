# -*- coding: ascii -*-
"""Draw.io Diagram MCP Server - Generate editable .drawio files for all SDLC diagrams.

No external API required. draw.io files are pure XML (mxGraph format).
14 UML diagram types supported (extended from 12 with "timing" and "call_graph_rich").

Tools:
    generate_drawio_diagram    - Single diagram as .drawio file (+3 new params)
    generate_all_drawio        - All 14 diagram types as .drawio files (was 12)
    get_shareable_url          - app.diagrams.net shareable URL for a .drawio file
    list_drawio_diagrams       - List existing .drawio files in output dir
    convert_mermaid_to_drawio  - Convert existing Mermaid .md to .drawio (best-effort)

Python 3.11+. ASCII-only source (cp1252 safe on Windows).
Backward compatibility: generate_drawio_diagram(type, path) is identical to pre-integration.
"""

import datetime as _datetime
import inspect as _inspect
import json as _json
import logging as _logging
import os
import sys
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional

from pydantic import Field

sys.path.insert(0, str(Path(__file__).resolve().parent))

# mcp 2.0 renamed FastMCP to MCPServer and moved it to mcp.server.mcpserver.
# Both names are probed so this server runs under either major version; the
# API used below (tool decorator, run(transport=...)) is identical in both.
try:
    from mcp.server.mcpserver import MCPServer
except ImportError:  # mcp < 2.0
    from mcp.server.fastmcp import FastMCP as MCPServer

try:
    from mcp.types import ToolAnnotations
except ImportError:  # very old SDK without the annotations model
    ToolAnnotations = None

from base.decorators import mcp_tool_handler

mcp = MCPServer(
    "drawio-diagram",
    instructions=(
        "Generate editable draw.io (.drawio) diagrams for all SDLC UML types. "
        "Files can be opened in draw.io desktop, app.diagrams.net, or VS Code. "
        "Produces shareable URLs (app.diagrams.net) for collaboration. "
        "Supports rich style mode with complexity-based color coding (use_rich_styles=True)."
    ),
)

try:
    from skill_context import get_skill_context, get_domain_context
    _SKILL_CONTEXT_AVAILABLE = True
except ImportError:
    _SKILL_CONTEXT_AVAILABLE = False
    _logging.getLogger(__name__).warning(
        "skill_context not importable. Domain 46 enrichment unavailable. "
        "Set GLOBAL_LIBRARY_PATH env var to enable."
    )

try:
    from kg_router import select_diagram_type as _kg_select_diagram_type
    _KG_ROUTER_AVAILABLE = True
except ImportError:
    _KG_ROUTER_AVAILABLE = False

_DRAWIO_MAX_SIZE_BYTES = int(os.environ.get("DRAWIO_MAX_FILE_SIZE_KB", "2048")) * 1024
_DRAWIO_SHARE = os.environ.get("DRAWIO_SHARE", "0") == "1"

_AUDIT_LOG_ENABLED = os.environ.get("ENABLE_AUDIT_LOG", "0") == "1"
_AUDIT_LOGGER = _logging.getLogger("drawio_diagram.audit")
_LOG = _logging.getLogger("drawio_diagram")


def _audit(tool_name, params):
    # type: (str, dict) -> None
    """Log a structured audit entry when ENABLE_AUDIT_LOG=1.

    Emits a single-line JSON record to the drawio_diagram.audit logger at INFO
    level. A serialization failure is downgraded to a warning rather than
    propagating, so audit logging never interrupts tool execution, but it is
    never silently discarded either. Set ENABLE_AUDIT_LOG=1 to activate.

    Args:
        tool_name: MCP tool name being invoked.
        params: Dict of sanitized parameter names and scalar values.
                Must not contain file contents or secrets.
    """
    if not _AUDIT_LOG_ENABLED:
        return
    try:
        _AUDIT_LOGGER.info(_json.dumps({
            "ts": _datetime.datetime.now(_datetime.timezone.utc).isoformat(),
            "tool": tool_name,
            "params": params,
        }))
    except (TypeError, ValueError) as exc:
        _AUDIT_LOGGER.warning(
            "audit record for %s could not be serialized: %s", tool_name, exc
        )


_TOOL_KWARGS = set(_inspect.signature(mcp.tool).parameters)


def _tool(**kwargs):
    """Register an MCP tool, dropping kwargs the installed SDK does not accept.

    ``annotations`` and ``structured_output`` were added to FastMCP at
    different points, so unsupported keywords are filtered rather than raising
    at import time on an older SDK.

    Args:
        **kwargs: Keyword arguments for the underlying ``mcp.tool`` decorator.

    Returns:
        The decorator returned by ``mcp.tool``.
    """
    supported = {key: value for key, value in kwargs.items() if key in _TOOL_KWARGS}
    return mcp.tool(**supported)


def _annotations(title, read_only, destructive, idempotent, open_world=False):
    """Build a ``ToolAnnotations`` object, or None on an SDK without the model.

    An omitted annotation set is read by the specification as the least-safe
    possible declaration, so every tool here declares all four hints.

    Args:
        title: Human-readable tool title.
        read_only: True when the tool performs no writes.
        destructive: True when the tool's effect is irreversible.
        idempotent: True when repeat calls with identical arguments have the
            same cumulative effect as a single call.
        open_world: True when the tool reaches an external or open-ended system.

    Returns:
        A ``ToolAnnotations`` instance, or None when unavailable.
    """
    if ToolAnnotations is None:
        return None
    return ToolAnnotations(
        title=title,
        readOnlyHint=read_only,
        destructiveHint=destructive,
        idempotentHint=idempotent,
        openWorldHint=open_world,
    )


ProjectPath = Annotated[str, Field(
    description="Absolute root path of the project to analyze."
)]
OutputDir = Annotated[str, Field(
    description=(
        "Output directory for the .drawio files, relative to the project root "
        "or absolute. Leave empty to use the DRAWIO_OUTPUT_DIR environment "
        "variable, falling back to '{project_root}/drawio'."
    )
)]
GithubRepo = Annotated[str, Field(
    description="Optional \"owner/repo\" used to build a raw.githubusercontent.com URL for the file. Empty falls back to an inline-encoded app.diagrams.net URL."
)]
GithubBranch = Annotated[str, Field(
    description="Branch name used in the GitHub raw URL. Ignored when github_repo is empty."
)]

DIAGRAM_TYPES_EXTENDED = [
    "class", "sequence", "activity", "state",
    "component", "package", "deployment", "usecase",
    "object", "communication", "composite", "interaction",
    "call_graph",
    "timing",
    "call_graph_rich",
]


def _model_data_field(hint):
    """Build a ModelData Field description carrying a type-specific hint.

    Args:
        hint: Short phrase naming the payload's primary key(s), e.g.
            "\"classes\"" or "\"nodes\"" -- see UDM_PRIMARY_KEY in
            langgraph_engine.diagrams.legacy_generator for the full schema.

    Returns:
        An Annotated[str, Field(...)] type for use as a tool parameter.
    """
    return Annotated[str, Field(
        description=(
            "Optional JSON object of pre-built structural data (UDM v1) to "
            "render from, instead of AST-scanning project_path. Use this when "
            "the authoritative structure lives somewhere other than code -- an "
            "architecture corpus, a spec, or a schema. DrawioConverter is "
            "fully deterministic and dict-driven; no LLM is ever involved "
            "either way. The object must contain a non-empty %s list; a "
            "payload missing it is rejected rather than silently rendered "
            "from placeholder data. Max 512 KB (see UML_MAX_MODEL_DATA_KB)."
            % hint
        )
    )]


_MAX_MODEL_DATA_BYTES = int(os.environ.get("UML_MAX_MODEL_DATA_KB", "512")) * 1024

# diagram_type slug -> UDM primary key, duplicated from
# langgraph_engine.diagrams.legacy_generator.UDM_PRIMARY_KEY so validation
# here does not require importing the engine before _ensure_scripts_path()
# has run. Kept in sync by tests/test_model_data.py in both repos.
_UDM_PRIMARY_KEY = {
    "class": "classes",
    "package": "packages",
    "component": "components",
    "sequence": "call_chains",
    "state": "states",
    "activity": "steps",
    "deployment": "nodes",
    "usecase": "use_cases",
    "object": "objects",
    "communication": "participants",
    "composite": "components",
    "interaction": "steps",
    "call_graph": "methods",
}


def _parse_model_data(raw, diagram_type):
    # type: (str, str) -> tuple
    """Parse and validate a caller-supplied model_data JSON string.

    Args:
        raw: JSON object string, or "" when the parameter was not supplied.
        diagram_type: Diagram type slug, used to check the UDM primary key.
            Types outside _UDM_PRIMARY_KEY (timing, call_graph_rich) skip
            the primary-key check -- DrawioConverter's analysis_data shape
            for those is not yet part of the UDM contract.

    Returns:
        (data, error): (None, None) when raw is empty ("not supplied" -- the
        caller follows the existing AST-derived path); (dict, None) on
        success; (None, str) with a caller-actionable message on failure.
    """
    if raw is None or raw.strip() == "":
        return None, None

    raw_bytes = raw.encode("utf-8")
    if len(raw_bytes) > _MAX_MODEL_DATA_BYTES:
        return None, (
            "model_data exceeds %d KB limit; set UML_MAX_MODEL_DATA_KB to raise it"
            % (_MAX_MODEL_DATA_BYTES // 1024)
        )
    if "\x00" in raw:
        return None, "model_data contains null bytes"

    try:
        data = _json.loads(raw)
    except _json.JSONDecodeError as exc:
        return None, "model_data is not valid JSON: %s at line %d column %d" % (
            exc.msg, exc.lineno, exc.colno,
        )

    if not isinstance(data, dict):
        return None, "model_data must be a JSON object, got %s" % type(data).__name__

    primary_key = _UDM_PRIMARY_KEY.get(diagram_type)
    if primary_key is not None:
        value = data.get(primary_key)
        if not value:
            return None, (
                "model_data for '%s' must contain a non-empty '%s' list"
                % (diagram_type, primary_key)
            )
        if not isinstance(value, list):
            return None, "model_data['%s'] must be a list, got %s" % (
                primary_key, type(value).__name__,
            )

    return data, None

# Canonical output file stems mandated for the standard diagram set.
_CANONICAL_STEMS = {
    "class": "class_diagram",
    "package": "package_diagram",
    "component": "component_diagram",
    "sequence": "sequence_diagram",
    "state": "state_diagram",
    "activity": "activity_diagram",
    "deployment": "deployment_diagram",
    "usecase": "usecase_diagram",
    "object": "object_diagram",
    "composite": "composite_diagram",
    "interaction": "interaction_diagram",
    "communication": "communication_diagram",
    "call_graph": "call_graph_diagram",
}


def _canonical_stem(diagram_type):
    """Map a diagram type slug onto its mandated output file stem.

    Args:
        diagram_type: Diagram type slug such as ``composite`` or ``call_graph``.

    Returns:
        The canonical snake_case stem, e.g. ``composite_diagram``.
    """
    slug = str(diagram_type).strip().lower().replace("-", "_")
    if slug in _CANONICAL_STEMS:
        return _CANONICAL_STEMS[slug]
    if not slug.endswith("_diagram"):
        slug = "%s_diagram" % slug
    return slug


def _engine_root_candidates():
    """Return the candidate directories that may contain ``langgraph_engine``.

    Ordered most-specific first: explicit environment overrides, then the
    sibling claude-workflow-engine checkout (where the package lives at the
    repository root), then its legacy ``scripts/`` location.

    Returns:
        List of Path objects, in probe order.
    """
    here = Path(__file__).resolve().parent
    workspace = here.parent
    candidates = []
    for var in ("CLAUDE_WORKFLOW_ENGINE_PATH", "WORKFLOW_ENGINE_PATH"):
        raw = os.environ.get(var, "").strip()
        if raw:
            candidates.append(Path(raw))
            candidates.append(Path(raw) / "scripts")
    candidates.append(workspace / "claude-workflow-engine")
    candidates.append(workspace / "claude-workflow-engine" / "scripts")
    candidates.append(workspace.parent / "scripts")
    return candidates


def _scripts_dir():
    """Return the resolved claude-workflow-engine root, or the first candidate.

    Returns:
        Path to the directory that contains ``langgraph_engine``, or the first
        probe candidate when none of them does.
    """
    for candidate in _engine_root_candidates():
        if (candidate / "langgraph_engine" / "__init__.py").is_file():
            return candidate
    return _engine_root_candidates()[0]


def _ensure_scripts_path():
    """Put the claude-workflow-engine root on sys.path.

    Only a directory that actually contains ``langgraph_engine/__init__.py`` is
    added, so a stale or renamed checkout produces an explicit failure instead
    of a silently ineffective sys.path entry.

    Returns:
        The Path that was added or already present, or None when no candidate
        contains the package.
    """
    for candidate in _engine_root_candidates():
        if (candidate / "langgraph_engine" / "__init__.py").is_file():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return candidate
    _LOG.warning(
        "langgraph_engine not found in any known location: %s. "
        "Set CLAUDE_WORKFLOW_ENGINE_PATH to the claude-workflow-engine checkout.",
        ", ".join(str(c) for c in _engine_root_candidates()),
    )
    return None


def _get_converter():
    """Lazy import and return a DrawioConverter instance.

    Returns:
        DrawioConverter instance from
        langgraph_engine.diagrams.drawio.drawio_converter_enriched -- the
        3-arg-signature subclass (convert(diagram_type, analysis_data,
        style_config=None)), not the 2-arg base class. mcp-drawio-diagram#4:
        the base class re-exported from langgraph_engine.diagrams
        .drawio_converter raises TypeError against every call site in this
        file, all of which pass (or rely on default handling for) a third
        argument.
    """
    _ensure_scripts_path()
    from langgraph_engine.diagrams.drawio.drawio_converter_enriched import DrawioConverter
    return DrawioConverter()


def _get_ast_analyzer(project_path):
    """Load AST analysis data from the project via UMLAstAnalyzer.

    Args:
        project_path: Root path of the project to analyze.

    Returns:
        Dict of analysis data, or {} on any error.
    """
    _ensure_scripts_path()
    try:
        from langgraph_engine.diagrams.ast_analyzer import UMLAstAnalyzer
        analyzer = UMLAstAnalyzer(project_path)
        return analyzer.analyze()
    except Exception as exc:
        _LOG.warning(
            "AST analysis of %s failed, falling back to call graph: %s: %s",
            project_path, type(exc).__name__, exc,
        )
        return {}


def _get_call_graph_data(project_path):
    """Load call graph data as analysis_data dict via CallGraphBuilder.

    Args:
        project_path: Root path of the project to analyze.

    Returns:
        Dict with "classes" key, or {} on any error.
    """
    _ensure_scripts_path()
    try:
        from langgraph_engine.call_graph_builder import CallGraphBuilder
        builder = CallGraphBuilder(project_path)
        graph = builder.build()
        classes = []
        for fqn, info in list(graph.items())[:60]:
            parts = fqn.split("::")
            if len(parts) == 2:
                file_part, cls_method = parts
                if "." in cls_method:
                    cls_name = cls_method.split(".")[0]
                else:
                    cls_name = Path(file_part).stem
            else:
                cls_name = fqn
            existing = next((c for c in classes if c["name"] == cls_name), None)
            if not existing:
                existing = {"name": cls_name, "methods": [], "attributes": [], "bases": []}
                classes.append(existing)
            method_name = info.get("method", fqn.split(".")[-1] if "." in fqn else fqn)
            existing["methods"].append({"name": method_name, "visibility": "+", "complexity": 0})
        return {"classes": classes}
    except Exception as exc:
        _LOG.warning(
            "call graph build for %s failed: %s: %s",
            project_path, type(exc).__name__, exc,
        )
        return {}


def _resolve_output_dir(project_path, output_dir):
    """Return absolute Path for the draw.io output directory, creating it.

    Precedence is DRAWIO_OUTPUT_DIR, then the caller-supplied directory, then
    the mandated default of ``drawio`` beneath the project root. An empty
    string means "not supplied", which is why the tool defaults are empty
    rather than a hard-coded path.

    Directory creation is deliberately allowed to raise: an unwritable output
    directory is a hard failure that must stop the caller, unlike a single
    diagram that fails to convert.

    Args:
        project_path: Root path of the project.
        output_dir: Caller-supplied directory, or an empty string.

    Returns:
        Resolved absolute Path object (created if not exists).
    """
    env_dir = os.environ.get("DRAWIO_OUTPUT_DIR", "").strip()
    resolved = env_dir or (output_dir or "").strip() or "drawio"
    od = Path(resolved)
    if not od.is_absolute():
        od = Path(project_path) / od
    od.mkdir(parents=True, exist_ok=True)
    return od


def _save_drawio(xml_content, output_path, shareable_url=""):
    """Write XML to a .drawio file using UTF-8 encoding.

    Enforces the DRAWIO_MAX_FILE_SIZE_KB size limit (default 2048 KB) before
    writing. When DRAWIO_SHARE=1 and a shareable_url is provided, prepends an
    XML comment with the URL at the top of the file for quick discovery.
    Raises ValueError if the encoded content exceeds the configured size limit.

    Args:
        xml_content: mxGraph XML string to write.
        output_path: Absolute path for the output file.
        shareable_url: Optional app.diagrams.net URL to embed as XML comment.

    Returns:
        Absolute path string of the written file.

    Raises:
        ValueError: When the encoded XML exceeds _DRAWIO_MAX_SIZE_BYTES.
    """
    if _DRAWIO_SHARE and shareable_url:
        xml_content = "<!-- Shareable URL: %s -->\n%s" % (shareable_url, xml_content)

    encoded = xml_content.encode("utf-8")
    if len(encoded) > _DRAWIO_MAX_SIZE_BYTES:
        raise ValueError(
            "draw.io XML exceeds size limit (%d KB). "
            "Set DRAWIO_MAX_FILE_SIZE_KB env var to increase the limit."
            % (_DRAWIO_MAX_SIZE_BYTES // 1024)
        )

    with open(str(output_path), "w", encoding="utf-8") as f:
        f.write(xml_content)
    return str(output_path)


def _build_rich_style_config(complexity_threshold_low, complexity_threshold_high):
    """Build a style_config dict from RICH_STYLE_CONFIG with threshold overrides.

    Attempts to import RICH_STYLE_CONFIG from drawio_converter_enriched.
    Falls back to a minimal inline config if the module is unavailable.

    Args:
        complexity_threshold_low: Override for complexity_threshold_low in config.
        complexity_threshold_high: Override for complexity_threshold_high in config.

    Returns:
        Dict with style configuration, or None if construction fails.
    """
    try:
        from drawio_converter_enriched import RICH_STYLE_CONFIG
        cfg = dict(RICH_STYLE_CONFIG)
        cfg["complexity_threshold_low"] = complexity_threshold_low
        cfg["complexity_threshold_high"] = complexity_threshold_high
        return cfg
    except ImportError:
        pass

    return {
        "colors": {
            "public":    "#FFFFFF",
            "private":   "#FFE6E6",
            "protected": "#FFFACD",
            "interface": "#DAE8FC",
            "abstract":  "#F8CECC",
            "enum":      "#D5E8D4",
        },
        "complexity_colors": {
            "low":    "#FFFFFF",
            "medium": "#FFF2CC",
            "high":   "#FF0000",
        },
        "complexity_threshold_low":  complexity_threshold_low,
        "complexity_threshold_high": complexity_threshold_high,
        "show_stereotypes":  True,
        "show_cardinality":  True,
        "arrow_style":       "uml",
        "use_swimlanes":     True,
        "max_styled_nodes":  200,
    }


# ======================================================================
# Tool 1: generate_drawio_diagram (MODIFIED -- 3 new params with defaults)
# Backward compat: generate_drawio_diagram(type, path) identical to pre-integration.
# ======================================================================

@_tool(
    annotations=_annotations("Generate one draw.io diagram", False, False, True, False),
    structured_output=False,
)
@mcp_tool_handler
def generate_drawio_diagram(
    diagram_type: Annotated[str, Field(description="Diagram type to generate. One of: class, sequence, activity, state, component, package, deployment, usecase, object, communication, composite, interaction, call_graph, timing, call_graph_rich.")],
    project_path: ProjectPath,
    output_dir: OutputDir = "",
    github_repo: GithubRepo = "",
    github_branch: GithubBranch = "main",
    use_rich_styles: Annotated[bool, Field(description="When true, apply complexity-based colour coding from RICH_STYLE_CONFIG. False reproduces the plain pre-integration styling exactly.")] = False,
    complexity_threshold_low: Annotated[int, Field(description="Methods with cyclomatic complexity below this value are filled white. Only used when use_rich_styles is true.")] = 2,
    complexity_threshold_high: Annotated[int, Field(description="Methods at or above this complexity are filled red. Only used when use_rich_styles is true.")] = 4,
    model_data: _model_data_field("(e.g. \"classes\" for class, \"nodes\" for deployment -- see UDM v1)") = "",
) -> dict:
    """Generate a single UML diagram as an editable .drawio file.

    Analyzes the project with AST/CallGraph and produces a draw.io XML file
    openable in draw.io desktop, app.diagrams.net, or VS Code draw.io extension.

    Extended from pre-integration with optional rich style support and two
    new diagram types. When use_rich_styles=False (default), output is
    byte-identical to pre-integration behavior (backward-compatible guarantee).

    Args:
        diagram_type: One of: class, sequence, activity, state, component,
                      package, deployment, usecase, object, communication,
                      composite, interaction, timing, call_graph_rich.
                      [Extended from 12 to 14 types in Domain 46 integration]
        project_path: Root path of the project to analyze.
        output_dir: Output directory (relative to project root, or absolute).
                    Default: docs/drawio
        github_repo: Optional "owner/repo" for shareable GitHub URL.
                     E.g. "techdeveloper-org/claude-workflow-engine"
        github_branch: Branch for GitHub raw URL. Default: "main"
        use_rich_styles: When True, apply complexity-based color coding via
                         RICH_STYLE_CONFIG. Default False = backward-compatible
                         pre-integration behavior (style_config=None path).
        complexity_threshold_low: Methods with cyclomatic complexity below
                                   this value receive white fill. Default 2.
        complexity_threshold_high: Methods at or above this value receive
                                    red fill. Default 4.
        model_data: Optional UDM JSON payload to render deterministically
                    instead of AST/CallGraph-scanning project_path.

    Returns:
        dict with output_file, shareable_url, diagram_type, file_size_bytes,
        open_hint, rich_styles_applied (bool, additive new key), source
        ("model_data" | "derived", additive new key).
    """
    _audit("generate_drawio_diagram", {
        "diagram_type": diagram_type, "project_path": project_path,
        "output_dir": output_dir, "github_repo": github_repo,
        "use_rich_styles": use_rich_styles,
        "model_data_bytes": len(model_data or ""),
    })
    if diagram_type not in DIAGRAM_TYPES_EXTENDED:
        raise ValueError(
            "Unknown diagram_type: %s (expected one of: %s)"
            % (diagram_type, ", ".join(DIAGRAM_TYPES_EXTENDED))
        )

    data, err = _parse_model_data(model_data, diagram_type)
    if err:
        return {"diagram_type": diagram_type, "format": "drawio", "output_file": "",
                "error": err, "source": "error"}

    _ensure_scripts_path()
    # mcp-drawio-diagram#4: the base DrawioConverter re-exported from
    # drawio_converter is a 2-arg convert(diagram_type, analysis_data); this
    # call site passes a third argument (or relies on the 15-type
    # SUPPORTED_TYPES list), which only the enriched subclass provides.
    from langgraph_engine.diagrams.drawio.drawio_converter_enriched import DrawioConverter
    from langgraph_engine.diagrams.drawio_converter import get_shareable_url

    style_config = None
    if use_rich_styles:
        style_config = _build_rich_style_config(
            complexity_threshold_low, complexity_threshold_high
        )

    if data is not None:
        analysis_data = data
        source = "model_data"
    else:
        analysis_data = _get_ast_analyzer(project_path)
        if not analysis_data.get("classes"):
            analysis_data = _get_call_graph_data(project_path)
        source = "derived"

    converter = DrawioConverter()
    xml = converter.convert(diagram_type, analysis_data, style_config)

    od = _resolve_output_dir(project_path, output_dir)
    filename = "%s.drawio" % _canonical_stem(diagram_type)
    out_path = od / filename

    github_raw_url = ""
    if github_repo:
        rel = str(out_path).replace("\\", "/")
        try:
            rel = str(out_path.relative_to(Path(project_path))).replace("\\", "/")
        except ValueError:
            pass
        github_raw_url = (
            "https://raw.githubusercontent.com/%s/%s/%s"
            % (github_repo, github_branch, rel)
        )

    url = get_shareable_url(xml, github_raw_url or None)
    _save_drawio(xml, out_path, url)

    return {
        "diagram_type": diagram_type,
        "format": "drawio",
        "output_file": str(out_path),
        "shareable_url": url,
        "file_size_bytes": len(xml.encode("utf-8")),
        "open_hint": (
            "Open in: draw.io desktop, https://app.diagrams.net, "
            "or VS Code draw.io extension"
        ),
        "rich_styles_applied": use_rich_styles and style_config is not None,
        "source": source,
    }


# ======================================================================
# Tool 2: generate_all_drawio (MODIFIED -- DIAGRAM_TYPES extended to 14)
# ======================================================================

@_tool(
    annotations=_annotations("Generate all draw.io diagrams", False, False, True, False),
    structured_output=False,
)
@mcp_tool_handler
def generate_all_drawio(
    project_path: ProjectPath,
    output_dir: OutputDir = "",
    github_repo: GithubRepo = "",
    github_branch: GithubBranch = "main",
    model_data: Annotated[str, Field(
        description=(
            "Optional JSON object mapping diagram type slugs to UDM payloads, "
            "e.g. {\"class\": {\"classes\": [...]}, \"deployment\": {\"nodes\": "
            "[...]}}. Slugs present are rendered deterministically from their "
            "payload; slugs absent fall back to the existing AST/CallGraph "
            "derivation, unchanged. A payload missing its type's primary key "
            "is rejected for that type only (reported in model_data_errors). "
            "Valid slugs: class, package, component, sequence, state, "
            "activity, deployment, usecase, object, communication, "
            "composite, interaction, call_graph. Max 512 KB total."
        )
    )] = "",
) -> dict:
    """Generate ALL 14 SDLC UML diagram types as editable .drawio files.

    Analyzes the project once and produces 14 .drawio files covering the
    complete SDLC: class, sequence, activity, state, component, package,
    deployment, use case, object, communication, composite, interaction,
    timing (NEW), call_graph_rich (NEW).

    Extended from 12 to 14 diagram types in Domain 46 integration.
    Existing 12 diagram outputs are byte-identical to pre-integration.

    Args:
        project_path: Root path of the project to analyze.
        output_dir: Output directory. Default: docs/drawio
        github_repo: Optional "owner/repo" for shareable GitHub URLs.
        github_branch: Branch for GitHub raw URL. Default: "main"
        model_data: Optional per-type UDM payload map. See parameter
            description for shape.

    Returns:
        dict with generated list (diagram_type, file, url, source per
        diagram), output_dir, total count, failed list, and
        model_data_errors (additive new key).
    """
    _audit("generate_all_drawio", {
        "project_path": project_path, "output_dir": output_dir,
        "github_repo": github_repo, "model_data_bytes": len(model_data or ""),
    })
    _ensure_scripts_path()
    # mcp-drawio-diagram#4: the base DrawioConverter re-exported from
    # drawio_converter is a 2-arg convert(diagram_type, analysis_data); this
    # call site passes a third argument (or relies on the 15-type
    # SUPPORTED_TYPES list), which only the enriched subclass provides.
    from langgraph_engine.diagrams.drawio.drawio_converter_enriched import DrawioConverter
    from langgraph_engine.diagrams.drawio_converter import get_shareable_url

    model_data_map = {}
    model_data_errors = {}
    if model_data and model_data.strip():
        if len(model_data.encode("utf-8")) > _MAX_MODEL_DATA_BYTES:
            return {
                "output_dir": "", "generated": [], "failed": [],
                "total_generated": 0, "total_failed": 0, "model_data_errors": {},
                "error": "model_data exceeds %d KB limit" % (_MAX_MODEL_DATA_BYTES // 1024),
            }
        try:
            parsed = _json.loads(model_data)
        except _json.JSONDecodeError as exc:
            return {
                "output_dir": "", "generated": [], "failed": [],
                "total_generated": 0, "total_failed": 0, "model_data_errors": {},
                "error": "model_data is not valid JSON: %s" % exc.msg,
            }
        if not isinstance(parsed, dict):
            return {
                "output_dir": "", "generated": [], "failed": [],
                "total_generated": 0, "total_failed": 0, "model_data_errors": {},
                "error": "model_data must be a JSON object mapping diagram type slugs to payloads",
            }
        for slug, payload in parsed.items():
            if slug not in _UDM_PRIMARY_KEY:
                model_data_errors[slug] = "unknown diagram type slug: %s" % slug
                continue
            if not isinstance(payload, dict):
                model_data_errors[slug] = "payload must be a JSON object, got %s" % type(payload).__name__
                continue
            primary_key = _UDM_PRIMARY_KEY[slug]
            if not payload.get(primary_key):
                model_data_errors[slug] = "must contain a non-empty '%s' list" % primary_key
                continue
            model_data_map[slug] = payload

    derived_data = None  # lazily computed only if any type needs it

    converter = DrawioConverter()
    od = _resolve_output_dir(project_path, output_dir)

    generated = []
    failed = []

    for dtype in DIAGRAM_TYPES_EXTENDED:
        try:
            if dtype in model_data_map:
                analysis_data = model_data_map[dtype]
                source = "model_data"
            else:
                if derived_data is None:
                    derived_data = _get_ast_analyzer(project_path)
                    if not derived_data.get("classes"):
                        derived_data = _get_call_graph_data(project_path)
                analysis_data = derived_data
                source = "derived"

            xml = converter.convert(dtype, analysis_data)
            filename = "%s.drawio" % _canonical_stem(dtype)
            out_path = od / filename

            github_raw_url = ""
            if github_repo:
                try:
                    rel = str(out_path.relative_to(Path(project_path))).replace("\\", "/")
                except ValueError:
                    rel = filename
                github_raw_url = (
                    "https://raw.githubusercontent.com/%s/%s/%s"
                    % (github_repo, github_branch, rel)
                )

            url = get_shareable_url(xml, github_raw_url or None)
            _save_drawio(xml, out_path, url)

            generated.append({
                "diagram_type": dtype,
                "output_file": str(out_path),
                "shareable_url": url,
                "file_size_bytes": len(xml.encode("utf-8")),
                "source": source,
            })
        except Exception as e:
            _LOG.error(
                "draw.io generation for type %s failed: %s: %s",
                dtype, type(e).__name__, e,
            )
            failed.append(
                {"diagram_type": dtype, "error": str(e), "error_type": type(e).__name__}
            )

    return {
        "output_dir": str(od),
        "generated": generated,
        "failed": failed,
        "total_generated": len(generated),
        "total_failed": len(failed),
        "model_data_errors": model_data_errors,
        "open_hint": (
            "Open any .drawio file in: draw.io desktop, "
            "https://app.diagrams.net (File > Open from URL / local), "
            "or VS Code with 'Draw.io Integration' extension."
        ),
    }


# ======================================================================
# Tool 3: get_shareable_url -- UNCHANGED
# ======================================================================

@_tool(
    annotations=_annotations("Get shareable draw.io URL", True, False, True, True),
    structured_output=False,
)
@mcp_tool_handler
def get_shareable_url(
    drawio_file_path: Annotated[str, Field(description="Absolute path to an existing .drawio file to build a shareable URL for.")],
    github_repo: GithubRepo = "",
    github_branch: GithubBranch = "main",
    project_path: Annotated[str, Field(description="Project root used to compute the path relative to the repository for the GitHub URL. Empty uses the bare file name.")] = "",
) -> dict:
    """Get a shareable app.diagrams.net URL for an existing .drawio file.

    Two URL modes:
        GitHub URL (recommended): If github_repo is provided and the file
            is committed, returns a ?url= link.
        Encoded URL: Falls back to encoding the XML directly in the URL
            fragment (#H). Works offline but URL is very long.

    Args:
        drawio_file_path: Absolute path to the .drawio file.
        github_repo: "owner/repo" for GitHub-hosted URL. E.g. "org/repo"
        github_branch: Branch name. Default: "main"
        project_path: Project root for computing relative path.

    Returns:
        dict with shareable_url, url_type ("github" or "encoded"), file_path.
    """
    _audit("get_shareable_url", {"drawio_file_path": drawio_file_path, "github_repo": github_repo, "github_branch": github_branch})
    _ensure_scripts_path()
    from langgraph_engine.diagrams.drawio_converter import get_shareable_url as _get_url

    fp = Path(drawio_file_path)
    if not fp.exists():
        return {"error": "File not found: %s" % drawio_file_path}

    with open(str(fp), "r", encoding="utf-8") as f:
        xml = f.read()

    github_raw_url = ""
    url_type = "encoded"

    if github_repo:
        rel = str(fp)
        if project_path:
            try:
                rel = str(fp.relative_to(Path(project_path))).replace("\\", "/")
            except ValueError:
                rel = fp.name
        github_raw_url = (
            "https://raw.githubusercontent.com/%s/%s/%s"
            % (github_repo, github_branch, rel)
        )
        url_type = "github"

    url = _get_url(xml, github_raw_url or None)

    return {
        "shareable_url": url,
        "url_type": url_type,
        "file_path": str(fp),
        "file_size_bytes": len(xml.encode("utf-8")),
        "note": (
            "GitHub URL works best when the file is committed and pushed. "
            "Encoded URL works immediately but is longer."
        ) if url_type == "github" else (
            "Encoded URL works immediately - share with anyone."
        ),
    }


# ======================================================================
# Tool 4: list_drawio_diagrams (MODIFIED -- supported_types extended to 14)
# ======================================================================

@_tool(
    annotations=_annotations("List draw.io diagrams", True, False, True, False),
    structured_output=False,
)
@mcp_tool_handler
def list_drawio_diagrams(
    project_path: ProjectPath,
    output_dir: OutputDir = "",
) -> dict:
    """List all existing .drawio diagram files in the output directory.

    Returns the supported_types list extended to 14 types (was 12) to include
    "timing" and "call_graph_rich" added in Domain 46 integration.

    Args:
        project_path: Root path of the project.
        output_dir: Directory to scan. Default: docs/drawio

    Returns:
        dict with files list (name, path, size_bytes, modified) and total count.
    """
    _audit("list_drawio_diagrams", {"project_path": project_path, "output_dir": output_dir})
    od = _resolve_output_dir(project_path, output_dir)
    files = []

    for f in sorted(od.glob("*.drawio")):
        stat = f.stat()
        files.append({
            "name": f.name,
            "path": str(f),
            "size_bytes": stat.st_size,
            "modified": str(stat.st_mtime),
        })

    return {
        "output_dir": str(od),
        "files": files,
        "total": len(files),
        "supported_types": DIAGRAM_TYPES_EXTENDED,
    }


# ======================================================================
# Tool 5: convert_mermaid_to_drawio -- UNCHANGED
# ======================================================================

@_tool(
    annotations=_annotations("Regenerate draw.io from Mermaid set", False, False, True, False),
    structured_output=False,
)
@mcp_tool_handler
def convert_mermaid_to_drawio(
    project_path: ProjectPath,
    uml_dir: Annotated[str, Field(description="Directory holding the existing Mermaid .md diagrams, relative to the project root or absolute. Leave empty to use UML_OUTPUT_DIR, falling back to '{project_root}/uml'.")] = "",
    output_dir: OutputDir = "",
    github_repo: GithubRepo = "",
    github_branch: GithubBranch = "main",
    model_data: Annotated[str, Field(
        description=(
            "Optional JSON object mapping diagram type slugs to the same UDM "
            "payloads used to generate the Mermaid files in uml_dir, e.g. "
            "{\"class\": {\"classes\": [...]}}. Supplying this is how the two "
            "renderings provably share one source of truth (see "
            "mcp-drawio-diagram#5) -- without it, a type is regenerated from "
            "an AST/CallGraph scan of project_path, which is NOT the same "
            "source as whatever process wrote the Mermaid .md files, and can "
            "disagree with them silently. A slug missing from the map falls "
            "back to that scan for that type only. Max 512 KB total."
        )
    )] = "",
) -> dict:
    """Regenerate .drawio files for the diagram types found in uml_dir's Mermaid set.

    Scans the Mermaid output directory for *_diagram.md files (and legacy
    *-diagram.md files) to discover which diagram TYPES exist, then renders
    a .drawio file for each type. Each file is regenerated independently, so
    one failure is recorded and skipped rather than aborting the run.

    IMPORTANT: the Mermaid file CONTENTS are never read or parsed -- only
    their filenames, to determine which types to (re)generate. Without
    model_data, each type's .drawio is built from a fresh AST/CallGraph scan
    of project_path, which has no guaranteed relationship to whatever
    process produced the Mermaid .md file of the same name (mcp-uml-diagram
    is one such process, but not the only possible one, and may itself have
    been called with its own model_data override -- see mcp-uml-diagram#4).
    Pass model_data with the SAME payload used for the Mermaid generation to
    guarantee the two outputs describe the same structure.
    """
    _audit("convert_mermaid_to_drawio", {
        "project_path": project_path, "uml_dir": uml_dir,
        "output_dir": output_dir, "github_repo": github_repo,
        "model_data_bytes": len(model_data or ""),
    })
    _ensure_scripts_path()
    # mcp-drawio-diagram#4: the base DrawioConverter re-exported from
    # drawio_converter is a 2-arg convert(diagram_type, analysis_data); this
    # call site passes a third argument (or relies on the 15-type
    # SUPPORTED_TYPES list), which only the enriched subclass provides.
    from langgraph_engine.diagrams.drawio.drawio_converter_enriched import DrawioConverter
    from langgraph_engine.diagrams.drawio_converter import get_shareable_url

    MERMAID_TYPE_MAP = {
        "class_diagram":                "class",
        "sequence_diagram":             "sequence",
        "activity_diagram":             "activity",
        "state_diagram":                "state",
        "component_diagram":            "component",
        "package_diagram":              "package",
        "deployment_diagram":           "deployment",
        "usecase_diagram":              "usecase",
        "use_case_diagram":             "usecase",
        "object_diagram":               "object",
        "communication_diagram":        "communication",
        "composite_diagram":            "composite",
        "composite_structure_diagram":  "composite",
        "interaction_diagram":          "interaction",
        "interaction_overview_diagram": "interaction",
        "call_graph_diagram":           "call_graph",
        "timing_diagram":               "timing",
        "uml_from_code_diagram":        "class",
    }

    model_data_map = {}
    model_data_errors = {}
    if model_data and model_data.strip():
        if len(model_data.encode("utf-8")) > _MAX_MODEL_DATA_BYTES:
            return {
                "output_dir": "", "uml_dir": "", "converted": [], "skipped": [],
                "total_converted": 0, "total_skipped": 0, "model_data_errors": {},
                "error": "model_data exceeds %d KB limit" % (_MAX_MODEL_DATA_BYTES // 1024),
            }
        try:
            parsed = _json.loads(model_data)
        except _json.JSONDecodeError as exc:
            return {
                "output_dir": "", "uml_dir": "", "converted": [], "skipped": [],
                "total_converted": 0, "total_skipped": 0, "model_data_errors": {},
                "error": "model_data is not valid JSON: %s" % exc.msg,
            }
        if not isinstance(parsed, dict):
            return {
                "output_dir": "", "uml_dir": "", "converted": [], "skipped": [],
                "total_converted": 0, "total_skipped": 0, "model_data_errors": {},
                "error": "model_data must be a JSON object mapping diagram type slugs to payloads",
            }
        for slug, payload in parsed.items():
            if slug not in _UDM_PRIMARY_KEY:
                model_data_errors[slug] = "unknown diagram type slug: %s" % slug
                continue
            if not isinstance(payload, dict):
                model_data_errors[slug] = "payload must be a JSON object, got %s" % type(payload).__name__
                continue
            primary_key = _UDM_PRIMARY_KEY[slug]
            if not payload.get(primary_key):
                model_data_errors[slug] = "must contain a non-empty '%s' list" % primary_key
                continue
            model_data_map[slug] = payload

    resolved_uml_dir = (
        os.environ.get("UML_OUTPUT_DIR", "").strip()
        or (uml_dir or "").strip()
        or "uml"
    )
    uml_path = (
        Path(project_path) / resolved_uml_dir
        if not Path(resolved_uml_dir).is_absolute()
        else Path(resolved_uml_dir)
    )
    derived_data = None  # lazily computed only if some type needs it

    converter = DrawioConverter()
    od = _resolve_output_dir(project_path, output_dir)

    converted = []
    skipped = []

    md_files = sorted(
        set(uml_path.glob("*_diagram.md")) | set(uml_path.glob("*-diagram.md"))
    )

    for md_file in md_files:
        stem = md_file.stem.replace("-", "_")
        dtype = MERMAID_TYPE_MAP.get(stem)
        if not dtype:
            skipped.append({"file": str(md_file), "reason": "unknown type"})
            continue

        try:
            if dtype in model_data_map:
                analysis_data = model_data_map[dtype]
                source = "model_data"
            else:
                if derived_data is None:
                    derived_data = _get_ast_analyzer(project_path)
                    if not derived_data.get("classes"):
                        derived_data = _get_call_graph_data(project_path)
                analysis_data = derived_data
                source = "derived"

            xml = converter.convert(dtype, analysis_data)
            out_filename = "%s.drawio" % _canonical_stem(dtype)
            out_path = od / out_filename

            github_raw_url = ""
            if github_repo:
                try:
                    rel = str(out_path.relative_to(Path(project_path))).replace("\\", "/")
                except ValueError:
                    rel = out_filename
                github_raw_url = (
                    "https://raw.githubusercontent.com/%s/%s/%s"
                    % (github_repo, github_branch, rel)
                )

            url = get_shareable_url(xml, github_raw_url or None)
            _save_drawio(xml, out_path, url)
            converted.append({
                "source_md": str(md_file),
                "output_drawio": str(out_path),
                "diagram_type": dtype,
                "shareable_url": url,
                "source": source,
            })
        except Exception as e:
            _LOG.error(
                "converting %s failed: %s: %s", md_file, type(e).__name__, e
            )
            skipped.append(
                {"file": str(md_file), "reason": str(e), "error_type": type(e).__name__}
            )

    return {
        "output_dir": str(od),
        "uml_dir": str(uml_path),
        "converted": converted,
        "skipped": skipped,
        "total_converted": len(converted),
        "total_skipped": len(skipped),
        "model_data_errors": model_data_errors,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")

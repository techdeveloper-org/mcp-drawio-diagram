# -*- coding: ascii -*-
"""drawio_converter_enriched.py - Root-level shim for mcp-drawio-diagram.

Re-exports DrawioConverter, RICH_STYLE_CONFIG, DEFAULT_STYLE_CONFIG,
UML_CLASS_STYLES, and UML_ARROW_STYLES from the actual implementation in
langgraph_engine/diagrams/drawio/drawio_converter_enriched.py.

Allows server.py to import RICH_STYLE_CONFIG without needing to know the
full package path. Falls back gracefully if the scripts path is not yet
on sys.path at import time.

Python 3.11+. ASCII-only source (cp1252 safe on Windows).
"""

import sys
from pathlib import Path

_scripts_dir = str(
    Path(__file__).resolve().parent.parent.parent / "claude-workflow-engine"
)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

try:
    from langgraph_engine.diagrams.drawio.drawio_converter_enriched import (  # noqa: F401
        DrawioConverter,
        RICH_STYLE_CONFIG,
        DEFAULT_STYLE_CONFIG,
        UML_CLASS_STYLES,
        UML_ARROW_STYLES,
    )
except ImportError as _e:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "drawio_converter_enriched: could not import from langgraph_engine: %s", _e
    )

    from typing import Any, Dict

    RICH_STYLE_CONFIG = {
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
        "complexity_threshold_low":  2,
        "complexity_threshold_high": 4,
        "show_stereotypes":  True,
        "show_cardinality":  True,
        "arrow_style":       "uml",
        "use_swimlanes":     True,
        "max_styled_nodes":  200,
    }  # type: Dict[str, Any]

    DEFAULT_STYLE_CONFIG = dict(RICH_STYLE_CONFIG)
    UML_CLASS_STYLES = {}  # type: Dict[str, str]
    UML_ARROW_STYLES = {}  # type: Dict[str, str]

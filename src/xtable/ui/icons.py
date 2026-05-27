from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QByteArray
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


ICON_RESOURCE_DIR = Path(__file__).resolve().parent / "resources" / "icons"
ICON_IDS = {
    "project-new",
    "project-open",
    "project-save",
    "import",
    "export",
    "validate",
    "undo",
    "redo",
    "theme",
    "issues",
    "logs",
    "diagnostics",
    "table",
    "enum",
    "meta",
    "ok",
    "warn",
    "error",
    "info",
}

THEME_ICON_COLORS = {
    "light": {
        "normal": "#344054",
        "accent": "#0f766e",
        "warn": "#b45309",
        "error": "#b42318",
        "success": "#047857",
        "info": "#2563eb",
    },
    "dark": {
        "normal": "#e7edf3",
        "accent": "#2dd4bf",
        "warn": "#fbbf24",
        "error": "#f97066",
        "success": "#34d399",
        "info": "#60a5fa",
    },
}

ICON_SVG = {
    "project-new": '<path d="M5 4h8l4 4v12H5z"/><path d="M13 4v5h5"/><path d="M9 14h6M12 11v6"/>',
    "project-open": '<path d="M3 8h7l2 3h9l-2 8H5z"/><path d="M3 8V5h7l2 3"/>',
    "project-save": '<path d="M5 4h12l2 2v14H5z"/><path d="M8 4v6h8V4"/><path d="M8 16h8v4H8z"/>',
    "import": '<path d="M12 4v11"/><path d="M8 11l4 4 4-4"/><path d="M5 20h14"/>',
    "export": '<path d="M12 16V5"/><path d="M8 9l4-4 4 4"/><path d="M5 20h14"/>',
    "validate": '<path d="M5 12l4 4L19 6"/><path d="M4 20h16"/>',
    "undo": '<path d="M19 12H5"/><path d="M9 8l-4 4 4 4"/>',
    "redo": '<path d="M5 12h14"/><path d="M15 8l4 4-4 4"/>',
    "theme": '<path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z"/>',
    "issues": '<path d="M12 4l9 16H3z"/><path d="M12 9v5"/><path d="M12 17h.01"/>',
    "logs": '<path d="M6 4h12v16H6z"/><path d="M9 8h6M9 12h6M9 16h4"/>',
    "diagnostics": '<path d="M5 5h14v10H5z"/><path d="M8 19h8"/><path d="M12 15v4"/>',
    "table": '<path d="M4 5h16v14H4z"/><path d="M4 10h16M4 15h16M9 5v14M15 5v14"/>',
    "enum": '<path d="M7 7h13M7 12h13M7 17h13"/><path d="M4 7h.01M4 12h.01M4 17h.01"/>',
    "meta": '<path d="M6 6h5v5H6zM13 13h5v5h-5z"/><path d="M11 8h3v7h-3"/>',
    "ok": '<path d="M5 12l4 4L19 6"/>',
    "warn": '<path d="M12 4l9 16H3z"/><path d="M12 9v5"/><path d="M12 17h.01"/>',
    "error": '<path d="M6 6l12 12M18 6L6 18"/>',
    "info": '<path d="M12 17v-6"/><path d="M12 7h.01"/><circle cx="12" cy="12" r="9"/>',
}

ICON_TONES = {
    "warn": "warn",
    "error": "error",
    "ok": "success",
    "info": "info",
    "issues": "warn",
}


def icon_for(icon_id: str, theme: str = "light", state: str = "normal") -> QIcon:
    if icon_id not in ICON_IDS:
        raise KeyError(f"Unknown icon id: {icon_id}")
    return _icon_for(icon_id, theme, state)


def icon_source_path(icon_id: str) -> Path:
    if icon_id not in ICON_IDS:
        raise KeyError(f"Unknown icon id: {icon_id}")
    return ICON_RESOURCE_DIR / f"{icon_id}.svg"


@lru_cache(maxsize=256)
def _icon_for(icon_id: str, theme: str, state: str) -> QIcon:
    tone = ICON_TONES.get(icon_id, state)
    color = THEME_ICON_COLORS[theme].get(tone, THEME_ICON_COLORS[theme]["normal"])
    svg = _load_svg_template(icon_id).replace("{color}", color)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(24, 24)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def _load_svg_template(icon_id: str) -> str:
    source_path = icon_source_path(icon_id)
    if source_path.exists():
        return source_path.read_text(encoding="utf-8")
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
      viewBox="0 0 24 24" fill="none" stroke="{{color}}" stroke-width="1.8"
      stroke-linecap="round" stroke-linejoin="round">
      {ICON_SVG[icon_id]}
    </svg>
    """

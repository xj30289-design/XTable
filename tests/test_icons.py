from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from xtable.ui.icons import ICON_IDS, ICON_RESOURCE_DIR, icon_for, icon_source_path


def test_project_icon_registry_covers_core_actions_and_navigation():
    expected = {
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

    assert expected <= ICON_IDS


def test_project_icons_have_managed_svg_resource_files():
    assert ICON_RESOURCE_DIR.exists()

    for icon_id in ICON_IDS:
        source_path = icon_source_path(icon_id)
        assert source_path.is_file()
        assert source_path.parent == ICON_RESOURCE_DIR
        assert "<svg" in source_path.read_text(encoding="utf-8")


def test_icons_are_theme_tinted_and_have_readable_pixmaps():
    app = QApplication.instance() or QApplication([])

    light = icon_for("project-save", "light").pixmap(QSize(20, 20)).toImage()
    dark = icon_for("project-save", "dark").pixmap(QSize(20, 20)).toImage()

    assert not light.isNull()
    assert not dark.isNull()
    assert light != dark

    app.quit()


def test_undo_redo_icons_use_flat_left_right_arrows():
    undo_svg = icon_source_path("undo").read_text(encoding="utf-8")
    redo_svg = icon_source_path("redo").read_text(encoding="utf-8")

    assert 'd="M19 12H5"' in undo_svg
    assert 'd="M9 8l-4 4 4 4"' in undo_svg
    assert 'd="M5 12h14"' in redo_svg
    assert 'd="M15 8l4 4-4 4"' in redo_svg
    assert "c3-5" not in undo_svg
    assert "c-3-5" not in redo_svg

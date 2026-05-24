from __future__ import annotations

from pathlib import Path


def test_non_ui_modules_do_not_import_pyside6():
    guarded_roots = [
        Path("src/xtable/application"),
        Path("src/xtable/domain"),
        Path("src/xtable/io"),
        Path("src/xtable/validation"),
    ]

    for root in guarded_roots:
        for source_path in root.rglob("*.py"):
            source = source_path.read_text(encoding="utf-8")
            assert "PySide6" not in source, source_path


def test_ui_requirements_are_documented_as_ui_first():
    guidelines = Path("docs/ui-implementation-guidelines.md").read_text(encoding="utf-8")

    assert "新 UI 需求必须先进入 `xtable.ui`" in guidelines
    assert "业务模块直接创建" in guidelines


def test_app_layer_does_not_create_high_risk_qt_widgets_directly():
    blocked = (
        "QMessageBox",
        "QDialog(",
        "QDialogButtonBox",
        "QTableWidget(",
        "QTabWidget(",
        "QSplitter(",
    )

    for source_path in Path("src/xtable/app").rglob("*.py"):
        source = source_path.read_text(encoding="utf-8")
        for pattern in blocked:
            assert pattern not in source, f"{source_path} directly uses {pattern}"


def test_demo_uses_icon_buttons_for_non_confirmation_actions():
    source = Path("src/xtable/ui/demo.py").read_text(encoding="utf-8")

    assert "QPushButton(" not in source
    assert "IconToolButton" in source


def test_ui_font_strategy_is_documented_and_configured():
    demo_source = Path("src/xtable/ui/demo.py").read_text(encoding="utf-8")
    guidelines = Path("docs/ui-implementation-guidelines.md").read_text(encoding="utf-8")

    assert "configure_ui_font" in demo_source
    assert "addApplicationFont" in demo_source
    assert "中文字体" in guidelines

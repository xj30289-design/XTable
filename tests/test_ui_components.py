from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QLineEdit,
    QTableWidget,
    QTextEdit,
    QToolBar,
    QToolButton,
)

from xtable.ui.components import (
    EditorToolbar,
    FieldInspector,
    IconToolButton,
    JsonEditorShell,
    ListEditorShell,
    MetaEditorShell,
    PickerShell,
    NavigationRail,
    PreviewTable,
)
from xtable.ui.theme import build_stylesheet


def test_icon_tool_button_uses_icon_id_tooltip_and_theme():
    app = QApplication.instance() or QApplication([])

    button = IconToolButton("project-save", "保存项目", theme="dark")

    assert isinstance(button, QToolButton)
    assert button.objectName() == "icon-tool-button-project-save"
    assert button.property("icon-id") == "project-save"
    assert button.toolTip() == "保存项目"
    assert button.accessibleName() == "保存项目"
    assert button.text() == ""
    assert button.iconSize() == QSize(20, 20)
    assert not button.icon().isNull()

    button.apply_theme("light")

    assert button.property("theme") == "light"
    assert not button.icon().isNull()

    button.close()
    app.quit()


def test_navigation_rail_exposes_semantic_items_and_selection():
    app = QApplication.instance() or QApplication([])

    selected: list[str] = []
    rail = NavigationRail(
        [
            ("table", "Table", "table"),
            ("enum", "Enum", "enum"),
            ("meta", "Meta", "meta"),
        ],
        on_select=selected.append,
        theme="dark",
    )

    assert isinstance(rail, QFrame)
    assert rail.objectName() == "navigation-rail"
    assert rail.button_for("table").property("icon-id") == "table"
    assert rail.button_for("table").isChecked()

    rail.select("meta")

    assert rail.button_for("meta").isChecked()
    assert not rail.button_for("table").isChecked()
    assert selected[-1] == "meta"

    rail.close()
    app.quit()


def test_editor_toolbar_groups_actions_and_keeps_global_actions_right_aligned():
    app = QApplication.instance() or QApplication([])

    action = QAction("保存")
    action.setObjectName("action-save-project")
    action.setProperty("icon-id", "project-save")
    action.setToolTip("保存项目")
    theme_action = QAction("切换主题")
    theme_action.setObjectName("action-toggle-theme")
    theme_action.setProperty("icon-id", "theme")
    theme_action.setToolTip("切换主题")

    toolbar = EditorToolbar(
        [("project", [action]), ("global", [theme_action])],
        theme="dark",
    )

    assert isinstance(toolbar, QToolBar)
    assert toolbar.objectName() == "editor-toolbar"
    assert toolbar.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert toolbar.findChild(object, "toolbar-right-spacer") is not None
    assert not action.icon().isNull()
    assert not theme_action.icon().isNull()

    toolbar.close()
    app.quit()


def test_preview_table_shows_static_states_and_semantic_cells():
    app = QApplication.instance() or QApplication([])

    table = PreviewTable(theme="dark")

    assert isinstance(table, QTableWidget)
    assert table.objectName() == "preview-table"
    assert table.rowCount() >= 4
    assert table.columnCount() >= 4
    assert table.item(1, 2).data(Qt.ItemDataRole.UserRole) == "readonly"
    assert table.item(2, 3).data(Qt.ItemDataRole.UserRole) == "error"
    assert table.item(3, 3).data(Qt.ItemDataRole.UserRole) == "warning"

    table.close()
    app.quit()


def test_field_inspector_exposes_expected_inputs_without_business_binding():
    app = QApplication.instance() or QApplication([])

    inspector = FieldInspector(theme="dark")

    assert inspector.objectName() == "field-inspector"
    assert inspector.findChild(QLineEdit, "field-name-input").text() == "item_id"
    assert inspector.findChild(QComboBox, "field-type-input").currentText() == "Int"
    assert inspector.findChild(QCheckBox, "field-required-input").isChecked()
    assert inspector.findChild(QTextEdit, "field-description-input").toPlainText()

    inspector.set_field_state("disabled")

    assert inspector.property("field-state") == "disabled"
    assert not inspector.findChild(QLineEdit, "field-name-input").isEnabled()

    inspector.close()
    app.quit()


def test_field_editor_shells_cover_enum_reference_json_list_and_meta_states():
    app = QApplication.instance() or QApplication([])

    enum_picker = PickerShell("enum", "品质枚举", ["Common", "Rare", "Epic"], state="normal")
    reference_picker = PickerShell("reference", "引用表", ["items.item_id", "skills.skill_id"], state="readonly")
    json_editor = JsonEditorShell(state="invalid")
    list_editor = ListEditorShell(state="empty")
    meta_editor = MetaEditorShell(state="disabled")

    assert enum_picker.objectName() == "enum-picker-shell"
    assert enum_picker.property("field-state") == "normal"
    assert reference_picker.objectName() == "reference-picker-shell"
    assert reference_picker.property("field-state") == "readonly"
    assert json_editor.objectName() == "json-editor-shell"
    assert json_editor.property("field-state") == "invalid"
    assert list_editor.objectName() == "list-editor-shell"
    assert list_editor.property("field-state") == "empty"
    assert meta_editor.objectName() == "meta-editor-shell"
    assert meta_editor.property("field-state") == "disabled"

    for widget in (enum_picker, reference_picker, json_editor, list_editor, meta_editor):
        widget.close()
    app.quit()


def test_theme_covers_phase15_table_and_form_components():
    stylesheet = build_stylesheet("dark")

    for selector in (
        "QTableWidget#preview-table",
        "QFrame#field-inspector",
        "QComboBox",
        "QCheckBox",
        "QTextEdit",
        "QFrame#field-editor-shell",
        "QFrame[field-state=\"invalid\"]",
        "QFrame[field-state=\"disabled\"]",
        "table_error_bg",
        "table_warning_bg",
    ):
        assert selector in stylesheet

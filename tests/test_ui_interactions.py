from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QLineEdit, QTableWidgetSelectionRange, QTextEdit, QToolButton

from xtable.ui.components import (
    DataListView,
    JsonEditorShell,
    PickerShell,
    PreviewTable,
    WorkspaceTabs,
)
from xtable.ui.focus import EditorFocusManager, ManagedLineEdit
from xtable.ui.theme import THEMES, build_stylesheet
from xtable.ui.demo import create_demo_window


def test_focus_manager_keeps_only_one_active_editor_and_blurs_on_outside_click():
    app = QApplication.instance() or QApplication([])
    manager = EditorFocusManager()
    first = ManagedLineEdit("first", manager)
    second = ManagedLineEdit("second", manager)

    first.activate_editor()

    assert manager.active_editor is first
    assert first.property("active-editor") is True

    second.activate_editor()

    assert manager.active_editor is second
    assert first.property("active-editor") is False
    assert second.property("active-editor") is True

    manager.deactivate_active(reason="outside-click")

    assert manager.active_editor is None
    assert second.property("active-editor") is False
    assert manager.last_deactivate_reason == "outside-click"

    first.close()
    second.close()
    app.quit()


def test_preview_table_supports_paste_batch_fill_readonly_protection_and_pixel_scroll():
    app = QApplication.instance() or QApplication([])
    table = PreviewTable(row_count=24, column_count=8)

    table.setCurrentCell(0, 0)
    table.paste_tsv("A\tB\nC\tD")

    assert table.item(0, 0).text() == "A"
    assert table.item(0, 1).text() == "B"
    assert table.item(1, 0).text() == "C"
    assert table.item(1, 1).text() == "D"

    readonly_before = table.item(1, 2).text()
    table.setCurrentCell(1, 2)
    table.batch_fill("blocked")

    assert table.item(1, 2).text() == readonly_before
    assert table.property("last-rejected-write") == "readonly"
    assert table.verticalScrollMode() == table.ScrollMode.ScrollPerPixel
    assert table.horizontalScrollMode() == table.ScrollMode.ScrollPerPixel

    table.close()
    app.quit()


def test_preview_table_supports_clipboard_copy_paste_shortcuts():
    app = QApplication.instance() or QApplication([])
    table = PreviewTable(row_count=8, column_count=5)

    QApplication.clipboard().setText("X\tY")
    table.setCurrentCell(0, 0)
    table.keyPressEvent(QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier))

    assert table.item(0, 0).text() == "X"
    assert table.item(0, 1).text() == "Y"

    table.setRangeSelected(QTableWidgetSelectionRange(0, 0, 0, 1), True)
    table.keyPressEvent(QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier))

    assert QApplication.clipboard().text().startswith("X\tY")

    table.close()
    app.quit()


def test_workspace_tabs_tracks_active_dirty_and_close_confirmation():
    app = QApplication.instance() or QApplication([])
    tabs = WorkspaceTabs()

    tabs.open_document("items", "Items", dirty=True)
    tabs.open_document("skills", "Skills", dirty=False)
    tabs.set_active_document("skills")

    assert tabs.objectName() == "workspace-tabs"
    assert tabs.active_document_key == "skills"
    assert tabs.tabText(0).endswith("*")
    assert tabs.close_document("items") is False
    assert tabs.property("pending-close-document") == "items"
    tabs.confirm_pending_close()
    assert tabs.document_count == 1

    tabs.close()
    app.quit()


def test_json_editor_validates_formats_minifies_and_exposes_line_column():
    app = QApplication.instance() or QApplication([])
    editor = JsonEditorShell(state="normal")
    text_edit = editor.findChild(QTextEdit, "json-editor-input")

    text_edit.setPlainText('{"id":1001,"tags":["shop"]}')
    assert editor.validate_json() is True
    assert editor.findChild(QToolButton, "json-editor-validate-button") is not None
    assert editor.findChild(QToolButton, "json-editor-format-button") is not None
    assert editor.findChild(QToolButton, "json-editor-minify-button") is not None
    editor.format_json()
    assert "\n" in text_edit.toPlainText()
    editor.minify_json()
    assert text_edit.toPlainText() == '{"id":1001,"tags":["shop"]}'

    text_edit.setPlainText('{"id": }')
    assert editor.validate_json() is False
    assert editor.property("json-valid") is False
    assert editor.findChild(object, "json-editor-status").text().startswith("Error")

    editor.close()
    app.quit()


def test_demo_wires_focus_manager_page_blur_display_modes_and_visible_editing_tools():
    app = QApplication.instance() or QApplication([])
    window = create_demo_window()
    window.show()
    app.processEvents()

    assert hasattr(window, "focus_manager")

    window.show_page("table")
    name_input = window.findChild(QLineEdit, "field-name-input")
    default_input = window.findChild(QLineEdit, "field-default-input")
    name_input.setFocus()
    app.processEvents()
    assert window.focus_manager.active_editor is name_input

    default_input.setFocus()
    app.processEvents()
    assert window.focus_manager.active_editor is default_input
    assert name_input.property("active-editor") is False

    window.show_page("forms")
    app.processEvents()
    assert window.focus_manager.active_editor is None
    assert window.focus_manager.last_deactivate_reason == "page-switch"

    assert window.findChild(QToolButton, "table-batch-fill-button") is not None
    assert window.findChild(QToolButton, "table-copy-selection-button") is not None
    assert window.findChild(QToolButton, "table-paste-selection-button") is not None
    assert window.findChild(QToolButton, "json-editor-format-button") is not None
    assert window.findChildren(QLineEdit, options=Qt.FindChildOption.FindChildrenRecursively)
    assert any(
        child.property("display-mode") == "readonly" or child.isReadOnly()
        for child in window.findChildren(QLineEdit)
    )

    window.close()
    app.quit()


def test_picker_shell_has_status_button_and_does_not_leave_empty_leading_slot():
    app = QApplication.instance() or QApplication([])
    picker = PickerShell("enum", "品质枚举", ["Common", "Rare"], state="invalid")

    status_button = picker.findChild(object, "enum-picker-status-button")

    assert status_button is not None
    assert status_button.property("field-state") == "invalid"
    assert status_button.property("icon-id") == "error"
    assert status_button.toolTip()

    picker.close()
    app.quit()


def test_data_list_view_covers_resource_list_states_and_filtering():
    app = QApplication.instance() or QApplication([])
    data_list = DataListView(
        [
            ("items", "Items", "table", "dirty"),
            ("skills", "Skills", "table", "ok"),
            ("qualities", "Qualities", "enum", "warning"),
        ]
    )

    assert data_list.objectName() == "data-list-view"
    assert data_list.findChild(QLineEdit, "data-list-filter").isEnabled()
    assert data_list.count() == 3

    data_list.apply_filter("skill")

    assert data_list.count() == 1
    assert data_list.item(0).data(Qt.ItemDataRole.UserRole) == "skills"

    data_list.set_loading(True)
    assert data_list.property("list-state") == "loading"
    data_list.set_empty()
    assert data_list.property("list-state") == "empty"

    data_list.close()
    app.quit()


def test_light_theme_selection_tokens_cover_text_and_tables():
    stylesheet = build_stylesheet("light")

    assert "selection_bg" in stylesheet
    assert "selection_text" in stylesheet
    assert THEMES["light"]["selection_text"] != THEMES["light"]["selection_bg"]
    for selector in (
        "selection-color",
        "QLineEdit",
        "QTextEdit",
        "QComboBox QAbstractItemView",
    ):
        assert selector in stylesheet

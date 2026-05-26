from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QTableView, QTableWidgetSelectionRange, QTextEdit, QToolButton

from xtable.domain.models import FieldDefinition, FieldType, NormalTableDefinition, TableRow
from xtable.ui.components import (
    DataListView,
    JsonEditorShell,
    PickerShell,
    PreviewTable,
    TableWorkbench,
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


def test_table_workbench_filters_rows_and_finds_matching_cells():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")
    filter_input = workbench.findChild(QLineEdit, "table-workbench-filter-input")
    search_input = workbench.findChild(QLineEdit, "table-workbench-search-input")

    assert filter_input is not None
    assert search_input is not None

    filter_input.setText("ether")

    assert view.isRowHidden(0) is True
    assert view.isRowHidden(1) is True
    assert view.isRowHidden(2) is False

    workbench.clear_filter()

    assert all(not view.isRowHidden(row) for row in range(workbench.model.rowCount()))

    search_input.setText("elixir")

    assert workbench.find_next_match() is True
    assert view.currentIndex().row() == 1
    assert view.currentIndex().column() == 1

    workbench.close()
    app.quit()


def test_table_workbench_replaces_matching_cells_from_visible_controls():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    search_input = workbench.findChild(QLineEdit, "table-workbench-search-input")
    replace_input = workbench.findChild(QLineEdit, "table-workbench-replace-input")
    replace_button = workbench.findChild(QToolButton, "table-workbench-replace-button")

    assert replace_input is not None
    assert replace_button is not None

    search_input.setText("Potion")
    replace_input.setText("Hi-Potion")

    assert workbench.replace_all_matches() == ((0, 1),)
    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Hi-Potion"
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"

    workbench.close()
    app.quit()


def test_table_workbench_sorts_rows_by_current_column():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")
    sort_asc_button = workbench.findChild(QToolButton, "table-workbench-sort-asc-button")
    sort_desc_button = workbench.findChild(QToolButton, "table-workbench-sort-desc-button")

    assert sort_asc_button is not None
    assert sort_desc_button is not None

    view.setCurrentIndex(workbench.model.index(0, 2))

    assert workbench.sort_by_current_column(descending=False) == (1, 2, 0)
    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Ether"
    assert workbench.model.data(workbench.model.index(2, 1), Qt.ItemDataRole.DisplayRole) == "Potion"

    assert workbench.sort_by_current_column(descending=True) == (2, 1, 0)
    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Potion"
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Ether"
    assert workbench.model.data(workbench.model.index(2, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"

    workbench.close()
    app.quit()


def test_table_workbench_paste_participates_in_undo_redo_flow():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")
    undo_button = workbench.findChild(QToolButton, "table-workbench-undo-button")
    redo_button = workbench.findChild(QToolButton, "table-workbench-redo-button")

    assert undo_button is not None
    assert redo_button is not None

    view.setCurrentIndex(workbench.model.index(0, 1))
    QApplication.clipboard().setText("Mega Potion")

    workbench.paste_clipboard()

    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Mega Potion"

    undo_button.click()

    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Potion"

    redo_button.click()

    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Mega Potion"

    workbench.close()
    app.quit()


def test_table_workbench_paste_reports_readonly_rejection_without_history():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")

    view.setCurrentIndex(workbench.model.index(0, 0))
    QApplication.clipboard().setText("9999")

    workbench.paste_clipboard()

    assert workbench.model.data(workbench.model.index(0, 0), Qt.ItemDataRole.DisplayRole) == 1001
    assert workbench.property("last-rejected-write") == "readonly"
    assert workbench.commands.can_undo is False

    workbench.close()
    app.quit()


def test_table_workbench_visible_edit_commit_and_cancel_flow():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")
    edit_input = workbench.findChild(QLineEdit, "table-workbench-edit-input")
    commit_button = workbench.findChild(QToolButton, "table-workbench-commit-edit-button")
    cancel_button = workbench.findChild(QToolButton, "table-workbench-cancel-edit-button")

    assert edit_input is not None
    assert commit_button is not None
    assert cancel_button is not None

    view.setCurrentIndex(workbench.model.index(0, 1))
    workbench.load_current_cell_for_edit()

    assert edit_input.text() == "Potion"

    edit_input.setText("Mega Potion")
    cancel_button.click()

    assert edit_input.text() == "Potion"
    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Potion"
    assert workbench.commands.can_undo is False

    edit_input.setText("Mega Potion")
    commit_button.click()

    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Mega Potion"
    assert workbench.commands.can_undo is True

    workbench.close()
    app.quit()


def test_table_workbench_multi_cell_paste_participates_in_undo_redo_flow():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")
    undo_button = workbench.findChild(QToolButton, "table-workbench-undo-button")
    redo_button = workbench.findChild(QToolButton, "table-workbench-redo-button")

    assert undo_button is not None
    assert redo_button is not None

    view.setCurrentIndex(workbench.model.index(0, 1))
    QApplication.clipboard().setText("Hi-Potion\t99\nEther\t5")

    workbench.paste_clipboard()

    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Hi-Potion"
    assert workbench.model.data(workbench.model.index(0, 2), Qt.ItemDataRole.DisplayRole) == 99
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Ether"
    assert workbench.model.data(workbench.model.index(1, 2), Qt.ItemDataRole.DisplayRole) == 5

    undo_button.click()

    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Potion"
    assert workbench.model.data(workbench.model.index(0, 2), Qt.ItemDataRole.DisplayRole) == 10
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"
    assert workbench.model.data(workbench.model.index(1, 2), Qt.ItemDataRole.DisplayRole) == 2

    redo_button.click()

    assert workbench.model.data(workbench.model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Hi-Potion"
    assert workbench.model.data(workbench.model.index(0, 2), Qt.ItemDataRole.DisplayRole) == 99
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Ether"
    assert workbench.model.data(workbench.model.index(1, 2), Qt.ItemDataRole.DisplayRole) == 5

    workbench.close()
    app.quit()


def test_table_workbench_insert_and_delete_rows_participate_in_undo_redo_flow():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")
    add_button = workbench.findChild(QToolButton, "table-workbench-add-row-button")
    delete_button = workbench.findChild(QToolButton, "table-workbench-delete-row-button")
    undo_button = workbench.findChild(QToolButton, "table-workbench-undo-button")
    redo_button = workbench.findChild(QToolButton, "table-workbench-redo-button")

    assert add_button is not None
    assert delete_button is not None
    assert undo_button is not None
    assert redo_button is not None

    view.setCurrentIndex(workbench.model.index(1, 1))
    add_button.click()

    assert workbench.model.rowCount() == 4
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == ""

    undo_button.click()

    assert workbench.model.rowCount() == 3
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"

    redo_button.click()

    assert workbench.model.rowCount() == 4
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == ""

    view.setCurrentIndex(workbench.model.index(1, 1))
    delete_button.click()

    assert workbench.model.rowCount() == 3
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"

    undo_button.click()

    assert workbench.model.rowCount() == 4
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == ""

    redo_button.click()

    assert workbench.model.rowCount() == 3
    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"

    workbench.close()
    app.quit()


def test_table_workbench_batch_fill_participates_in_undo_redo_flow():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")
    fill_input = workbench.findChild(QLineEdit, "table-workbench-fill-input")
    fill_button = workbench.findChild(QToolButton, "table-workbench-fill-button")
    undo_button = workbench.findChild(QToolButton, "table-workbench-undo-button")
    redo_button = workbench.findChild(QToolButton, "table-workbench-redo-button")

    assert fill_input is not None
    assert fill_button is not None
    assert undo_button is not None
    assert redo_button is not None

    selection_model = view.selectionModel()
    selection_model.select(
        workbench.model.index(0, 2),
        QItemSelectionModel.SelectionFlag.Select,
    )
    selection_model.select(
        workbench.model.index(1, 2),
        QItemSelectionModel.SelectionFlag.Select,
    )
    fill_input.setText("7")

    fill_button.click()

    assert workbench.model.data(workbench.model.index(0, 2), Qt.ItemDataRole.DisplayRole) == 7
    assert workbench.model.data(workbench.model.index(1, 2), Qt.ItemDataRole.DisplayRole) == 7

    undo_button.click()

    assert workbench.model.data(workbench.model.index(0, 2), Qt.ItemDataRole.DisplayRole) == 10
    assert workbench.model.data(workbench.model.index(1, 2), Qt.ItemDataRole.DisplayRole) == 2

    redo_button.click()

    assert workbench.model.data(workbench.model.index(0, 2), Qt.ItemDataRole.DisplayRole) == 7
    assert workbench.model.data(workbench.model.index(1, 2), Qt.ItemDataRole.DisplayRole) == 7

    workbench.close()
    app.quit()


def test_table_workbench_large_table_batch_fill_reports_changed_cell_count():
    app = QApplication.instance() or QApplication([])
    table = NormalTableDefinition(
        table_id="large_items",
        display_name="Large Items",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
            FieldDefinition(field_id="name", name="name", display_name="Name", field_type=FieldType.STRING),
            FieldDefinition(field_id="count", name="count", display_name="Count", field_type=FieldType.INT),
        ],
        rows=[
            TableRow(values={"id": 1000 + row, "name": f"Item {row}", "count": row})
            for row in range(250)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")
    fill_input = workbench.findChild(QLineEdit, "table-workbench-fill-input")

    assert view.verticalScrollMode() == view.ScrollMode.ScrollPerPixel
    assert view.horizontalScrollMode() == view.ScrollMode.ScrollPerPixel

    selection_model = view.selectionModel()
    for row in (0, 127, 249):
        selection_model.select(
            workbench.model.index(row, 2),
            QItemSelectionModel.SelectionFlag.Select,
        )
    fill_input.setText("7")

    changed = workbench.batch_fill_selection()

    assert changed == ((0, 2), (127, 2), (249, 2))
    assert workbench.property("last-batch-edit-count") == 3
    assert workbench.model.data(workbench.model.index(249, 2), Qt.ItemDataRole.DisplayRole) == 7

    workbench.close()
    app.quit()


def test_table_workbench_large_table_batch_fill_focuses_last_changed_cell():
    app = QApplication.instance() or QApplication([])
    table = NormalTableDefinition(
        table_id="large_items",
        display_name="Large Items",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
            FieldDefinition(field_id="name", name="name", display_name="Name", field_type=FieldType.STRING),
            FieldDefinition(field_id="count", name="count", display_name="Count", field_type=FieldType.INT),
        ],
        rows=[
            TableRow(values={"id": 1000 + row, "name": f"Item {row}", "count": row})
            for row in range(250)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")
    fill_input = workbench.findChild(QLineEdit, "table-workbench-fill-input")

    selection_model = view.selectionModel()
    for row in (0, 127, 249):
        selection_model.select(
            workbench.model.index(row, 2),
            QItemSelectionModel.SelectionFlag.Select,
        )
    fill_input.setText("7")

    changed = workbench.batch_fill_selection()

    assert changed[-1] == (249, 2)
    assert view.currentIndex().row() == 249
    assert view.currentIndex().column() == 2

    workbench.close()
    app.quit()


def test_table_workbench_large_table_ctrl_home_end_navigates_edges():
    app = QApplication.instance() or QApplication([])
    table = NormalTableDefinition(
        table_id="large_items",
        display_name="Large Items",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
            FieldDefinition(field_id="name", name="name", display_name="Name", field_type=FieldType.STRING),
            FieldDefinition(field_id="count", name="count", display_name="Count", field_type=FieldType.INT),
        ],
        rows=[
            TableRow(values={"id": 1000 + row, "name": f"Item {row}", "count": row})
            for row in range(250)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")

    view.setCurrentIndex(workbench.model.index(127, 2))
    QApplication.sendEvent(
        view,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_End,
            Qt.KeyboardModifier.ControlModifier,
        ),
    )

    assert view.currentIndex().row() == 249
    assert view.currentIndex().column() == 2

    QApplication.sendEvent(
        view,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Home,
            Qt.KeyboardModifier.ControlModifier,
        ),
    )

    assert view.currentIndex().row() == 0
    assert view.currentIndex().column() == 2

    workbench.close()
    app.quit()


def test_table_workbench_wide_table_ctrl_left_right_navigates_row_edges():
    app = QApplication.instance() or QApplication([])
    fields = [
        FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
        *[
            FieldDefinition(
                field_id=f"value_{column}",
                name=f"value_{column}",
                display_name=f"Value {column}",
                field_type=FieldType.INT,
            )
            for column in range(8)
        ],
    ]
    table = NormalTableDefinition(
        table_id="wide_items",
        display_name="Wide Items",
        fields=fields,
        rows=[
            TableRow(values={"id": 1000 + row, **{f"value_{column}": row * 10 + column for column in range(8)}})
            for row in range(40)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")

    view.setCurrentIndex(workbench.model.index(17, 3))
    QApplication.sendEvent(
        view,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Right,
            Qt.KeyboardModifier.ControlModifier,
        ),
    )

    assert view.currentIndex().row() == 17
    assert view.currentIndex().column() == workbench.model.columnCount() - 1

    QApplication.sendEvent(
        view,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Left,
            Qt.KeyboardModifier.ControlModifier,
        ),
    )

    assert view.currentIndex().row() == 17
    assert view.currentIndex().column() == 0

    workbench.close()
    app.quit()


def test_table_workbench_large_table_reports_scrollbar_position_for_handfeel():
    app = QApplication.instance() or QApplication([])
    fields = [
        FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
        *[
            FieldDefinition(
                field_id=f"value_{column}",
                name=f"value_{column}",
                display_name=f"Value {column}",
                field_type=FieldType.INT,
            )
            for column in range(12)
        ],
    ]
    table = NormalTableDefinition(
        table_id="scroll_items",
        display_name="Scroll Items",
        fields=fields,
        rows=[
            TableRow(values={"id": 1000 + row, **{f"value_{column}": row * 10 + column for column in range(12)}})
            for row in range(320)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")
    view.resize(360, 220)
    workbench.show()
    QApplication.processEvents()

    vertical = view.verticalScrollBar()
    horizontal = view.horizontalScrollBar()
    vertical.setValue(max(1, vertical.maximum() // 2))
    horizontal.setValue(max(1, horizontal.maximum() // 2))
    QApplication.processEvents()

    scroll_position = workbench.property("scroll-position")

    assert scroll_position["vertical"] == vertical.value()
    assert scroll_position["horizontal"] == horizontal.value()
    assert scroll_position["vertical-maximum"] == vertical.maximum()
    assert scroll_position["horizontal-maximum"] == horizontal.maximum()

    workbench.close()
    app.quit()


def test_table_workbench_large_table_reports_visible_range_for_drag_feedback():
    app = QApplication.instance() or QApplication([])
    fields = [
        FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
        *[
            FieldDefinition(
                field_id=f"value_{column}",
                name=f"value_{column}",
                display_name=f"Value {column}",
                field_type=FieldType.INT,
            )
            for column in range(16)
        ],
    ]
    table = NormalTableDefinition(
        table_id="visible_range_items",
        display_name="Visible Range Items",
        fields=fields,
        rows=[
            TableRow(values={"id": 1000 + row, **{f"value_{column}": row * 10 + column for column in range(16)}})
            for row in range(360)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")
    view.resize(360, 220)
    workbench.show()
    QApplication.processEvents()

    initial_range = workbench.property("visible-range")
    view.verticalScrollBar().setValue(max(1, view.verticalScrollBar().maximum() // 2))
    view.horizontalScrollBar().setValue(max(1, view.horizontalScrollBar().maximum() // 2))
    QApplication.processEvents()

    visible_range = workbench.property("visible-range")

    assert visible_range["first-row"] > initial_range["first-row"]
    assert visible_range["last-row"] >= visible_range["first-row"]
    assert visible_range["first-column"] >= initial_range["first-column"]
    assert visible_range["last-column"] >= visible_range["first-column"]

    workbench.close()
    app.quit()


def test_table_workbench_large_table_shows_visible_range_status_for_hand_acceptance():
    app = QApplication.instance() or QApplication([])
    fields = [
        FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
        *[
            FieldDefinition(
                field_id=f"value_{column}",
                name=f"value_{column}",
                display_name=f"Value {column}",
                field_type=FieldType.INT,
            )
            for column in range(16)
        ],
    ]
    table = NormalTableDefinition(
        table_id="visible_range_status_items",
        display_name="Visible Range Status Items",
        fields=fields,
        rows=[
            TableRow(values={"id": 1000 + row, **{f"value_{column}": row * 10 + column for column in range(16)}})
            for row in range(360)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")
    status = workbench.findChild(QLabel, "table-workbench-visible-range-label")
    view.resize(360, 220)
    workbench.show()
    QApplication.processEvents()

    view.verticalScrollBar().setValue(max(1, view.verticalScrollBar().maximum() // 2))
    view.horizontalScrollBar().setValue(max(1, view.horizontalScrollBar().maximum() // 2))
    QApplication.processEvents()

    visible_range = workbench.property("visible-range")

    assert status is not None
    assert status.text() == (
        f"行 {visible_range['first-row'] + 1}-{visible_range['last-row'] + 1} / "
        f"列 {visible_range['first-column'] + 1}-{visible_range['last-column'] + 1}"
    )

    workbench.close()
    app.quit()


def test_table_workbench_large_table_shows_scroll_progress_status_for_drag_feedback():
    app = QApplication.instance() or QApplication([])
    fields = [
        FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
        *[
            FieldDefinition(
                field_id=f"value_{column}",
                name=f"value_{column}",
                display_name=f"Value {column}",
                field_type=FieldType.INT,
            )
            for column in range(16)
        ],
    ]
    table = NormalTableDefinition(
        table_id="scroll_progress_items",
        display_name="Scroll Progress Items",
        fields=fields,
        rows=[
            TableRow(values={"id": 1000 + row, **{f"value_{column}": row * 10 + column for column in range(16)}})
            for row in range(360)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")
    status = workbench.findChild(QLabel, "table-workbench-scroll-progress-label")
    view.resize(360, 220)
    workbench.show()
    QApplication.processEvents()

    view.verticalScrollBar().setValue(max(1, view.verticalScrollBar().maximum() // 2))
    view.horizontalScrollBar().setValue(max(1, view.horizontalScrollBar().maximum() // 2))
    QApplication.processEvents()

    scroll_position = workbench.property("scroll-position")
    vertical_percent = round(scroll_position["vertical"] * 100 / scroll_position["vertical-maximum"])
    horizontal_percent = round(scroll_position["horizontal"] * 100 / scroll_position["horizontal-maximum"])

    assert status is not None
    assert status.text() == f"纵向 {vertical_percent}% / 横向 {horizontal_percent}%"

    workbench.close()
    app.quit()


def test_table_workbench_large_table_shows_last_scroll_axis_for_drag_feedback():
    app = QApplication.instance() or QApplication([])
    fields = [
        FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
        *[
            FieldDefinition(
                field_id=f"value_{column}",
                name=f"value_{column}",
                display_name=f"Value {column}",
                field_type=FieldType.INT,
            )
            for column in range(16)
        ],
    ]
    table = NormalTableDefinition(
        table_id="scroll_axis_items",
        display_name="Scroll Axis Items",
        fields=fields,
        rows=[
            TableRow(values={"id": 1000 + row, **{f"value_{column}": row * 10 + column for column in range(16)}})
            for row in range(360)
        ],
        primary_key="id",
    )
    workbench = TableWorkbench(table)
    view = workbench.findChild(QTableView, "table-workbench-view")
    status = workbench.findChild(QLabel, "table-workbench-scroll-axis-label")
    view.resize(360, 220)
    workbench.show()
    QApplication.processEvents()

    view.verticalScrollBar().setValue(max(1, view.verticalScrollBar().maximum() // 2))
    QApplication.processEvents()

    assert status is not None
    assert workbench.property("last-scroll-axis") == "vertical"
    assert status.text() == "最近滚动：纵向"

    view.horizontalScrollBar().setValue(max(1, view.horizontalScrollBar().maximum() // 2))
    QApplication.processEvents()

    assert workbench.property("last-scroll-axis") == "horizontal"
    assert status.text() == "最近滚动：横向"

    workbench.close()
    app.quit()


def test_table_workbench_keyboard_copy_paste_undo_redo_flow():
    app = QApplication.instance() or QApplication([])
    workbench = TableWorkbench()
    view = workbench.findChild(QTableView, "table-workbench-view")

    view.setCurrentIndex(workbench.model.index(0, 1))
    QApplication.sendEvent(
        view,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_C,
            Qt.KeyboardModifier.ControlModifier,
        ),
    )

    assert QApplication.clipboard().text() == "Potion"

    view.setCurrentIndex(workbench.model.index(1, 1))
    QApplication.clipboard().setText("Mega Potion")
    QApplication.sendEvent(
        view,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_V,
            Qt.KeyboardModifier.ControlModifier,
        ),
    )

    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Mega Potion"

    QApplication.sendEvent(
        view,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Z,
            Qt.KeyboardModifier.ControlModifier,
        ),
    )

    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"

    QApplication.sendEvent(
        view,
        QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Y,
            Qt.KeyboardModifier.ControlModifier,
        ),
    )

    assert workbench.model.data(workbench.model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Mega Potion"

    workbench.close()
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

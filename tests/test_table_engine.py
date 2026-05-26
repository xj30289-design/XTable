from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy

from xtable.domain.models import FieldDefinition, FieldType, NormalTableDefinition, ProjectSchema, TableRow
from xtable.table_engine import CellState, EditCommandStack, QtTableModel, TableBuffer


def build_table() -> NormalTableDefinition:
    return NormalTableDefinition(
        table_id="items",
        display_name="Items",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
            FieldDefinition(field_id="name", name="name", display_name="Name", field_type=FieldType.STRING),
            FieldDefinition(field_id="count", name="count", display_name="Count", field_type=FieldType.INT),
        ],
        rows=[
            TableRow(values={"id": 1001, "name": "Potion", "count": 10}),
            TableRow(values={"id": 1002, "name": "Elixir", "count": 2}),
        ],
    )


def test_table_buffer_exposes_phase2_table_rows_columns_headers_and_values():
    buffer = TableBuffer(build_table())

    assert buffer.row_count == 2
    assert buffer.column_count == 3
    assert buffer.horizontal_header(1) == "Name"
    assert buffer.vertical_header(1) == "2"
    assert buffer.value_at(0, 1) == "Potion"


def test_table_buffer_edits_cells_and_rejects_readonly_fields():
    buffer = TableBuffer(build_table())

    assert buffer.set_value(0, 1, "Mega Potion") is True
    assert buffer.value_at(0, 1) == "Mega Potion"
    assert buffer.set_value(0, 0, "changed_id") is False
    assert buffer.value_at(0, 0) == 1001


def test_table_buffer_copies_pastes_inserts_and_deletes_rows():
    buffer = TableBuffer(build_table())

    assert buffer.copy_range(0, 1, 1, 2) == "Potion\t10\nElixir\t2"
    changes = buffer.paste_tsv(0, 1, "Hi-Potion\t99\nEther\t5")

    assert changes == ((0, 1), (0, 2), (1, 1), (1, 2))
    assert buffer.copy_range(0, 1, 1, 2) == "Hi-Potion\t99\nEther\t5"

    buffer.insert_row(1)
    assert buffer.row_count == 3
    assert buffer.value_at(1, 0) is None
    assert buffer.value_at(1, 1) == ""
    buffer.delete_rows(1, 1)
    assert buffer.row_count == 2


def test_qt_table_model_exposes_data_headers_flags_and_set_data():
    model = QtTableModel(TableBuffer(build_table()))

    assert model.rowCount() == 2
    assert model.columnCount() == 3
    assert model.headerData(1, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == "Name"
    assert model.headerData(0, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole) == "1"
    assert model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Potion"
    assert model.setData(model.index(0, 1), "Mega Potion", Qt.ItemDataRole.EditRole) is True
    assert model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Mega Potion"

    readonly_flags = model.flags(model.index(0, 0))
    editable_flags = model.flags(model.index(0, 1))

    assert not readonly_flags & Qt.ItemFlag.ItemIsEditable
    assert editable_flags & Qt.ItemFlag.ItemIsEditable
    assert model.setData(model.index(0, 0), "changed_id", Qt.ItemDataRole.EditRole) is False


def test_qt_table_model_inserts_and_removes_rows():
    model = QtTableModel(TableBuffer(build_table()))

    assert model.insertRows(1, 1) is True
    assert model.rowCount() == 3
    assert model.data(model.index(1, 1), Qt.ItemDataRole.DisplayRole) == ""

    assert model.removeRows(1, 1) is True
    assert model.rowCount() == 2


def test_table_model_maps_cell_states_for_errors_warnings_readonly_and_references():
    buffer = TableBuffer(build_table())
    model = QtTableModel(buffer)
    state_spy = QSignalSpy(model.dataChanged)
    model.set_cell_state(0, 1, CellState("error", "Name is required"))
    model.set_cell_state(1, 1, CellState("warning", "Name is duplicated"))
    model.set_cell_state(1, 2, CellState("reference", "Referenced by drops"))

    assert model.data(model.index(0, 1), Qt.ItemDataRole.UserRole) == "error"
    assert model.data(model.index(0, 1), Qt.ItemDataRole.ToolTipRole) == "Name is required"
    assert model.data(model.index(1, 1), Qt.ItemDataRole.UserRole) == "warning"
    assert model.data(model.index(1, 2), Qt.ItemDataRole.UserRole) == "reference"
    assert model.data(model.index(0, 0), Qt.ItemDataRole.UserRole) == "readonly"
    assert state_spy.count() == 3


def test_edit_command_stack_undoes_and_redoes_cell_edits():
    model = QtTableModel(TableBuffer(build_table()))
    stack = EditCommandStack(model)
    change_spy = QSignalSpy(model.dataChanged)

    assert stack.can_undo is False
    assert stack.edit_cell(0, 1, "Mega Potion") is True
    assert model.buffer.value_at(0, 1) == "Mega Potion"
    assert stack.can_undo is True
    assert stack.can_redo is False

    assert stack.undo() is True
    assert model.buffer.value_at(0, 1) == "Potion"
    assert stack.can_redo is True

    assert stack.redo() is True
    assert model.buffer.value_at(0, 1) == "Mega Potion"
    assert stack.edit_cell(0, 0, "changed_id") is False
    assert model.buffer.value_at(0, 0) == 1001
    assert change_spy.count() == 3


def test_table_buffer_parses_tsv_values_by_field_type_and_rejects_invalid_input():
    table = build_table()
    buffer = TableBuffer(table)

    assert buffer.paste_tsv(0, 2, "99") == ((0, 2),)
    assert buffer.value_at(0, 2) == 99
    assert isinstance(buffer.value_at(0, 2), int)

    assert buffer.paste_tsv(0, 2, "not-int") == ()
    assert buffer.value_at(0, 2) == 99
    assert buffer.cell_state(0, 2).kind == "error"

    schema = ProjectSchema()
    schema.add_table(table)
    schema.validate_structure()


def test_table_buffer_handles_empty_and_out_of_bounds_ranges_without_tracebacks():
    empty = TableBuffer(NormalTableDefinition(table_id="empty", display_name="Empty", fields=[], rows=[]))
    buffer = TableBuffer(build_table())

    assert empty.copy_range(0, 0, 10, 10) == ""
    assert buffer.copy_range(-2, -1, 20, 20) == "1001\tPotion\t10\n1002\tElixir\t2"
    assert buffer.value_at(99, 99) is None
    assert buffer.paste_tsv(99, 99, "ignored") == ()
    buffer.delete_rows(99, 10)
    assert buffer.row_count == 2


def test_table_buffer_batch_fill_find_replace_filter_and_sort_helpers():
    buffer = TableBuffer(build_table())

    assert buffer.batch_fill([(0, 1), (1, 1)], "Potion") == ((0, 1), (1, 1))
    assert buffer.find_cells("potion") == ((0, 1), (1, 1))
    assert buffer.replace_all("Potion", "Hi-Potion") == ((0, 1), (1, 1))
    assert buffer.copy_range(0, 1, 1, 1) == "Hi-Potion\nHi-Potion"

    buffer.set_value(1, 2, 99)

    assert buffer.filter_rows("hi-potion") == (0, 1)
    assert buffer.sort_row_order("count") == (0, 1)
    assert buffer.sort_row_order("count", descending=True) == (1, 0)


def test_qt_table_model_replace_all_emits_changed_cells():
    model = QtTableModel(TableBuffer(build_table()))
    change_spy = QSignalSpy(model.dataChanged)

    assert model.replace_all("Potion", "Hi-Potion") == ((0, 1),)
    assert model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Hi-Potion"
    assert change_spy.count() == 1


def test_qt_table_model_sorts_rows_and_keeps_cell_states_with_source_rows():
    model = QtTableModel(TableBuffer(build_table()))
    about_spy = QSignalSpy(model.layoutAboutToBeChanged)
    changed_spy = QSignalSpy(model.layoutChanged)
    model.set_cell_state(1, 1, CellState("warning", "Elixir warning"))

    assert model.sort_by_column(2, descending=False) == (1, 0)
    assert model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole) == "Elixir"
    assert model.data(model.index(1, 1), Qt.ItemDataRole.DisplayRole) == "Potion"
    assert model.data(model.index(0, 1), Qt.ItemDataRole.UserRole) == "warning"
    assert about_spy.count() == 1
    assert changed_spy.count() == 1

from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from xtable.domain.models import FieldDefinition, FieldType, TableDefinition, TableRow


@dataclass(frozen=True)
class CellState:
    kind: str
    message: str = ""


@dataclass(frozen=True)
class CellEditCommand:
    row: int
    column: int
    old_value: Any
    new_value: Any


@dataclass(frozen=True)
class CellEditBatchCommand:
    edits: tuple[CellEditCommand, ...]


@dataclass(frozen=True)
class RowEditCommand:
    action: str
    row: int
    rows: tuple[TableRow, ...]


class TableBuffer:
    def __init__(self, table: TableDefinition) -> None:
        self.table = table
        self._cell_states: dict[tuple[int, int], CellState] = {}

    @property
    def row_count(self) -> int:
        return len(self.table.rows)

    @property
    def column_count(self) -> int:
        return len(self.table.fields)

    def horizontal_header(self, column: int) -> str:
        if column < 0 or column >= self.column_count:
            return ""
        return self.table.fields[column].display_name

    def vertical_header(self, row: int) -> str:
        if row < 0 or row >= self.row_count:
            return ""
        return str(row + 1)

    def value_at(self, row: int, column: int) -> Any:
        if row < 0 or row >= self.row_count or column < 0 or column >= self.column_count:
            return None
        field = self.table.fields[column]
        table_row = self.table.rows[row]
        return table_row.values.get(field.name, table_row.values.get(field.field_id, field.empty_value()))

    def set_value(self, row: int, column: int, value: Any, *, parse: bool = False) -> bool:
        if not self.is_editable(row, column):
            return False
        field = self.table.fields[column]
        if parse:
            parsed = self.parse_cell_value(field, value)
            if not parsed.ok:
                self.set_cell_state(row, column, CellState("error", parsed.error))
                return False
            value = parsed.value
        self.table.rows[row].values[field.name] = value
        if self.cell_state(row, column).kind == "error":
            self.set_cell_state(row, column, CellState("normal"))
        return True

    def is_editable(self, row: int, column: int) -> bool:
        if row < 0 or row >= self.row_count or column < 0 or column >= self.column_count:
            return False
        field = self.table.fields[column]
        state = self.cell_state(row, column)
        return not field.readonly and field.field_id not in getattr(self.table, "readonly_fields", ()) and state.kind != "readonly"

    def set_cell_state(self, row: int, column: int, state: CellState) -> None:
        if row < 0 or row >= self.row_count or column < 0 or column >= self.column_count:
            return
        self._cell_states[(row, column)] = state

    def cell_state(self, row: int, column: int) -> CellState:
        if row < 0 or row >= self.row_count or column < 0 or column >= self.column_count:
            return CellState("invalid")
        field = self.table.fields[column]
        if field.readonly or field.field_id in getattr(self.table, "readonly_fields", ()):
            return CellState("readonly")
        return self._cell_states.get((row, column), CellState("normal"))

    def copy_range(self, top: int, left: int, bottom: int, right: int) -> str:
        if self.row_count == 0 or self.column_count == 0:
            return ""
        top = max(top, 0)
        left = max(left, 0)
        bottom = min(bottom, self.row_count - 1)
        right = min(right, self.column_count - 1)
        if top > bottom or left > right:
            return ""
        lines: list[str] = []
        for row in range(top, bottom + 1):
            values = [str(self.value_at(row, column)) for column in range(left, right + 1)]
            lines.append("\t".join(values))
        return "\n".join(lines)

    def paste_tsv(self, start_row: int, start_column: int, text: str) -> tuple[tuple[int, int], ...]:
        changed: list[tuple[int, int]] = []
        for row_offset, line in enumerate(text.splitlines()):
            for column_offset, value in enumerate(line.split("\t")):
                row = start_row + row_offset
                column = start_column + column_offset
                if row >= self.row_count or column >= self.column_count:
                    continue
                if self.set_value(row, column, value, parse=True):
                    changed.append((row, column))
        return tuple(changed)

    def batch_fill(self, cells: Iterable[tuple[int, int]], value: Any) -> tuple[tuple[int, int], ...]:
        changed: list[tuple[int, int]] = []
        for row, column in cells:
            if self.set_value(row, column, value, parse=isinstance(value, str)):
                changed.append((row, column))
        return tuple(changed)

    def find_cells(self, query: str) -> tuple[tuple[int, int], ...]:
        needle = query.lower()
        matches: list[tuple[int, int]] = []
        for row in range(self.row_count):
            for column in range(self.column_count):
                if needle in str(self.value_at(row, column)).lower():
                    matches.append((row, column))
        return tuple(matches)

    def replace_all(self, old: str, new: str) -> tuple[tuple[int, int], ...]:
        changed: list[tuple[int, int]] = []
        for row, column in self.find_cells(old):
            if str(self.value_at(row, column)) == old and self.set_value(row, column, new, parse=True):
                changed.append((row, column))
        return tuple(changed)

    def filter_rows(self, query: str) -> tuple[int, ...]:
        needle = query.lower()
        rows: list[int] = []
        for row in range(self.row_count):
            if any(needle in str(self.value_at(row, column)).lower() for column in range(self.column_count)):
                rows.append(row)
        return tuple(rows)

    def sort_row_order(self, field_id_or_name: str, *, descending: bool = False) -> tuple[int, ...]:
        try:
            field = self.table.field(field_id_or_name)
        except KeyError:
            return tuple(range(self.row_count))
        column = self.table.fields.index(field)
        return tuple(sorted(range(self.row_count), key=lambda row: self.value_at(row, column), reverse=descending))

    def reorder_rows(self, order: Iterable[int]) -> tuple[int, ...]:
        order_tuple = tuple(order)
        if sorted(order_tuple) != list(range(self.row_count)):
            return tuple(range(self.row_count))
        rows = [self.table.rows[row] for row in order_tuple]
        old_states = self._cell_states
        self.table.rows[:] = rows
        self._cell_states = {
            (new_row, column): state
            for new_row, old_row in enumerate(order_tuple)
            for (state_row, column), state in old_states.items()
            if state_row == old_row
        }
        return order_tuple

    def insert_row(self, row: int, values: dict[str, Any] | None = None) -> None:
        initial_values = values if values is not None else {field.name: field.initial_value() for field in self.table.fields}
        self.table.rows.insert(row, TableRow(values=initial_values))

    def delete_rows(self, row: int, count: int) -> None:
        if row < 0 or row >= self.row_count or count < 1:
            return
        count = min(count, self.row_count - row)
        del self.table.rows[row : row + count]

    def parse_cell_value(self, field: FieldDefinition, raw_value: Any) -> ParsedCellValue:
        if not isinstance(raw_value, str):
            return ParsedCellValue(True, raw_value)
        value = raw_value.strip()
        if value == "":
            return ParsedCellValue(True, field.empty_value())
        try:
            if field.field_type in {FieldType.INT, FieldType.ID}:
                return ParsedCellValue(True, int(value))
            if field.field_type == FieldType.FLOAT:
                return ParsedCellValue(True, float(value))
            if field.field_type == FieldType.BOOL:
                normalized = value.lower()
                if normalized in {"true", "1", "yes", "y"}:
                    return ParsedCellValue(True, True)
                if normalized in {"false", "0", "no", "n"}:
                    return ParsedCellValue(True, False)
                return ParsedCellValue(False, error=f"Field {field.name} expects bool")
            if field.field_type in {FieldType.LIST, FieldType.JSON, FieldType.META}:
                parsed = json.loads(value)
                expected = list if field.field_type == FieldType.LIST else dict
                if not isinstance(parsed, expected):
                    return ParsedCellValue(False, error=f"Field {field.name} expects {expected.__name__}")
                return ParsedCellValue(True, parsed)
        except (TypeError, ValueError, json.JSONDecodeError):
            return ParsedCellValue(False, error=f"Field {field.name} expects {field.field_type.value}")
        return ParsedCellValue(True, raw_value)


class QtTableModel(QAbstractTableModel):
    def __init__(self, buffer: TableBuffer) -> None:
        super().__init__()
        self.buffer = buffer

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        if parent is not None and parent.isValid():
            return 0
        return self.buffer.row_count

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        if parent is not None and parent.isValid():
            return 0
        return self.buffer.column_count

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.buffer.horizontal_header(section)
        return self.buffer.vertical_header(section)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.UserRole:
            return self.buffer.cell_state(index.row(), index.column()).kind
        if role == Qt.ItemDataRole.ToolTipRole:
            return self.buffer.cell_state(index.row(), index.column()).message
        if role not in {Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole}:
            return None
        return self.buffer.value_at(index.row(), index.column())

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
        if not self.buffer.set_value(index.row(), index.column(), value, parse=isinstance(value, str)):
            return False
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if self.buffer.is_editable(index.row(), index.column()):
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def insertRows(self, row: int, count: int, parent: QModelIndex | None = None) -> bool:
        parent_index = parent or QModelIndex()
        if row < 0 or row > self.buffer.row_count or count < 1:
            return False
        self.beginInsertRows(parent_index, row, row + count - 1)
        for offset in range(count):
            self.buffer.insert_row(row + offset)
        self.endInsertRows()
        return True

    def insert_table_rows(self, row: int, rows: Iterable[TableRow], parent: QModelIndex | None = None) -> bool:
        rows_tuple = tuple(deepcopy(tuple(rows)))
        parent_index = parent or QModelIndex()
        if row < 0 or row > self.buffer.row_count or not rows_tuple:
            return False
        self.beginInsertRows(parent_index, row, row + len(rows_tuple) - 1)
        for offset, table_row in enumerate(rows_tuple):
            self.buffer.table.rows.insert(row + offset, table_row)
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex | None = None) -> bool:
        parent_index = parent or QModelIndex()
        if row < 0 or count < 1 or row + count > self.buffer.row_count:
            return False
        self.beginRemoveRows(parent_index, row, row + count - 1)
        self.buffer.delete_rows(row, count)
        self.endRemoveRows()
        return True

    def paste_tsv(self, start_row: int, start_column: int, text: str) -> tuple[tuple[int, int], ...]:
        changed = self.buffer.paste_tsv(start_row, start_column, text)
        self._emit_changed_cells(changed)
        return changed

    def batch_fill(self, cells: Iterable[tuple[int, int]], value: Any) -> tuple[tuple[int, int], ...]:
        changed = self.buffer.batch_fill(cells, value)
        self._emit_changed_cells(changed)
        return changed

    def replace_all(self, old: str, new: str) -> tuple[tuple[int, int], ...]:
        if not old:
            return ()
        changed = self.buffer.replace_all(old, new)
        self._emit_changed_cells(changed)
        return changed

    def sort_by_column(self, column: int, *, descending: bool = False) -> tuple[int, ...]:
        if column < 0 or column >= self.buffer.column_count:
            return tuple(range(self.buffer.row_count))
        field = self.buffer.table.fields[column]
        order = self.buffer.sort_row_order(field.name, descending=descending)
        if order == tuple(range(self.buffer.row_count)):
            return order
        self.layoutAboutToBeChanged.emit()
        order = self.buffer.reorder_rows(order)
        self.layoutChanged.emit()
        return order

    def set_cell_state(self, row: int, column: int, state: CellState) -> None:
        self.buffer.set_cell_state(row, column, state)
        index = self.index(row, column)
        if index.isValid():
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.UserRole, Qt.ItemDataRole.ToolTipRole])

    def _emit_changed_cells(self, cells: Iterable[tuple[int, int]]) -> None:
        for row, column in cells:
            index = self.index(row, column)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])


@dataclass(frozen=True)
class ParsedCellValue:
    ok: bool
    value: Any = None
    error: str = ""


class EditCommandStack:
    def __init__(self, model: QtTableModel) -> None:
        self.model = model
        self._undo_stack: list[CellEditBatchCommand | RowEditCommand] = []
        self._redo_stack: list[CellEditBatchCommand | RowEditCommand] = []

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def edit_cell(self, row: int, column: int, value: Any) -> bool:
        old_value = self.model.buffer.value_at(row, column)
        if not self.model.setData(self.model.index(row, column), value, Qt.ItemDataRole.EditRole):
            return False
        command = CellEditCommand(row=row, column=column, old_value=old_value, new_value=value)
        self._undo_stack.append(CellEditBatchCommand((command,)))
        self._redo_stack.clear()
        return True

    def paste_tsv(self, start_row: int, start_column: int, text: str) -> tuple[tuple[int, int], ...]:
        old_values: dict[tuple[int, int], Any] = {}
        for row_offset, line in enumerate(text.splitlines()):
            for column_offset, _value in enumerate(line.split("\t")):
                row = start_row + row_offset
                column = start_column + column_offset
                old_values[(row, column)] = self.model.buffer.value_at(row, column)

        changed = self.model.paste_tsv(start_row, start_column, text)
        edits = tuple(
            CellEditCommand(
                row=row,
                column=column,
                old_value=old_values[(row, column)],
                new_value=self.model.buffer.value_at(row, column),
            )
            for row, column in changed
        )
        if edits:
            self._undo_stack.append(CellEditBatchCommand(edits))
            self._redo_stack.clear()
        return changed

    def batch_fill(self, cells: Iterable[tuple[int, int]], value: Any) -> tuple[tuple[int, int], ...]:
        cells_tuple = tuple(dict.fromkeys(cells))
        old_values = {cell: self.model.buffer.value_at(cell[0], cell[1]) for cell in cells_tuple}
        changed = self.model.batch_fill(cells_tuple, value)
        edits = tuple(
            CellEditCommand(
                row=row,
                column=column,
                old_value=old_values[(row, column)],
                new_value=self.model.buffer.value_at(row, column),
            )
            for row, column in changed
        )
        if edits:
            self._undo_stack.append(CellEditBatchCommand(edits))
            self._redo_stack.clear()
        return changed

    def insert_rows(self, row: int, count: int = 1) -> bool:
        if not self.model.insertRows(row, count):
            return False
        rows = tuple(deepcopy(tuple(self.model.buffer.table.rows[row : row + count])))
        self._undo_stack.append(RowEditCommand(action="insert", row=row, rows=rows))
        self._redo_stack.clear()
        return True

    def delete_rows(self, row: int, count: int = 1) -> bool:
        if row < 0 or count < 1 or row + count > self.model.buffer.row_count:
            return False
        rows = tuple(deepcopy(tuple(self.model.buffer.table.rows[row : row + count])))
        if not self.model.removeRows(row, count):
            return False
        self._undo_stack.append(RowEditCommand(action="delete", row=row, rows=rows))
        self._redo_stack.clear()
        return True

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        command = self._undo_stack[-1]
        if not self._undo_command(command):
            return False
        self._undo_stack.pop()
        self._redo_stack.append(command)
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        command = self._redo_stack[-1]
        if not self._redo_command(command):
            return False
        self._redo_stack.pop()
        self._undo_stack.append(command)
        return True

    def _undo_command(self, command: CellEditBatchCommand | RowEditCommand) -> bool:
        if isinstance(command, CellEditBatchCommand):
            return self._apply(command.edits, use_old_value=True)
        if command.action == "insert":
            return self.model.removeRows(command.row, len(command.rows))
        if command.action == "delete":
            return self.model.insert_table_rows(command.row, command.rows)
        return False

    def _redo_command(self, command: CellEditBatchCommand | RowEditCommand) -> bool:
        if isinstance(command, CellEditBatchCommand):
            return self._apply(command.edits, use_old_value=False)
        if command.action == "insert":
            return self.model.insert_table_rows(command.row, command.rows)
        if command.action == "delete":
            return self.model.removeRows(command.row, len(command.rows))
        return False

    def _apply(self, edits: Iterable[CellEditCommand], *, use_old_value: bool) -> bool:
        ordered_edits = tuple(reversed(tuple(edits))) if use_old_value else tuple(edits)
        for edit in ordered_edits:
            value = edit.old_value if use_old_value else edit.new_value
            if not self.model.setData(self.model.index(edit.row, edit.column), value, Qt.ItemDataRole.EditRole):
                return False
        return True

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent, QKeySequence
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem


class PreviewTable(QTableWidget):
    def __init__(self, *, theme: str = "light", row_count: int = 5, column_count: int = 5) -> None:
        super().__init__(row_count, column_count)
        self.setObjectName("preview-table")
        self.setProperty("theme", theme)
        self.setProperty("last-rejected-write", "")
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        headers = ["字段", "类型", "默认值", "校验", "说明"]
        if column_count > len(headers):
            headers.extend(f"列 {index + 1}" for index in range(len(headers), column_count))
        self.setHorizontalHeaderLabels(headers[:column_count])
        self.setVerticalHeaderLabels([str(index + 1) for index in range(row_count)])
        self._populate()

    def set_demo_state(self, state: str) -> None:
        self.setProperty("table-state", state)
        if state == "dirty":
            self.item(0, 3).setText("Dirty")
            self.item(0, 3).setData(Qt.ItemDataRole.UserRole, "dirty")
        elif state == "error":
            self.item(0, 3).setText("Error")
            self.item(0, 3).setData(Qt.ItemDataRole.UserRole, "error")
        elif state == "warning":
            self.item(0, 3).setText("Warning")
            self.item(0, 3).setData(Qt.ItemDataRole.UserRole, "warning")
        else:
            self.item(0, 3).setText("OK")
            self.item(0, 3).setData(Qt.ItemDataRole.UserRole, "normal")

    def _populate(self) -> None:
        rows = [
            ("item_id", "Int", "0", "OK", "主键"),
            ("display_name", "String", "-", "Readonly", "策划展示名"),
            ("quality", "Enum", "Epic", "Error", "引用 ItemQuality"),
            ("stack_count", "Int", "1", "Warning", "建议大于 0"),
            ("tags", "List<String>", "[]", "OK", "标签列表"),
        ]
        states = {
            (1, 2): "readonly",
            (2, 3): "error",
            (3, 3): "warning",
        }
        for row_index in range(self.rowCount()):
            source_row = rows[row_index % len(rows)]
            for column_index in range(self.columnCount()):
                value = source_row[column_index % len(source_row)]
                item = QTableWidgetItem(value)
                state = states.get((row_index, column_index), "normal")
                item.setData(Qt.ItemDataRole.UserRole, state)
                item.setData(Qt.ItemDataRole.UserRole + 1, state)
                if state == "readonly":
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row_index, column_index, item)

    def _can_write(self, row: int, column: int) -> bool:
        item = self.item(row, column)
        if item is None:
            return True
        return item.data(Qt.ItemDataRole.UserRole) != "readonly"

    def _write_cell(self, row: int, column: int, value: str) -> None:
        if row >= self.rowCount() or column >= self.columnCount():
            return
        if not self._can_write(row, column):
            self.setProperty("last-rejected-write", "readonly")
            return
        item = self.item(row, column) or QTableWidgetItem()
        item.setText(value)
        item.setData(Qt.ItemDataRole.UserRole, "dirty")
        self.setItem(row, column, item)

    def paste_tsv(self, text: str) -> None:
        start_row = max(self.currentRow(), 0)
        start_column = max(self.currentColumn(), 0)
        for row_offset, line in enumerate(text.splitlines()):
            for column_offset, value in enumerate(line.split("\t")):
                self._write_cell(start_row + row_offset, start_column + column_offset, value)

    def copy_selection(self) -> str:
        ranges = self.selectedRanges()
        if not ranges:
            item = self.currentItem()
            return item.text() if item is not None else ""
        cell_range = ranges[0]
        lines: list[str] = []
        for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
            values: list[str] = []
            for column in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                item = self.item(row, column)
                values.append(item.text() if item is not None else "")
            lines.append("\t".join(values))
        return "\n".join(lines)

    def batch_fill(self, value: str) -> None:
        ranges = self.selectedRanges()
        if not ranges:
            self._write_cell(max(self.currentRow(), 0), max(self.currentColumn(), 0), value)
            return
        for cell_range in ranges:
            for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
                for column in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
                    self._write_cell(row, column, value)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        clipboard = QGuiApplication.clipboard()
        if event.matches(QKeySequence.StandardKey.Paste):
            self.paste_tsv(clipboard.text())
            event.accept()
            return
        if event.matches(QKeySequence.StandardKey.Copy):
            clipboard.setText(self.copy_selection())
            event.accept()
            return
        super().keyPressEvent(event)

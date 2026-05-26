from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
)

from xtable.domain.models import FieldDefinition, FieldType, NormalTableDefinition, TableRow
from xtable.table_engine import EditCommandStack, QtTableModel, TableBuffer
from xtable.ui.icons import icon_for


class TableWorkbench(QFrame):
    def __init__(self, table: NormalTableDefinition | None = None, *, theme: str = "light") -> None:
        super().__init__()
        self.setObjectName("table-workbench")
        self.setProperty("theme", theme)
        self.buffer = TableBuffer(table or self._sample_table())
        self.model = QtTableModel(self.buffer)
        self.commands = EditCommandStack(self.model)
        self.setProperty("last-rejected-write", "")
        self.setProperty("last-batch-edit-count", 0)
        self.setProperty("scroll-position", {})
        self.setProperty("visible-range", {})
        self.setProperty("last-scroll-axis", "")
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        self.copy_button = self._tool_button("export", "复制选区", "table-workbench-copy-button")
        self.paste_button = self._tool_button("import", "粘贴", "table-workbench-paste-button")
        self.undo_button = self._tool_button("undo", "撤销", "table-workbench-undo-button")
        self.redo_button = self._tool_button("redo", "重做", "table-workbench-redo-button")
        self.add_row_button = self._tool_button("table", "插入行", "table-workbench-add-row-button")
        self.delete_row_button = self._tool_button("error", "删除行", "table-workbench-delete-row-button")
        for button in (self.copy_button, self.paste_button, self.undo_button, self.redo_button, self.add_row_button, self.delete_row_button):
            toolbar.addWidget(button)
        toolbar.addStretch()
        self.filter_input = QLineEdit()
        self.filter_input.setObjectName("table-workbench-filter-input")
        self.filter_input.setPlaceholderText("筛选")
        self.filter_input.setFixedWidth(140)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("table-workbench-search-input")
        self.search_input.setPlaceholderText("查找")
        self.search_input.setFixedWidth(140)
        self.find_button = self._tool_button("diagnostics", "查找下一个", "table-workbench-find-button")
        self.clear_filter_button = self._tool_button("error", "清除筛选", "table-workbench-clear-filter-button")
        toolbar.addWidget(self.filter_input)
        toolbar.addWidget(self.clear_filter_button)
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.find_button)
        self.sort_asc_button = self._tool_button("table", "Sort ascending", "table-workbench-sort-asc-button")
        self.sort_desc_button = self._tool_button("table", "Sort descending", "table-workbench-sort-desc-button")
        toolbar.addWidget(self.sort_asc_button)
        toolbar.addWidget(self.sort_desc_button)
        self.replace_input = QLineEdit()
        self.replace_input.setObjectName("table-workbench-replace-input")
        self.replace_input.setPlaceholderText("Replace")
        self.replace_input.setFixedWidth(140)
        self.replace_button = self._tool_button("validate", "Replace all", "table-workbench-replace-button")
        toolbar.addWidget(self.replace_input)
        toolbar.addWidget(self.replace_button)
        self.fill_input = QLineEdit()
        self.fill_input.setObjectName("table-workbench-fill-input")
        self.fill_input.setPlaceholderText("Fill")
        self.fill_input.setFixedWidth(100)
        self.fill_button = self._tool_button("validate", "Fill selection", "table-workbench-fill-button")
        toolbar.addWidget(self.fill_input)
        toolbar.addWidget(self.fill_button)
        self.edit_input = QLineEdit()
        self.edit_input.setObjectName("table-workbench-edit-input")
        self.edit_input.setPlaceholderText("Edit cell")
        self.edit_input.setFixedWidth(140)
        self.commit_edit_button = self._tool_button("validate", "提交编辑", "table-workbench-commit-edit-button")
        self.cancel_edit_button = self._tool_button("error", "取消编辑", "table-workbench-cancel-edit-button")
        toolbar.addWidget(self.edit_input)
        toolbar.addWidget(self.commit_edit_button)
        toolbar.addWidget(self.cancel_edit_button)

        self.view = QTableView()
        self.view.setObjectName("table-workbench-view")
        self.view.setModel(self.model)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view.installEventFilter(self)
        self.view.verticalScrollBar().valueChanged.connect(self.update_scroll_position)
        self.view.horizontalScrollBar().valueChanged.connect(self.update_scroll_position)
        self.visible_range_label = QLabel()
        self.visible_range_label.setObjectName("table-workbench-visible-range-label")
        self.scroll_progress_label = QLabel()
        self.scroll_progress_label.setObjectName("table-workbench-scroll-progress-label")
        self.scroll_axis_label = QLabel()
        self.scroll_axis_label.setObjectName("table-workbench-scroll-axis-label")

        self.copy_button.clicked.connect(self.copy_selection)
        self.paste_button.clicked.connect(self.paste_clipboard)
        self.undo_button.clicked.connect(self.commands.undo)
        self.redo_button.clicked.connect(self.commands.redo)
        self.add_row_button.clicked.connect(lambda: self.commands.insert_rows(max(self.view.currentIndex().row(), 0), 1))
        self.delete_row_button.clicked.connect(lambda: self.commands.delete_rows(max(self.view.currentIndex().row(), 0), 1))
        self.filter_input.textChanged.connect(self.apply_filter)
        self.clear_filter_button.clicked.connect(self.clear_filter)
        self.find_button.clicked.connect(self.find_next_match)
        self.replace_button.clicked.connect(self.replace_all_matches)
        self.fill_button.clicked.connect(self.batch_fill_selection)
        self.sort_asc_button.clicked.connect(lambda: self.sort_by_current_column(descending=False))
        self.sort_desc_button.clicked.connect(lambda: self.sort_by_current_column(descending=True))
        self.commit_edit_button.clicked.connect(self.commit_cell_edit)
        self.cancel_edit_button.clicked.connect(self.load_current_cell_for_edit)
        self.view.selectionModel().currentChanged.connect(lambda _current, _previous: self.load_current_cell_for_edit())

        layout.addLayout(toolbar)
        layout.addWidget(self.view, 1)
        layout.addWidget(self.visible_range_label)
        layout.addWidget(self.scroll_progress_label)
        layout.addWidget(self.scroll_axis_label)
        self.load_current_cell_for_edit()
        self.update_scroll_position()

    def _wire_view_signals(self) -> None:
        self.view.selectionModel().currentChanged.connect(lambda _current, _previous: self.load_current_cell_for_edit())
        self.view.verticalScrollBar().valueChanged.connect(self.update_scroll_position)
        self.view.horizontalScrollBar().valueChanged.connect(self.update_scroll_position)

    def set_table(self, table: NormalTableDefinition) -> None:
        self.buffer = TableBuffer(table)
        self.model = QtTableModel(self.buffer)
        self.commands = EditCommandStack(self.model)
        self.view.setModel(self.model)
        self._wire_view_signals()
        self.update_scroll_position()
        self.load_current_cell_for_edit()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.view and event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent):
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_End:
                self.navigate_to_table_edge(last=True)
                return True
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Home:
                self.navigate_to_table_edge(last=False)
                return True
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Right:
                self.navigate_to_row_edge(last=True)
                return True
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Left:
                self.navigate_to_row_edge(last=False)
                return True
            if event.matches(QKeySequence.StandardKey.Copy):
                self.copy_selection()
                return True
            if event.matches(QKeySequence.StandardKey.Paste):
                self.paste_clipboard()
                return True
            if event.matches(QKeySequence.StandardKey.Undo):
                self.commands.undo()
                return True
            if event.matches(QKeySequence.StandardKey.Redo):
                self.commands.redo()
                return True
        return super().eventFilter(watched, event)

    def copy_selection(self) -> None:
        selection = self.view.selectionModel().selectedIndexes()
        if not selection:
            return
        rows = [index.row() for index in selection]
        columns = [index.column() for index in selection]
        QGuiApplication.clipboard().setText(self.buffer.copy_range(min(rows), min(columns), max(rows), max(columns)))

    def paste_clipboard(self) -> None:
        index = self.view.currentIndex()
        row = max(index.row(), 0)
        column = max(index.column(), 0)
        text = QGuiApplication.clipboard().text()
        if "\t" not in text and "\n" not in text and "\r" not in text:
            if self.commands.edit_cell(row, column, text):
                self.setProperty("last-rejected-write", "")
            elif self.buffer.cell_state(row, column).kind == "readonly":
                self.setProperty("last-rejected-write", "readonly")
            return
        changed = self.commands.paste_tsv(row, column, text)
        self.setProperty("last-rejected-write", "" if changed else "rejected")

    def load_current_cell_for_edit(self) -> None:
        index = self.view.currentIndex()
        if not index.isValid():
            self.edit_input.clear()
            return
        value = self.model.data(index, Qt.ItemDataRole.EditRole)
        self.edit_input.setText("" if value is None else str(value))

    def commit_cell_edit(self) -> bool:
        index = self.view.currentIndex()
        if not index.isValid():
            return False
        if self.commands.edit_cell(index.row(), index.column(), self.edit_input.text()):
            self.setProperty("last-rejected-write", "")
            self.load_current_cell_for_edit()
            return True
        if self.buffer.cell_state(index.row(), index.column()).kind == "readonly":
            self.setProperty("last-rejected-write", "readonly")
        return False

    def apply_filter(self, text: str) -> None:
        visible_rows = set(self.buffer.filter_rows(text))
        for row in range(self.model.rowCount()):
            self.view.setRowHidden(row, bool(text) and row not in visible_rows)

    def clear_filter(self) -> None:
        self.filter_input.clear()
        self.apply_filter("")

    def find_next_match(self) -> bool:
        matches = self.buffer.find_cells(self.search_input.text())
        if not matches:
            return False
        current = self.view.currentIndex()
        current_position = (current.row(), current.column()) if current.isValid() else (-1, -1)
        target = next((match for match in matches if match > current_position), matches[0])
        target_index = self.model.index(target[0], target[1])
        self.view.setCurrentIndex(target_index)
        self.view.scrollTo(target_index)
        return True

    def replace_all_matches(self) -> tuple[tuple[int, int], ...]:
        changed = self.model.replace_all(self.search_input.text(), self.replace_input.text())
        if changed:
            first_row, first_column = changed[0]
            first_index = self.model.index(first_row, first_column)
            self.view.setCurrentIndex(first_index)
            self.view.scrollTo(first_index)
        return changed

    def batch_fill_selection(self) -> tuple[tuple[int, int], ...]:
        cells = tuple((index.row(), index.column()) for index in self.view.selectionModel().selectedIndexes())
        changed = self.commands.batch_fill(cells, self.fill_input.text())
        self.setProperty("last-batch-edit-count", len(changed))
        if changed:
            last_row, last_column = changed[-1]
            last_index = self.model.index(last_row, last_column)
            self.view.setCurrentIndex(last_index)
            self.view.scrollTo(last_index)
        return changed

    def navigate_to_table_edge(self, *, last: bool) -> bool:
        if self.model.rowCount() == 0 or self.model.columnCount() == 0:
            return False
        current = self.view.currentIndex()
        column = current.column() if current.isValid() else 0
        column = min(max(column, 0), self.model.columnCount() - 1)
        row = self.model.rowCount() - 1 if last else 0
        target_index = self.model.index(row, column)
        self.view.setCurrentIndex(target_index)
        self.view.scrollTo(target_index)
        return True

    def navigate_to_row_edge(self, *, last: bool) -> bool:
        if self.model.rowCount() == 0 or self.model.columnCount() == 0:
            return False
        current = self.view.currentIndex()
        row = current.row() if current.isValid() else 0
        row = min(max(row, 0), self.model.rowCount() - 1)
        column = self.model.columnCount() - 1 if last else 0
        target_index = self.model.index(row, column)
        self.view.setCurrentIndex(target_index)
        self.view.scrollTo(target_index)
        return True

    def update_scroll_position(self) -> None:
        vertical = self.view.verticalScrollBar()
        horizontal = self.view.horizontalScrollBar()
        previous_position = self.property("scroll-position") or {}
        scroll_position = {
            "vertical": vertical.value(),
            "horizontal": horizontal.value(),
            "vertical-maximum": vertical.maximum(),
            "horizontal-maximum": horizontal.maximum(),
        }
        changed_axes = []
        if previous_position and previous_position.get("vertical") != scroll_position["vertical"]:
            changed_axes.append("vertical")
        if previous_position and previous_position.get("horizontal") != scroll_position["horizontal"]:
            changed_axes.append("horizontal")
        if changed_axes:
            last_scroll_axis = "+".join(changed_axes)
            self.setProperty("last-scroll-axis", last_scroll_axis)
            axis_names = {"vertical": "纵向", "horizontal": "横向"}
            self.scroll_axis_label.setText(f"最近滚动：{'+'.join(axis_names[axis] for axis in changed_axes)}")
        elif not self.property("last-scroll-axis"):
            self.scroll_axis_label.setText("最近滚动：无")
        self.setProperty("scroll-position", scroll_position)
        vertical_percent = round(scroll_position["vertical"] * 100 / scroll_position["vertical-maximum"]) if scroll_position["vertical-maximum"] else 0
        horizontal_percent = round(scroll_position["horizontal"] * 100 / scroll_position["horizontal-maximum"]) if scroll_position["horizontal-maximum"] else 0
        self.scroll_progress_label.setText(f"纵向 {vertical_percent}% / 横向 {horizontal_percent}%")
        self.update_visible_range()

    def update_visible_range(self) -> None:
        viewport = self.view.viewport()
        first_row = self.view.rowAt(0)
        if first_row < 0 and self.model.rowCount() > 0:
            first_row = 0
        last_row = self.view.rowAt(max(0, viewport.height() - 1))
        if last_row < 0 and self.model.rowCount() > 0:
            last_row = self.model.rowCount() - 1

        first_column = self.view.columnAt(0)
        if first_column < 0 and self.model.columnCount() > 0:
            first_column = 0
        last_column = self.view.columnAt(max(0, viewport.width() - 1))
        if last_column < 0 and self.model.columnCount() > 0:
            last_column = self.model.columnCount() - 1

        visible_range = {
            "first-row": first_row,
            "last-row": last_row,
            "first-column": first_column,
            "last-column": last_column,
        }
        self.setProperty("visible-range", visible_range)
        self.visible_range_label.setText(
            f"行 {visible_range['first-row'] + 1}-{visible_range['last-row'] + 1} / "
            f"列 {visible_range['first-column'] + 1}-{visible_range['last-column'] + 1}"
        )

    def sort_by_current_column(self, *, descending: bool = False) -> tuple[int, ...]:
        index = self.view.currentIndex()
        column = index.column() if index.isValid() else 0
        order = self.model.sort_by_column(column, descending=descending)
        if self.model.rowCount() > 0:
            self.view.setCurrentIndex(self.model.index(0, column))
        self.clear_filter()
        return order

    def _tool_button(self, icon_id: str, tooltip: str, object_name: str) -> QToolButton:
        button = QToolButton()
        button.setObjectName(object_name)
        button.setProperty("icon-id", icon_id)
        button.setToolTip(tooltip)
        button.setIcon(icon_for(icon_id, self.property("theme") or "light"))
        return button

    def _sample_table(self) -> NormalTableDefinition:
        return NormalTableDefinition(
            table_id="items",
            display_name="Items",
            fields=[
                FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
                FieldDefinition(field_id="name", name="name", display_name="Name", field_type=FieldType.STRING),
                FieldDefinition(field_id="count", name="count", display_name="Count", field_type=FieldType.INT),
                FieldDefinition(field_id="enabled", name="enabled", display_name="Enabled", field_type=FieldType.BOOL),
            ],
            rows=[
                TableRow(values={"id": 1001, "name": "Potion", "count": 10, "enabled": True}),
                TableRow(values={"id": 1002, "name": "Elixir", "count": 2, "enabled": False}),
                TableRow(values={"id": 1003, "name": "Ether", "count": 5, "enabled": True}),
            ],
            primary_key="id",
        )


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

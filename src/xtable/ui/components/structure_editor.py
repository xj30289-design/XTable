from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from xtable.domain.models import FieldDefinition, FieldType, TableDefinition
from xtable.ui.components.buttons import IconToolButton


class StructureEditor(QFrame):
    """Table structure editor: metadata form + sortable field list with IconToolButton."""

    schema_modified = Signal(str)
    field_focused = Signal(str, str)

    def __init__(self, *, theme: str = "light") -> None:
        super().__init__()
        self.setObjectName("structure-editor")
        self.setProperty("theme", theme)
        self._table: TableDefinition | None = None
        self._suppress = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("表格参数")
        header.setObjectName("structure-editor-params-label")
        layout.addWidget(header)

        self._display_input = QLineEdit()
        self._display_input.setObjectName("structure-editor-display-name")
        self._display_input.setPlaceholderText("显示名称")
        layout.addWidget(QLabel("显示名:"))
        layout.addWidget(self._display_input)

        self._desc_input = QTextEdit()
        self._desc_input.setObjectName("structure-editor-description")
        self._desc_input.setFixedHeight(50)
        self._desc_input.setPlaceholderText("表格说明")
        layout.addWidget(QLabel("说明:"))
        layout.addWidget(self._desc_input)

        self._pk_input = QComboBox()
        self._pk_input.setObjectName("structure-editor-primary-key")
        layout.addWidget(QLabel("主键:"))
        layout.addWidget(self._pk_input)

        layout.addSpacing(6)
        layout.addWidget(QLabel("字段列表"))

        field_toolbar = QHBoxLayout()
        field_toolbar.setContentsMargins(0, 0, 0, 0)
        self._up_btn = IconToolButton("arrow-up", "上移")
        self._up_btn.setObjectName("structure-editor-up-button")
        self._down_btn = IconToolButton("arrow-down", "下移")
        self._down_btn.setObjectName("structure-editor-down-button")
        self._add_btn = IconToolButton("add", "新增字段")
        self._add_btn.setObjectName("structure-editor-add-field-button")
        self._del_btn = IconToolButton("remove", "删除选中字段")
        self._del_btn.setObjectName("structure-editor-delete-field-button")
        for btn in (self._up_btn, self._down_btn, self._add_btn, self._del_btn):
            field_toolbar.addWidget(btn)
        field_toolbar.addStretch()
        layout.addLayout(field_toolbar)

        self._field_list = QListWidget()
        self._field_list.setObjectName("structure-editor-field-list")
        self._field_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._field_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        layout.addWidget(self._field_list, 1)

        self._display_input.editingFinished.connect(self._notify_params)
        self._desc_input.textChanged.connect(self._notify_params)
        self._pk_input.currentTextChanged.connect(self._notify_params)
        self._field_list.currentItemChanged.connect(self._on_field_selected)
        self._field_list.model().rowsMoved.connect(self._on_reorder)
        self._up_btn.clicked.connect(self._move_up)
        self._down_btn.clicked.connect(self._move_down)
        self._add_btn.clicked.connect(self._add_field)
        self._del_btn.clicked.connect(self._delete_field)

        self.setEnabled(False)

    def set_table(self, table: TableDefinition | None) -> None:
        self._suppress = True
        self._table = table
        if table is None:
            self._display_input.clear()
            self._desc_input.clear()
            self._pk_input.clear()
            self._field_list.clear()
            self.setEnabled(False)
            self._suppress = False
            return
        self.setEnabled(True)
        self._display_input.setText(table.display_name)
        self._desc_input.setPlainText(table.description or "")
        self._rebuild_pk()
        self._rebuild_fields()
        self._suppress = False

    def table_id(self) -> str | None:
        return self._table.table_id if self._table else None

    def _rebuild_pk(self) -> None:
        self._pk_input.clear()
        self._pk_input.addItem("")
        for f in (self._table.fields if self._table else []):
            self._pk_input.addItem(f.field_id, f.field_id)
        if self._table and self._table.primary_key:
            idx = self._pk_input.findText(self._table.primary_key)
            if idx >= 0:
                self._pk_input.setCurrentIndex(idx)

    def _rebuild_fields(self) -> None:
        current = self._selected_field_id()
        self._field_list.blockSignals(True)
        self._field_list.clear()
        if self._table:
            for f in self._table.fields:
                item = QListWidgetItem(f"{f.name} ({f.field_type.value})")
                item.setData(Qt.ItemDataRole.UserRole, f.field_id)
                self._field_list.addItem(item)
        self._field_list.blockSignals(False)
        if current:
            self._select_field(current)

    def _selected_field_id(self) -> str:
        item = self._field_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else ""

    def _select_field(self, fid: str) -> None:
        for i in range(self._field_list.count()):
            if self._field_list.item(i).data(Qt.ItemDataRole.UserRole) == fid:
                self._field_list.setCurrentItem(self._field_list.item(i))
                return

    def _notify_params(self) -> None:
        if self._suppress or self._table is None:
            return
        self._table.display_name = self._display_input.text()
        self._table.description = self._desc_input.toPlainText()
        self._table.primary_key = self._pk_input.currentText() or ""
        self.schema_modified.emit(self._table.table_id)

    def _on_field_selected(self, current: QListWidgetItem, _prev: QListWidgetItem) -> None:
        if self._suppress or current is None or self._table is None:
            return
        self.field_focused.emit(self._table.table_id, current.data(Qt.ItemDataRole.UserRole) or "")

    def _on_reorder(self) -> None:
        if self._suppress or self._table is None:
            return
        new_order = []
        for i in range(self._field_list.count()):
            fid = self._field_list.item(i).data(Qt.ItemDataRole.UserRole)
            f = self._table.field(fid)
            if f is not None:
                new_order.append(f)
        if len(new_order) == len(self._table.fields):
            self._table.fields = new_order
            self._rebuild_pk()
            self.schema_modified.emit(self._table.table_id)

    def _move_up(self) -> None:
        self._move(-1)

    def _move_down(self) -> None:
        self._move(1)

    def _move(self, direction: int) -> None:
        if self._table is None:
            return
        i = self._field_list.currentRow()
        t = i + direction
        if i < 0 or t < 0 or t >= len(self._table.fields):
            return
        self._table.fields[i], self._table.fields[t] = self._table.fields[t], self._table.fields[i]
        self._rebuild_fields()
        self._field_list.setCurrentRow(t)
        self._rebuild_pk()
        self.schema_modified.emit(self._table.table_id)

    def _add_field(self) -> None:
        if self._table is None:
            return
        fid = f"field_{len(self._table.fields) + 1}"
        self._table.fields.append(FieldDefinition(field_id=fid, name=fid, display_name=fid, field_type=FieldType.STRING))
        self._rebuild_fields()
        self._rebuild_pk()
        self._select_field(fid)
        self.schema_modified.emit(self._table.table_id)

    def _delete_field(self) -> None:
        if self._table is None:
            return
        fid = self._selected_field_id()
        if not fid:
            return
        self._table.fields = [f for f in self._table.fields if f.field_id != fid]
        if self._table.primary_key == fid:
            self._table.primary_key = ""
        self._rebuild_fields()
        self._rebuild_pk()
        self.schema_modified.emit(self._table.table_id)

from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from xtable.domain.models import FieldDefinition, TableDefinition


class StructureEditor(QFrame):
    """Table structure editor: table metadata + sortable field list.

    Emits ``schema_modified(table_id)`` when any structure change is made.
    Emits ``field_focused(table_id, field_id)`` when a field is selected.
    """

    schema_modified = Signal(str)            # table_id
    field_focused = Signal(str, str)         # table_id, field_id

    def __init__(self, *, theme: str = "light") -> None:
        super().__init__()
        self.setObjectName("structure-editor")
        self.setProperty("theme", theme)
        self._table: TableDefinition | None = None
        self._suppress_signal = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ── Table parameters ──
        params_label = QLabel("表格参数")
        params_label.setObjectName("structure-editor-params-label")
        layout.addWidget(params_label)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(4)

        self._display_name_input = QLineEdit()
        self._display_name_input.setObjectName("structure-editor-display-name")
        self._display_name_input.setPlaceholderText("显示名称")
        form.addRow("显示名", self._display_name_input)

        self._description_input = QTextEdit()
        self._description_input.setObjectName("structure-editor-description")
        self._description_input.setFixedHeight(50)
        self._description_input.setPlaceholderText("表格说明")
        form.addRow("说明", self._description_input)

        self._primary_key_input = QComboBox()
        self._primary_key_input.setObjectName("structure-editor-primary-key")
        form.addRow("主键", self._primary_key_input)

        layout.addLayout(form)

        # ── Field list ──
        fields_label = QLabel("字段列表")
        fields_label.setObjectName("structure-editor-fields-label")
        layout.addWidget(fields_label)

        field_toolbar = QHBoxLayout()
        field_toolbar.setContentsMargins(0, 0, 0, 0)
        self._up_button = QPushButton("↑")
        self._up_button.setObjectName("structure-editor-up-button")
        self._up_button.setFixedWidth(28)
        self._up_button.setToolTip("上移")
        self._down_button = QPushButton("↓")
        self._down_button.setObjectName("structure-editor-down-button")
        self._down_button.setFixedWidth(28)
        self._down_button.setToolTip("下移")
        self._add_field_button = QPushButton("+")
        self._add_field_button.setObjectName("structure-editor-add-field-button")
        self._add_field_button.setFixedWidth(28)
        self._add_field_button.setToolTip("新增字段")
        self._delete_field_button = QPushButton("-")
        self._delete_field_button.setObjectName("structure-editor-delete-field-button")
        self._delete_field_button.setFixedWidth(28)
        self._delete_field_button.setToolTip("删除选中字段")
        field_toolbar.addWidget(self._up_button)
        field_toolbar.addWidget(self._down_button)
        field_toolbar.addWidget(self._add_field_button)
        field_toolbar.addWidget(self._delete_field_button)
        field_toolbar.addStretch()
        layout.addLayout(field_toolbar)

        self._field_list = QListWidget()
        self._field_list.setObjectName("structure-editor-field-list")
        self._field_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._field_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        layout.addWidget(self._field_list, 1)

        # ── Signals ──
        self._display_name_input.editingFinished.connect(self._on_params_changed)
        self._description_input.textChanged.connect(self._on_params_changed)
        self._primary_key_input.currentTextChanged.connect(self._on_params_changed)
        self._field_list.currentItemChanged.connect(self._on_field_selected)
        self._field_list.model().rowsMoved.connect(self._on_fields_reordered)
        self._up_button.clicked.connect(self._move_field_up)
        self._down_button.clicked.connect(self._move_field_down)
        self._add_field_button.clicked.connect(self._add_field)
        self._delete_field_button.clicked.connect(self._delete_field)

    def set_table(self, table: TableDefinition | None) -> None:
        self._suppress_signal = True
        self._table = table
        if table is None:
            self._display_name_input.clear()
            self._description_input.clear()
            self._primary_key_input.clear()
            self._field_list.clear()
            self.setEnabled(False)
            self._suppress_signal = False
            return

        self.setEnabled(True)
        self._display_name_input.setText(table.display_name)
        self._description_input.setPlainText(table.description or "")
        self._rebuild_primary_key()
        self._rebuild_field_list()
        self._suppress_signal = False

    def table_id(self) -> str | None:
        return self._table.table_id if self._table else None

    # ── Internal helpers ──

    def _rebuild_primary_key(self) -> None:
        if self._table is None:
            return
        current = self._primary_key_input.currentText()
        self._primary_key_input.clear()
        self._primary_key_input.addItem("")
        for field in self._table.fields:
            self._primary_key_input.addItem(field.field_id, field.field_id)
        if current:
            idx = self._primary_key_input.findText(current)
            if idx >= 0:
                self._primary_key_input.setCurrentIndex(idx)

    def _rebuild_field_list(self) -> None:
        if self._table is None:
            return
        current_id = self._selected_field_id()
        self._field_list.blockSignals(True)
        self._field_list.clear()
        for field in self._table.fields:
            item = QListWidgetItem(f"{field.name} ({field.field_type.value})")
            item.setData(Qt.ItemDataRole.UserRole, field.field_id)
            self._field_list.addItem(item)
        self._field_list.blockSignals(False)
        if current_id:
            self._set_field_selection(current_id)

    def _selected_field_id(self) -> str:
        item = self._field_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) or "" if item else ""

    def _set_field_selection(self, field_id: str) -> None:
        for i in range(self._field_list.count()):
            item = self._field_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == field_id:
                self._field_list.setCurrentItem(item)
                return

    # ── Handlers ──

    def _on_params_changed(self) -> None:
        if self._suppress_signal or self._table is None:
            return
        table = self._table
        new_pk = self._primary_key_input.currentText() or ""
        table.display_name = self._display_name_input.text()
        table.description = self._description_input.toPlainText()
        table.primary_key = new_pk
        self.schema_modified.emit(table.table_id)

    def _on_field_selected(self, current: QListWidgetItem, _previous: QListWidgetItem) -> None:
        if self._suppress_signal or current is None or self._table is None:
            return
        field_id = current.data(Qt.ItemDataRole.UserRole) or ""
        self.field_focused.emit(self._table.table_id, field_id)

    def _on_fields_reordered(self) -> None:
        if self._suppress_signal or self._table is None:
            return
        new_order: list[FieldDefinition] = []
        for i in range(self._field_list.count()):
            item = self._field_list.item(i)
            if item is None:
                continue
            fid = item.data(Qt.ItemDataRole.UserRole) or ""
            field = self._table.field(fid)
            if field is not None:
                new_order.append(field)
        if len(new_order) == len(self._table.fields):
            self._table.fields = new_order
            self._rebuild_primary_key()
            self.schema_modified.emit(self._table.table_id)

    def _move_field_up(self) -> None:
        self._move_field(-1)

    def _move_field_down(self) -> None:
        self._move_field(1)

    def _move_field(self, direction: int) -> None:
        if self._table is None:
            return
        idx = self._field_list.currentRow()
        target = idx + direction
        if idx < 0 or target < 0 or target >= len(self._table.fields):
            return
        self._table.fields[idx], self._table.fields[target] = (
            self._table.fields[target],
            self._table.fields[idx],
        )
        self._rebuild_field_list()
        self._field_list.setCurrentRow(target)
        self._rebuild_primary_key()
        self.schema_modified.emit(self._table.table_id)

    def _add_field(self) -> None:
        if self._table is None:
            return
        from xtable.domain.models import FieldType

        field_id = f"field_{len(self._table.fields) + 1}"
        new_field = FieldDefinition(
            field_id=field_id,
            name=field_id,
            display_name=field_id,
            field_type=FieldType.STRING,
        )
        self._table.fields.append(new_field)
        self._rebuild_field_list()
        self._rebuild_primary_key()
        self._set_field_selection(field_id)
        self.schema_modified.emit(self._table.table_id)

    def _delete_field(self) -> None:
        if self._table is None:
            return
        field_id = self._selected_field_id()
        if not field_id:
            return
        self._table.fields = [f for f in self._table.fields if f.field_id != field_id]
        if self._table.primary_key == field_id:
            self._table.primary_key = ""
        self._rebuild_field_list()
        self._rebuild_primary_key()
        self.schema_modified.emit(self._table.table_id)

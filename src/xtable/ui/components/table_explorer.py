from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from xtable.domain.models import FieldDefinition, FieldType, NormalTableDefinition, ProjectSchema
from xtable.ui.components.buttons import IconToolButton
from xtable.ui.dialogs import ConfirmDialog


class TableExplorer(QFrame):
    """Table list panel with add/delete controls using IconToolButton."""

    table_selected = Signal(str)
    table_added = Signal(str)
    table_deleted = Signal(str)

    def __init__(self, *, theme: str = "light") -> None:
        super().__init__()
        self.setObjectName("table-explorer")
        self.setProperty("theme", theme)
        self._schema: ProjectSchema | None = None
        self._selected_table_id: str = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        header = QLabel("表格")
        header.setObjectName("table-explorer-header")
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        self._add_btn = IconToolButton("add", "新建表格")
        self._add_btn.setObjectName("table-explorer-add-button")
        self._del_btn = IconToolButton("remove", "删除选中表格")
        self._del_btn.setObjectName("table-explorer-delete-button")
        toolbar.addWidget(self._add_btn)
        toolbar.addWidget(self._del_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self._list = QListWidget()
        self._list.setObjectName("table-explorer-list")
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self._list, 1)

        self._list.currentItemChanged.connect(self._on_current_changed)
        self._add_btn.clicked.connect(self._on_add)
        self._del_btn.clicked.connect(self._on_delete)

    def load_schema(self, schema: ProjectSchema) -> None:
        self._schema = schema
        self._populate()

    def set_selected(self, table_id: str) -> None:
        self._selected_table_id = table_id
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == table_id:
                self._list.setCurrentItem(item)
                return

    def current_table_id(self) -> str | None:
        item = self._list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _populate(self) -> None:
        self._list.blockSignals(True)
        self._list.clear()
        if self._schema:
            for table in self._schema.tables.values():
                item = QListWidgetItem(table.display_name or table.table_id)
                item.setData(Qt.ItemDataRole.UserRole, table.table_id)
                item.setToolTip(f"{table.table_id} ({table.table_type.value})")
                self._list.addItem(item)
        self._list.blockSignals(False)
        if self._selected_table_id:
            self.set_selected(self._selected_table_id)

    def _on_current_changed(self, current: QListWidgetItem, _previous: QListWidgetItem) -> None:
        if current is None:
            return
        tid = current.data(Qt.ItemDataRole.UserRole) or ""
        self._selected_table_id = tid
        self.table_selected.emit(tid)

    def _on_add(self) -> None:
        table_id, ok = QInputDialog.getText(self, "新建表格", "表格 ID:")
        if not ok or not table_id:
            return
        display_name, ok = QInputDialog.getText(self, "新建表格", "显示名称:", text=table_id)
        if not ok:
            return
        if self._schema is None:
            return
        new_table = NormalTableDefinition(
            table_id=table_id,
            display_name=display_name or table_id,
            fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True)],
            rows=[],
            primary_key="id",
        )
        self._schema.tables[table_id] = new_table
        self._populate()
        self.set_selected(table_id)
        self.table_added.emit(table_id)

    def _on_delete(self) -> None:
        tid = self.current_table_id()
        if not tid or self._schema is None:
            return
        table = self._schema.tables.get(tid)
        if table is None:
            return
        impact = self._schema.deletion_impact("table", tid)
        if impact.references:
            parent = self.window() if self.window() else self
            dialog = ConfirmDialog(
                parent=parent,
                title="删除表格",
                message=f"确定删除 {table.display_name}？\n该表格被 {len(impact.references)} 处引用。",
                confirm_text="删除",
            )
            if not dialog.exec():
                return
        del self._schema.tables[tid]
        self._populate()
        self.table_deleted.emit(tid)
        if self._list.count() > 0:
            self._list.setCurrentRow(0)

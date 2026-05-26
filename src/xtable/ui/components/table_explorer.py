from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from xtable.domain.models import ProjectSchema, TableDefinition


class TableExplorer(QFrame):
    """List of all tables in the current project schema with add/delete controls."""

    table_selected = Signal(str)  # table_id
    table_added = Signal(str)  # table_id
    table_deleted = Signal(str)  # table_id

    def __init__(self, *, theme: str = "light") -> None:
        super().__init__()
        self.setObjectName("table-explorer")
        self.setProperty("theme", theme)
        self._schema: ProjectSchema | None = None
        self._selected_table_id: str = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Header
        header = QLabel("表格")
        header.setObjectName("table-explorer-header")
        layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        self._add_button = QPushButton("+")
        self._add_button.setObjectName("table-explorer-add-button")
        self._add_button.setFixedWidth(28)
        self._add_button.setToolTip("新建表格")
        self._delete_button = QPushButton("-")
        self._delete_button.setObjectName("table-explorer-delete-button")
        self._delete_button.setFixedWidth(28)
        self._delete_button.setToolTip("删除选中表格")
        toolbar.addWidget(self._add_button)
        toolbar.addWidget(self._delete_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table list
        self._list = QListWidget()
        self._list.setObjectName("table-explorer-list")
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self._list, 1)

        # Signals
        self._list.currentItemChanged.connect(self._on_current_changed)
        self._add_button.clicked.connect(self._on_add)
        self._delete_button.clicked.connect(self._on_delete)

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
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole) or None

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

        # Restore selection
        if self._selected_table_id:
            self.set_selected(self._selected_table_id)

    def _on_current_changed(self, current: QListWidgetItem, _previous: QListWidgetItem) -> None:
        if current is None:
            return
        table_id = current.data(Qt.ItemDataRole.UserRole) or ""
        self._selected_table_id = table_id
        self.table_selected.emit(table_id)

    def _on_add(self) -> None:
        from PySide6.QtWidgets import QInputDialog

        table_id, ok = QInputDialog.getText(self, "新建表格", "表格 ID:")
        if not ok or not table_id:
            return
        display_name, ok = QInputDialog.getText(self, "新建表格", "显示名称:", text=table_id)
        if not ok:
            return

        from xtable.domain.models import (
            FieldDefinition,
            FieldType,
            NormalTableDefinition,
            TableRow,
        )

        new_table = NormalTableDefinition(
            table_id=table_id,
            display_name=display_name or table_id,
            fields=[
                FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
            ],
            rows=[],
            primary_key="id",
        )
        if self._schema is not None:
            self._schema.tables[table_id] = new_table
            self._populate()
            self.set_selected(table_id)
            self.table_added.emit(table_id)

    def _on_delete(self) -> None:
        table_id = self.current_table_id()
        if not table_id or self._schema is None:
            return
        table = self._schema.tables.get(table_id)
        if table is None:
            return

        impact = self._schema.deletion_impact("table", table_id)
        if impact.blocked or impact.references:
            from xtable.ui.dialogs import ConfirmDialog

            parent = self.window() if self.window() else self
            detail = f"该表格被 {len(impact.references)} 处引用" if impact.references else ""
            dialog = ConfirmDialog(
                parent=parent,
                title="删除表格",
                message=f"确定删除表格 {table.display_name}？{detail}",
                confirm_text="删除",
            )
            if not dialog.exec():
                return

        del self._schema.tables[table_id]
        self._populate()
        self.table_deleted.emit(table_id)

        # If the deleted table was selected, pick another one
        current = self.current_table_id()
        if current is None:
            self._list.setCurrentRow(0 if self._list.count() > 0 else -1)

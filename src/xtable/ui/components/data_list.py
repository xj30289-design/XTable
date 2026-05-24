from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QListWidget, QListWidgetItem

DataListItem = tuple[str, str, str, str]


class DataListView(QListWidget):
    def __init__(self, items: Sequence[DataListItem]) -> None:
        super().__init__()
        self.setObjectName("data-list-view")
        self.source_items = list(items)
        self.filter_input = QLineEdit(self)
        self.filter_input.setObjectName("data-list-filter")
        self.filter_input.setPlaceholderText("筛选")
        self.filter_input.textChanged.connect(self.apply_filter)
        self.setViewportMargins(0, 30, 0, 0)
        self.apply_filter("")

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        self.filter_input.setGeometry(4, 4, max(self.width() - 8, 0), 24)

    def apply_filter(self, text: str) -> None:
        self.clear()
        lowered = text.lower()
        for key, title, kind, state in self.source_items:
            if lowered and lowered not in key.lower() and lowered not in title.lower():
                continue
            item = QListWidgetItem(f"{title} · {kind} · {state}")
            item.setData(Qt.ItemDataRole.UserRole, key)
            item.setData(Qt.ItemDataRole.UserRole + 1, state)
            self.addItem(item)
        self.setProperty("list-state", "empty" if self.count() == 0 else "ready")

    def set_loading(self, loading: bool) -> None:
        self.setProperty("list-state", "loading" if loading else "ready")

    def set_empty(self) -> None:
        self.clear()
        self.setProperty("list-state", "empty")

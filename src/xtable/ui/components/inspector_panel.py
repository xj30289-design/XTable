from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QStackedWidget, QVBoxLayout

from xtable.domain.models import FieldDefinition
from xtable.ui.components.inspector import FieldInspector


class InspectorPanel(QFrame):
    """Global right-side properties panel, similar to Unity Inspector.

    Shows FieldInspector when a field is selected. Shows empty state otherwise.
    """

    EMPTY_LABEL = "选择对象以查看属性"

    def __init__(self, *, theme: str = "light") -> None:
        super().__init__()
        self.setObjectName("inspector-panel")
        self.setProperty("theme", theme)
        self.setVisible(False)
        self.setMinimumWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._title = QLabel("属性")
        self._title.setObjectName("inspector-panel-title")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setFixedHeight(32)
        layout.addWidget(self._title)

        self._stack = QStackedWidget()
        self._stack.setObjectName("inspector-panel-stack")
        layout.addWidget(self._stack, 1)

        self._empty_page = QLabel(self.EMPTY_LABEL)
        self._empty_page.setObjectName("inspector-panel-empty")
        self._empty_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_page.setWordWrap(True)
        self._stack.addWidget(self._empty_page)

        self._field_inspector = FieldInspector(theme=theme)
        self._field_inspector.setObjectName("inspector-field-editor")
        self._stack.addWidget(self._field_inspector)

        self._stack.setCurrentIndex(0)

    @property
    def field_inspector(self) -> FieldInspector:
        return self._field_inspector

    def show_field(self, table_id: str, field: FieldDefinition) -> None:
        self._field_inspector.set_field(field, table_id=table_id)
        self._title.setText(f"字段: {field.display_name or field.name}")
        self._stack.setCurrentIndex(1)

    def clear(self) -> None:
        self._field_inspector.clear()
        self._title.setText("属性")
        self._stack.setCurrentIndex(0)
        self.setVisible(False)

    def has_content(self) -> bool:
        return self._stack.currentIndex() > 0

    def apply_theme(self, theme: str) -> None:
        self.setProperty("theme", theme)
        self._field_inspector.setProperty("theme", theme)

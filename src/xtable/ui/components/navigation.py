from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout

from xtable.ui.icons import icon_for

NavItem = tuple[str, str, str]


class NavigationRail(QFrame):
    def __init__(
        self,
        items: Sequence[NavItem],
        *,
        on_select: Callable[[str], None],
        theme: str = "light",
    ) -> None:
        super().__init__()
        self.items = list(items)
        self.on_select = on_select
        self.buttons: dict[str, QToolButton] = {}
        self.setObjectName("navigation-rail")
        self.setFixedWidth(56)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        for index, (key, title, icon_id) in enumerate(self.items):
            button = QToolButton()
            button.setObjectName(f"nav-{key}")
            button.setProperty("icon-id", icon_id)
            button.setToolTip(title)
            button.setAccessibleName(title)
            button.setCheckable(True)
            button.setFixedSize(42, 40)
            button.setIconSize(QSize(24, 24))
            button.clicked.connect(lambda checked=False, page_key=key: self.select(page_key))
            layout.addWidget(button)
            self.buttons[key] = button
            if index == 0:
                button.setChecked(True)

        layout.addStretch()
        self.apply_theme(theme)

    def button_for(self, key: str) -> QToolButton:
        return self.buttons[key]

    def select(self, key: str) -> None:
        for page_key, button in self.buttons.items():
            button.setChecked(page_key == key)
        self.on_select(key)

    def apply_theme(self, theme: str) -> None:
        for button in self.buttons.values():
            button.setIcon(icon_for(button.property("icon-id"), theme))

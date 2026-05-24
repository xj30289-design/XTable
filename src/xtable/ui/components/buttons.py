from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolButton

from xtable.ui.icons import icon_for


class IconToolButton(QToolButton):
    def __init__(self, icon_id: str, tooltip: str, *, theme: str = "light", size: int = 20) -> None:
        super().__init__()
        self.icon_id = icon_id
        self.setObjectName(f"icon-tool-button-{icon_id}")
        self.setProperty("icon-id", icon_id)
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip)
        self.setText("")
        self.setIconSize(QSize(size, size))
        self.apply_theme(theme)

    def apply_theme(self, theme: str) -> None:
        self.setProperty("theme", theme)
        self.setIcon(icon_for(self.icon_id, theme))

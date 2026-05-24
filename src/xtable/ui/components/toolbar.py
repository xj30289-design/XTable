from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QSizePolicy, QToolBar, QWidget

from xtable.ui.icons import icon_for

ActionGroup = tuple[str, Sequence[QAction]]


class EditorToolbar(QToolBar):
    def __init__(self, groups: Sequence[ActionGroup], *, theme: str = "light") -> None:
        super().__init__("Editor")
        self.groups = list(groups)
        self.setObjectName("editor-toolbar")
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._build(theme)

    def _build(self, theme: str) -> None:
        first_group = True
        spacer_added = False
        for group_name, actions in self.groups:
            if group_name == "global" and not spacer_added:
                spacer = QWidget()
                spacer.setObjectName("toolbar-right-spacer")
                spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.addWidget(spacer)
                spacer_added = True
            elif not first_group:
                self.addSeparator()

            for action in actions:
                icon_id = action.property("icon-id")
                if icon_id:
                    action.setIcon(icon_for(icon_id, theme))
                self.addAction(action)
            first_group = False

    def apply_theme(self, theme: str) -> None:
        for action in self.actions():
            icon_id = action.property("icon-id")
            if icon_id:
                action.setIcon(icon_for(icon_id, theme))

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from xtable.ui.icons import icon_for
from xtable.ui.theme import build_stylesheet


class MessageDialog(QDialog):
    def __init__(
        self,
        title: str,
        message: str,
        *,
        kind: str = "info",
        theme: str = "light",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("xtable-message-dialog")
        self.setProperty("dialog-kind", kind)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet(build_stylesheet(theme))

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(20, 18, 20, 18)
        root_layout.setSpacing(14)

        icon_frame = QFrame()
        icon_frame.setObjectName("message-dialog-icon-frame")
        icon_frame.setFixedSize(38, 38)
        icon_layout = QHBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel()
        icon_label.setObjectName("message-dialog-icon")
        icon_label.setProperty("icon-id", kind)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setPixmap(icon_for(kind, theme).pixmap(QSize(20, 20)))
        icon_layout.addWidget(icon_label)
        root_layout.addWidget(icon_frame, 0, Qt.AlignmentFlag.AlignTop)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("message-dialog-title")
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)

        body_label = QLabel(message)
        body_label.setObjectName("message-dialog-body")
        body_label.setWordWrap(True)
        body_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_layout.addWidget(body_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.setObjectName("message-dialog-buttons")
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button is not None:
            ok_button.setObjectName("message-dialog-primary-button")
            ok_button.setText("确定")
        buttons.accepted.connect(self.accept)
        content_layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)

        root_layout.addLayout(content_layout, 1)

    @classmethod
    def error(
        cls,
        title: str,
        message: str,
        *,
        theme: str = "light",
        parent: QWidget | None = None,
    ) -> "MessageDialog":
        return cls(title, message, kind="error", theme=theme, parent=parent)


class ConfirmDialog(MessageDialog):
    def __init__(
        self,
        title: str,
        message: str,
        *,
        theme: str = "light",
        parent: QWidget | None = None,
    ) -> None:
        QDialog.__init__(self, parent)
        self.setObjectName("xtable-confirm-dialog")
        self.setProperty("dialog-kind", "confirm")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet(build_stylesheet(theme))

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(20, 18, 20, 18)
        root_layout.setSpacing(14)

        icon_frame = QFrame()
        icon_frame.setObjectName("message-dialog-icon-frame")
        icon_frame.setFixedSize(38, 38)
        icon_layout = QHBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel()
        icon_label.setObjectName("message-dialog-icon")
        icon_label.setProperty("icon-id", "info")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setPixmap(icon_for("info", theme).pixmap(QSize(20, 20)))
        icon_layout.addWidget(icon_label)
        root_layout.addWidget(icon_frame, 0, Qt.AlignmentFlag.AlignTop)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("message-dialog-title")
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)

        body_label = QLabel(message)
        body_label.setObjectName("message-dialog-body")
        body_label.setWordWrap(True)
        body_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_layout.addWidget(body_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.setObjectName("confirm-dialog-buttons")
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_button is not None:
            ok_button.setText("确认")
        if cancel_button is not None:
            cancel_button.setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        content_layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)

        root_layout.addLayout(content_layout, 1)


class ProjectDialogs:
    def get_project_create_options(self, parent: QWidget) -> dict[str, object] | None:
        directory = QFileDialog.getExistingDirectory(parent, "选择项目目录")
        if not directory:
            return None
        default_name = Path(directory).name or "XTableProject"
        name, accepted = QInputDialog.getText(
            parent,
            "新建项目",
            "项目名",
            text=default_name,
        )
        if not accepted or not name.strip():
            return None
        operator, accepted = QInputDialog.getText(
            parent,
            "新建项目",
            "操作者",
            text="",
        )
        if not accepted:
            return None
        return {
            "root": Path(directory),
            "name": name.strip(),
            "operator": operator.strip(),
        }

    def get_existing_project_root(self, parent: QWidget) -> Path | None:
        directory = QFileDialog.getExistingDirectory(parent, "打开项目目录")
        return Path(directory) if directory else None

    def create_error_dialog(
        self,
        parent: QWidget | None,
        title: str,
        message: str,
        *,
        theme: str | None = None,
    ) -> MessageDialog:
        resolved_theme = theme or _theme_from_parent(parent)
        return MessageDialog.error(title, message, theme=resolved_theme, parent=parent)

    def show_error(self, parent: QWidget, title: str, message: str) -> None:
        self.create_error_dialog(parent, title, message).exec()


def _theme_from_parent(parent: QWidget | None) -> str:
    if parent is None:
        return "light"
    theme = parent.property("theme")
    return theme if theme in {"light", "dark"} else "light"

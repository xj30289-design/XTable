from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QStatusBar, QToolButton, QWidget

from xtable.ui.icons import icon_for


STATUS_FIELDS = (
    ("status-project", "项目", "未打开"),
    ("status-object", "当前对象", "-"),
    ("status-save", "保存状态", "未保存"),
    ("status-validation", "校验状态", "未运行"),
    ("status-task", "后台任务", "空闲"),
    ("status-issues", "错误/警告", "0/0"),
)


def _make_group(object_name: str) -> QWidget:
    group = QWidget()
    group.setObjectName(object_name)
    layout = QHBoxLayout(group)
    layout.setContentsMargins(8, 0, 8, 0)
    layout.setSpacing(10)
    return group


def _group_layout(group: QWidget) -> QHBoxLayout:
    layout = group.layout()
    assert isinstance(layout, QHBoxLayout)
    return layout


def _make_separator() -> QFrame:
    separator = QFrame()
    separator.setObjectName("status-separator")
    separator.setFrameShape(QFrame.Shape.VLine)
    separator.setFrameShadow(QFrame.Shadow.Plain)
    return separator


class IssueSummaryWidget(QToolButton):
    def __init__(self, on_click: Callable[[], None]) -> None:
        super().__init__()
        self.setObjectName("status-issue-summary")
        self.setProperty("summary-kind", "issue-summary")
        self.setIconSize(QSize(16, 16))
        self.clicked.connect(on_click)
        self.update_summary(0, 0, 0, "light")

    def update_summary(self, errors: int, warnings: int, infos: int, theme: str) -> None:
        icon_id = "error" if errors else "warn" if warnings else "ok"
        self.setProperty("icon-id", icon_id)
        self.setIcon(icon_for(icon_id, theme))
        self.setText(f"{errors} / {warnings}")
        self.setToolTip(f"Error: {errors} / Warn: {warnings} / Info: {infos}")


class IssueStatusButton(QToolButton):
    def __init__(self, on_click: Callable[[], None]) -> None:
        super().__init__()
        self.setObjectName("status-issue-button")
        self.setToolTip("Error: 0 / Warn: 0 / Info: 0")
        self.setIconSize(QSize(16, 16))
        self.clicked.connect(on_click)
        self.update_summary(0, 0, 0, "light")

    def update_summary(self, errors: int, warnings: int, infos: int, theme: str) -> None:
        if errors:
            icon_id = "error"
            count = errors
        elif warnings:
            icon_id = "warn"
            count = warnings
        elif infos:
            icon_id = "info"
            count = infos
        else:
            icon_id = "ok"
            count = 0
        self.setProperty("icon-id", icon_id)
        self.setIcon(icon_for(icon_id, theme))
        self.setText(str(count))
        self.setToolTip(f"Error: {errors} / Warn: {warnings} / Info: {infos}")


class EditorStatusBar(QStatusBar):
    def __init__(self, on_issue_clicked: Callable[[], None]) -> None:
        super().__init__()
        self.setObjectName("status-bar")
        self.fields: dict[str, QLabel] = {}
        self.setContentsMargins(4, 0, 4, 0)
        root_layout = self.layout()
        if isinstance(root_layout, QHBoxLayout):
            root_layout.setSpacing(10)

        self.left_group = _make_group("status-left-group")
        self.context_group = _make_group("status-context-group")
        self.state_group = _make_group("status-state-group")

        self.issue_summary = IssueSummaryWidget(on_issue_clicked)
        _group_layout(self.left_group).addWidget(self.issue_summary)
        self.addWidget(self.left_group)
        self.addWidget(_make_separator())

        for object_name, tooltip, text in STATUS_FIELDS:
            label = QLabel(text)
            label.setObjectName(object_name)
            label.setToolTip(tooltip)
            label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
            self.fields[object_name] = label
            if object_name in {"status-project", "status-object"}:
                _group_layout(self.context_group).addWidget(label)
            else:
                _group_layout(self.state_group).addWidget(label)
        self.addWidget(self.context_group)
        self.addPermanentWidget(self.state_group)
        self.issue_button = IssueStatusButton(on_issue_clicked)
        root_layout = self.layout()
        if isinstance(root_layout, QHBoxLayout):
            root_layout.setSpacing(10)

    def set_project(self, name: str) -> None:
        self.fields["status-project"].setText(name)
        self.fields["status-save"].setText("已保存")

    def set_object(self, name: str) -> None:
        self.fields["status-object"].setText(name)

    def update_issue_summary(self, errors: int, warnings: int, infos: int, theme: str) -> None:
        self.fields["status-issues"].setText(f"{errors}/{warnings}")
        self.issue_summary.update_summary(errors, warnings, infos, theme)
        self.issue_button.update_summary(errors, warnings, infos, theme)

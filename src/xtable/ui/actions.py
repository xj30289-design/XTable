from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

from xtable.ui.icons import icon_for


@dataclass(frozen=True)
class ActionSpec:
    action_id: str
    icon_id: str
    menu: str
    label: str
    tooltip: str
    shortcut: str = ""
    toolbar: bool = True
    toolbar_group: str = ""


ACTION_SPECS = (
    ActionSpec("action-new-project", "project-new", "文件", "新建项目", "新建项目", "Ctrl+N"),
    ActionSpec("action-open-project", "project-open", "文件", "打开项目", "打开项目", "Ctrl+O"),
    ActionSpec("action-save-project", "project-save", "文件", "保存项目", "保存项目", "Ctrl+S"),
    ActionSpec("action-import", "import", "文件", "导入", "导入数据", toolbar=True),
    ActionSpec("action-export", "export", "文件", "导出", "导出数据", toolbar=True),
    ActionSpec("action-exit", "diagnostics", "文件", "退出", "退出编辑器", toolbar=False),
    ActionSpec("action-undo", "undo", "编辑", "撤销", "撤销", "Ctrl+Z"),
    ActionSpec("action-redo", "redo", "编辑", "重做", "重做", "Ctrl+Y"),
    ActionSpec("action-find", "diagnostics", "编辑", "查找", "查找", "Ctrl+F", toolbar=False),
    ActionSpec("action-replace", "diagnostics", "编辑", "替换", "替换", "Ctrl+H", toolbar=False),
    ActionSpec("action-toggle-theme", "theme", "查看", "切换主题", "切换深浅主题"),
    ActionSpec("action-toggle-issues", "issues", "查看", "问题面板", "展开或收起问题报告"),
    ActionSpec("action-validate", "validate", "查看", "校验", "校验当前项目"),
    ActionSpec("action-reset-layout", "diagnostics", "查看", "重置布局", "重置布局", toolbar=False),
    ActionSpec("action-fullscreen", "diagnostics", "窗口", "全屏", "切换全屏", toolbar=False),
    ActionSpec("action-about", "info", "帮助", "关于", "关于 XTable", toolbar=False),
    ActionSpec("action-diagnostics", "diagnostics", "帮助", "诊断信息", "复制诊断信息", toolbar=False),
    ActionSpec("action-open-ui-kit-demo", "diagnostics", "帮助", "UI Kit Demo", "打开 UI Kit Demo", toolbar=False),
)


def create_actions(parent: QWidget, handlers: dict[str, Callable[[], None]]) -> dict[str, QAction]:
    actions: dict[str, QAction] = {}
    for spec in ACTION_SPECS:
        action = QAction(icon_for(spec.icon_id), spec.label, parent)
        action.setObjectName(spec.action_id)
        action.setProperty("icon-id", spec.icon_id)
        action.setToolTip(spec.tooltip)
        if spec.shortcut:
            action.setShortcut(spec.shortcut)
        if spec.action_id in handlers:
            action.triggered.connect(handlers[spec.action_id])
        actions[spec.action_id] = action
    return actions

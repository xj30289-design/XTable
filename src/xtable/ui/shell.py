from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from xtable.ui.actions import ACTION_SPECS, create_actions
from xtable.ui.components import EditorToolbar, NavigationRail
from xtable.ui.focus import EditorFocusManager, install_editor_focus_management
from xtable.ui.icons import icon_for
from xtable.ui.issue_drawer import IssueDrawer
from xtable.ui.status_bar import EditorStatusBar
from xtable.ui.theme import build_stylesheet

PageSpec = tuple[str, str, str, QWidget]


class EditorShell(QMainWindow):
    def __init__(
        self,
        *,
        title: str,
        pages: Sequence[PageSpec],
        handlers: dict[str, Callable[[], None]] | None = None,
        object_name: str = "editor-shell-window",
    ) -> None:
        super().__init__()
        self.pages_by_key: dict[str, QWidget] = {}
        self.issue_counts = (0, 0, 0)
        self.focus_manager = EditorFocusManager()
        self.setObjectName(object_name)
        self.setWindowTitle(title)
        self.resize(1200, 760)
        base_handlers = {
            "action-toggle-theme": self.toggle_theme,
            "action-toggle-issues": lambda: self.open_diagnostics("issues"),
            "action-diagnostics": lambda: self.open_diagnostics("logs"),
        }
        if handlers:
            base_handlers.update(handlers)
        self.actions = create_actions(self, base_handlers)
        self._build_menu_bar()
        self._build_toolbar()
        self._build_status_bar()
        self._build_workspace(pages)
        self.editor_focus_filter = install_editor_focus_management(self, self.focus_manager)
        self.apply_theme("light")

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        menu_bar.setObjectName("main-menu-bar")
        menus = {name: menu_bar.addMenu(name) for name in ("文件", "编辑", "查看", "窗口", "帮助")}
        for spec in ACTION_SPECS:
            menus[spec.menu].addAction(self.actions[spec.action_id])

    def _build_toolbar(self) -> None:
        groups: list[tuple[str, list[QAction]]] = [
            (
                "project",
                [
                    self.actions["action-new-project"],
                    self.actions["action-open-project"],
                    self.actions["action-save-project"],
                ],
            ),
            ("io", [self.actions["action-import"], self.actions["action-export"]]),
            ("edit", [self.actions["action-undo"], self.actions["action-redo"]]),
            ("validate", [self.actions["action-validate"]]),
            ("global", [self.actions["action-toggle-theme"], self.actions["action-diagnostics"]]),
        ]
        self.toolbar = EditorToolbar(groups, theme=self.property("theme") or "light")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

    def _build_status_bar(self) -> None:
        status_bar = EditorStatusBar(lambda: self.open_diagnostics("issues"))
        self.status_fields = status_bar.fields
        self.setStatusBar(status_bar)

    def _build_workspace(self, pages: Sequence[PageSpec]) -> None:
        root = QWidget()
        root.setObjectName("main-workspace")
        outer_layout = QVBoxLayout(root)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setObjectName("main-vertical-splitter")

        work_area = QWidget()
        work_area.setObjectName("work-area")
        work_layout = QHBoxLayout(work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        work_layout.setSpacing(0)

        nav_items = [(key, title, icon_id) for key, title, icon_id, _ in pages]
        self.navigation = NavigationRail(nav_items, on_select=self.show_page)
        self.workspace_pages = QStackedWidget()
        self.workspace_pages.setObjectName("workspace-pages")
        for key, _title, _icon_id, page in pages:
            page.setObjectName(f"page-{key}")
            self.pages_by_key[key] = page
            self.workspace_pages.addWidget(page)

        work_layout.addWidget(self.navigation)
        work_layout.addWidget(self.workspace_pages, 1)

        self.issue_drawer = IssueDrawer()
        self.main_splitter.addWidget(work_area)
        self.main_splitter.addWidget(self.issue_drawer)
        self.issue_drawer.setMinimumHeight(160)
        self.issue_drawer.setMaximumHeight(380)
        self.main_splitter.setSizes([600, 220])

        outer_layout.addWidget(self.main_splitter, 1)
        self.setCentralWidget(root)
        if pages:
            self.show_page(pages[0][0])

    def show_page(self, key: str) -> None:
        page = self.pages_by_key.get(key)
        if page is None:
            return
        self.focus_manager.deactivate_active(reason="page-switch")
        self.clearFocus()
        self.workspace_pages.setCurrentWidget(page)
        self.navigation.select(key) if not self.navigation.button_for(key).isChecked() else None
        self.statusBar().set_object(key)

    def apply_theme(self, theme: str) -> None:
        self.setProperty("theme", theme)
        self.setStyleSheet(build_stylesheet(theme))
        for spec in ACTION_SPECS:
            action = self.actions.get(spec.action_id)
            if action is not None:
                action.setIcon(icon_for(spec.icon_id, theme))
        self.toolbar.apply_theme(theme)
        self.navigation.apply_theme(theme)
        self.update_issue_summary(*self.issue_counts)

    def toggle_theme(self) -> None:
        self.apply_theme("dark" if self.property("theme") == "light" else "light")

    def open_diagnostics(self, tab: str = "issues") -> None:
        tabs = self.findChild(QTabWidget, "diagnostics-tabs")
        if tabs is not None:
            tabs.setCurrentIndex(1 if tab == "logs" else 0)
        self.issue_drawer.setVisible(True)

    def update_issue_summary(self, errors: int, warnings: int, infos: int) -> None:
        self.issue_counts = (errors, warnings, infos)
        status_bar = self.statusBar()
        if hasattr(status_bar, "update_issue_summary"):
            status_bar.update_issue_summary(
                errors,
                warnings,
                infos,
                self.property("theme") or "light",
            )


def make_placeholder_page(text: str) -> QLabel:
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label

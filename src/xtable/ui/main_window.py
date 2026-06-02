from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    QSizePolicy,
    QStackedWidget,
    QTabWidget,
    QToolButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from xtable.application.project_service import ProjectError, ProjectService
from xtable.domain.project import Project
from xtable.ui.actions import ACTION_SPECS, create_actions
from xtable.ui.dialogs import ProjectDialogs
from xtable.ui.icons import icon_for
from xtable.ui.issue_drawer import IssueDrawer
from xtable.ui.status_bar import EditorStatusBar
from xtable.ui.theme import build_stylesheet


class MainWindow(QMainWindow):
    def __init__(
        self,
        project_service: ProjectService | None = None,
        dialogs: ProjectDialogs | None = None,
    ) -> None:
        super().__init__()
        self.project_service = project_service or ProjectService()
        self.dialogs = dialogs or ProjectDialogs()
        self.current_project: Project | None = None
        self.issue_counts = (0, 0, 0)
        self.setObjectName("xtable-main-window")
        self.setWindowTitle("XTable")
        self.resize(1200, 760)
        self.actions = create_actions(
            self,
            {
                "action-new-project": self.create_project,
                "action-open-project": self.open_project,
                "action-save-project": self.save_project,
                "action-toggle-theme": self.toggle_theme,
                "action-toggle-issues": lambda: self.toggle_issue_drawer("issues"),
                "action-open-ui-kit-demo": self.open_ui_kit_demo,
                "action-exit": self.close,
            },
        )
        self._build_menu_bar()
        self._build_toolbar()
        self._build_status_bar()
        self._build_workspace()
        self.apply_theme("light")

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        menu_bar.setObjectName("main-menu-bar")
        menus = {name: menu_bar.addMenu(name) for name in ("文件", "编辑", "查看", "窗口", "帮助")}
        for spec in ACTION_SPECS:
            menus[spec.menu].addAction(self.actions[spec.action_id])
            if spec.action_id in {"action-save-project", "action-redo", "action-validate"}:
                menus[spec.menu].addSeparator()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Project")
        toolbar.setObjectName("top-toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        for action_id in ("action-new-project", "action-open-project", "action-save-project"):
            toolbar.addAction(self.actions[action_id])
        toolbar.addSeparator()
        for action_id in ("action-import", "action-export"):
            toolbar.addAction(self.actions[action_id])
        toolbar.addSeparator()
        for action_id in ("action-undo", "action-redo"):
            toolbar.addAction(self.actions[action_id])
        toolbar.addSeparator()
        toolbar.addAction(self.actions["action-validate"])

        spacer = QWidget()
        spacer.setObjectName("toolbar-right-spacer")
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        toolbar.addAction(self.actions["action-toggle-theme"])
        toolbar.addAction(self.actions["action-diagnostics"])

    def _build_workspace(self) -> None:
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

        rail = QFrame()
        rail.setObjectName("left-rail")
        rail.setFixedWidth(56)
        rail_layout = QVBoxLayout(rail)
        rail_layout.setContentsMargins(8, 8, 8, 8)

        self.pages = QStackedWidget()
        self.pages.setObjectName("workspace-pages")
        for key, title, icon_text in (
            ("table", "Table", "table"),
            ("enum", "Enum", "enum"),
            ("meta", "Meta", "meta"),
        ):
            button = QToolButton()
            button.setObjectName(f"nav-{key}")
            button.setProperty("icon-id", icon_text)
            button.setToolTip(title)
            button.setAccessibleName(title)
            button.setCheckable(True)
            button.setFixedSize(42, 40)
            button.setIconSize(QSize(24, 24))
            button.setIcon(icon_for(icon_text, self.property("theme") or "light"))
            button.clicked.connect(lambda checked=False, page_key=key: self.show_page(page_key))
            rail_layout.addWidget(button)

            page = QLabel(f"{title} 工作区")
            page.setObjectName(f"page-{key}")
            page.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pages.addWidget(page)

        rail_layout.addStretch()
        work_layout.addWidget(rail)
        work_layout.addWidget(self.pages, 1)

        self.issue_drawer = IssueDrawer()
        self.main_splitter.addWidget(work_area)
        self.main_splitter.addWidget(self.issue_drawer)
        self.configure_diagnostics_drawer_bounds()
        self.main_splitter.setSizes([600, self.ui_state["diagnostics_drawer_height"]])
        outer_layout.addWidget(self.main_splitter, 1)
        self.setCentralWidget(root)
        self.show_page("table")

    def _build_status_bar(self) -> None:
        status_bar = EditorStatusBar(lambda: self.toggle_issue_drawer("issues"))
        self.status_fields = status_bar.fields
        self.setStatusBar(status_bar)

    def show_page(self, key: str) -> None:
        page = self.findChild(QWidget, f"page-{key}")
        if page is None:
            return
        self.pages.setCurrentWidget(page)
        for nav_key in ("table", "enum", "meta"):
            button = self.findChild(QToolButton, f"nav-{nav_key}")
            if button is not None:
                button.setChecked(nav_key == key)
        self.statusBar().set_object(key)

    def apply_theme(self, theme: str) -> None:
        self.setProperty("theme", theme)
        self.setStyleSheet(build_stylesheet(theme))
        for spec in ACTION_SPECS:
            action = self.actions.get(spec.action_id)
            if action is not None:
                action.setIcon(icon_for(spec.icon_id, theme))
        for key in ("table", "enum", "meta"):
            button = self.findChild(QToolButton, f"nav-{key}")
            if button is not None:
                button.setIcon(icon_for(button.property("icon-id"), theme))
        self.update_issue_summary(*self.issue_counts)

    def toggle_theme(self) -> None:
        self.apply_theme("dark" if self.property("theme") == "light" else "light")

    def toggle_issue_drawer(self, tab: str = "issues") -> None:
        tabs = self.findChild(QTabWidget, "diagnostics-tabs")
        if tabs is not None:
            tabs.setCurrentIndex(1 if tab == "logs" else 0)
        self.issue_drawer.setVisible(not self.issue_drawer.isVisible())

    @property
    def ui_state(self) -> dict[str, int]:
        if not hasattr(self, "_ui_state"):
            self._ui_state = {"diagnostics_drawer_height": 220}
        return self._ui_state

    def configure_diagnostics_drawer_bounds(self) -> None:
        max_height = max(160, self.height() // 2)
        self.issue_drawer.setMinimumHeight(160)
        self.issue_drawer.setMaximumHeight(max_height)

    def set_diagnostics_drawer_height(self, height: int) -> None:
        self.configure_diagnostics_drawer_bounds()
        self.issue_drawer.setVisible(True)
        bounded_height = max(
            self.issue_drawer.minimumHeight(),
            min(height, self.issue_drawer.maximumHeight()),
        )
        self.ui_state["diagnostics_drawer_height"] = bounded_height
        total_height = max(self.main_splitter.height(), bounded_height + 1)
        self.main_splitter.setSizes([total_height - bounded_height, bounded_height])

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

    def create_project(self) -> None:
        options = self.dialogs.get_project_create_options(self)
        if not options:
            return
        try:
            root = options.pop("root")
            self.current_project = self.project_service.create_project(root, **options)
            self._show_project_state("已创建项目")
        except ProjectError as error:
            self.dialogs.show_error(self, "新建项目失败", str(error))

    def open_project(self) -> None:
        root = self.dialogs.get_existing_project_root(self)
        if not root:
            return
        try:
            self.current_project = self.project_service.open_project(root)
            self._show_project_state("已打开项目")
        except ProjectError as error:
            self.dialogs.show_error(self, "打开项目失败", str(error))

    def save_project(self) -> None:
        if self.current_project is None:
            self.dialogs.show_error(self, "保存项目失败", "当前没有打开的项目。")
            return
        try:
            self.project_service.save_project(self.current_project)
            self._show_project_state("已保存项目")
        except ProjectError as error:
            self.dialogs.show_error(self, "保存项目失败", str(error))

    def _show_project_state(self, message: str) -> None:
        if self.current_project is None:
            return
        self.statusBar().showMessage(f"{message}：{self.current_project.settings.name}")
        self.statusBar().set_project(self.current_project.settings.name)

    def open_ui_kit_demo(self) -> None:
        from xtable.ui.demo import create_demo_window

        demo_window = getattr(self, "ui_kit_demo_window", None)
        if demo_window is None:
            demo_window = create_demo_window()
            self.ui_kit_demo_window = demo_window
        demo_window.show()
        demo_window.raise_()
        demo_window.activateWindow()

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
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
from xtable.domain.models import NormalTableDefinition, ProjectSchema
from xtable.domain.project import Project
from xtable.ui.actions import ACTION_SPECS, create_actions
from xtable.ui.components.inspector_panel import InspectorPanel
from xtable.ui.components.structure_editor import StructureEditor
from xtable.ui.components.table_explorer import TableExplorer
from xtable.ui.components.tables import TableWorkbench
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
        self.project_schema: ProjectSchema | None = None
        self.table_workbench: TableWorkbench | None = None
        self.table_explorer: TableExplorer | None = None
        self.structure_editor: StructureEditor | None = None
        self.inspector_panel: InspectorPanel | None = None
        self._schema_dirty: bool = False
        self._table_mode_stack: QStackedWidget | None = None
        self.issue_counts = (0, 0, 0)
        self.setObjectName("xtable-main-window")
        self.setWindowTitle("XTable")
        self.resize(1200, 760)
        self._page_keys = ("table", "enum", "meta")
        self.actions = create_actions(
            self,
            {
                "action-new-project": self.create_project,
                "action-open-project": self.open_project,
                "action-save-project": self.save_project,
                "action-toggle-theme": self.toggle_theme,
                "action-toggle-issues": lambda: self.toggle_issue_drawer("issues"),
                "action-toggle-inspector": self._toggle_inspector,
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
        toolbar.addAction(self.actions["action-toggle-inspector"])

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

        # Left navigation rail
        rail = QFrame()
        rail.setObjectName("left-rail")
        rail.setFixedWidth(56)
        rail_layout = QVBoxLayout(rail)
        rail_layout.setContentsMargins(8, 8, 8, 8)

        self.pages = QStackedWidget()
        self.pages.setObjectName("workspace-pages")

        # Table page: composite with mode switching
        table_page = self._build_table_page()
        self.pages.addWidget(table_page)

        enum_page = QLabel("Enum 工作区")
        enum_page.setObjectName("page-enum")
        enum_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pages.addWidget(enum_page)
        meta_page = QLabel("Meta 工作区")
        meta_page.setObjectName("page-meta")
        meta_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pages.addWidget(meta_page)

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

        rail_layout.addStretch()

        # Inspector panel (right side, starts hidden)
        self.inspector_panel = InspectorPanel(theme=self.property("theme") or "light")

        work_layout.addWidget(rail)
        work_layout.addWidget(self.pages, 1)
        work_layout.addWidget(self.inspector_panel)

        self.issue_drawer = IssueDrawer()
        self.main_splitter.addWidget(work_area)
        self.main_splitter.addWidget(self.issue_drawer)
        self.configure_diagnostics_drawer_bounds()
        self.main_splitter.setSizes([600, self.ui_state["diagnostics_drawer_height"]])
        outer_layout.addWidget(self.main_splitter, 1)
        self.setCentralWidget(root)
        self.show_page("table")

    def _build_table_page(self) -> QWidget:
        """Build the table page with data/structure mode switching and explorer."""
        page = QWidget()
        page.setObjectName("page-table")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Mode toggle bar
        mode_bar = QFrame()
        mode_bar.setObjectName("table-mode-bar")
        mode_bar.setFixedHeight(32)
        mode_layout = QHBoxLayout(mode_bar)
        mode_layout.setContentsMargins(8, 0, 0, 0)

        self._table_explorer = TableExplorer(theme=self.property("theme") or "light")
        mode_layout.addWidget(self._table_explorer)

        self._table_data_button = QToolButton()
        self._table_data_button.setObjectName("table-mode-data-button")
        self._table_data_button.setText("表格数据")
        self._table_data_button.setCheckable(True)
        self._table_data_button.setChecked(True)
        self._table_data_button.setToolTip("切换到数据视图")

        self._table_structure_button = QToolButton()
        self._table_structure_button.setObjectName("table-mode-structure-button")
        self._table_structure_button.setText("表格结构")
        self._table_structure_button.setCheckable(True)
        self._table_structure_button.setToolTip("切换到结构视图")

        mode_group = QButtonGroup()
        mode_group.setExclusive(True)
        mode_group.addButton(self._table_data_button)
        mode_group.addButton(self._table_structure_button)
        mode_group.idClicked.connect(self._switch_table_mode)

        mode_layout.addStretch()
        mode_layout.addWidget(self._table_data_button)
        mode_layout.addWidget(self._table_structure_button)
        layout.addWidget(mode_bar)

        # Mode content stack
        self._table_mode_stack = QStackedWidget()
        self._table_mode_stack.setObjectName("table-mode-stack")

        # Data mode: TableWorkbench
        self.table_workbench = TableWorkbench(theme=self.property("theme") or "light")
        self._table_mode_stack.addWidget(self.table_workbench)

        # Structure mode: StructureEditor
        self._structure_editor = StructureEditor(theme=self.property("theme") or "light")
        self._table_mode_stack.addWidget(self._structure_editor)

        layout.addWidget(self._table_mode_stack, 1)

        # Wire signals
        self._table_explorer.table_selected.connect(self._on_table_selected)
        self._table_explorer.table_added.connect(self._on_table_added)
        self._table_explorer.table_deleted.connect(self._on_table_deleted)
        self._structure_editor.field_focused.connect(self._on_field_focused)
        self._structure_editor.schema_modified.connect(self._on_schema_modified)
        if self.inspector_panel:
            self._structure_editor.field_focused.connect(
                lambda tid, fid: self._load_field_inspector(tid, fid)
            )

        return page

    def _build_status_bar(self) -> None:
        status_bar = EditorStatusBar(lambda: self.toggle_issue_drawer("issues"))
        self.status_fields = status_bar.fields
        self.setStatusBar(status_bar)

    def show_page(self, key: str) -> None:
        page = self.findChild(QWidget, f"page-{key}")
        if page is None:
            return
        self.pages.setCurrentWidget(page)
        for nav_key in self._page_keys:
            button = self.findChild(QToolButton, f"nav-{nav_key}")
            if button is not None:
                button.setChecked(nav_key == key)
        self.statusBar().set_object(key)
        # Auto-hide inspector when leaving table page
        if key != "table" and self.inspector_panel and self.inspector_panel.has_content():
            self.inspector_panel.clear()
            self.actions["action-toggle-inspector"].setChecked(False)

    def apply_theme(self, theme: str) -> None:
        self.setProperty("theme", theme)
        self.setStyleSheet(build_stylesheet(theme))
        for spec in ACTION_SPECS:
            action = self.actions.get(spec.action_id)
            if action is not None:
                action.setIcon(icon_for(spec.icon_id, theme))
        for key in self._page_keys:
            button = self.findChild(QToolButton, f"nav-{key}")
            if button is not None:
                button.setIcon(icon_for(button.property("icon-id"), theme))
        if self.inspector_panel:
            self.inspector_panel.apply_theme(theme)
        if self._table_explorer:
            self._table_explorer.setProperty("theme", theme)
        if self._structure_editor:
            self._structure_editor.setProperty("theme", theme)
        if self.table_workbench:
            self.table_workbench.setProperty("theme", theme)
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
            self._load_project_schema()
            self._show_project_state("已创建项目")
        except ProjectError as error:
            self.dialogs.show_error(self, "新建项目失败", str(error))

    def open_project(self) -> None:
        root = self.dialogs.get_existing_project_root(self)
        if not root:
            return
        try:
            self.current_project = self.project_service.open_project(root)
            self._load_project_schema()
            self._show_project_state("已打开项目")
        except ProjectError as error:
            self.dialogs.show_error(self, "打开项目失败", str(error))

    def save_project(self) -> None:
        if self.current_project is None:
            self.dialogs.show_error(self, "保存项目失败", "当前没有打开的项目。")
            return
        try:
            if self._schema_dirty and self.project_schema is not None:
                try:
                    self.project_schema.validate_structure()
                except ValueError as error:
                    self.dialogs.show_error(self, "校验失败", str(error))
                    return
                self.current_project = self.project_service.save_schema(
                    self.current_project, self.project_schema
                )
            self.current_project = self.project_service.save_project(self.current_project)
            self._clear_schema_dirty()
            self._show_project_state("已保存项目")
        except ProjectError as error:
            self.dialogs.show_error(self, "保存项目失败", str(error))

    def _show_project_state(self, message: str) -> None:
        if self.current_project is None:
            return
        self.statusBar().showMessage(f"{message}：{self.current_project.settings.name}")
        self.statusBar().set_project(self.current_project.settings.name)

    def _load_project_schema(self) -> None:
        if self.current_project is None or self.table_workbench is None:
            return
        try:
            self.project_schema = self.project_service.load_schema(self.current_project)
        except ProjectError:
            self.project_schema = ProjectSchema()

        # Populate explorer
        if self._table_explorer is not None:
            self._table_explorer.load_schema(self.project_schema)

        # Select first normal table
        normal_tables = [
            table for table in self.project_schema.tables.values()
            if isinstance(table, NormalTableDefinition)
        ]
        if normal_tables:
            self._set_table(normal_tables[0])
            if self._table_explorer is not None:
                self._table_explorer.set_selected(normal_tables[0].table_id)
        self._clear_schema_dirty()

    def _set_table(self, table: NormalTableDefinition) -> None:
        if self.table_workbench is None or self._structure_editor is None:
            return
        self.table_workbench.set_table(table)
        self._structure_editor.set_table(table)
        self._switch_to_table_mode("data")

    def _switch_table_mode(self, _button_id: int) -> None:
        if self._table_mode_stack is None:
            return
        if self._table_data_button and self._table_data_button.isChecked():
            self._table_mode_stack.setCurrentIndex(0)
        elif self._table_structure_button and self._table_structure_button.isChecked():
            self._table_mode_stack.setCurrentIndex(1)

    def _switch_to_table_mode(self, mode: str) -> None:
        if self._table_mode_stack is None:
            return
        if mode == "structure":
            self._table_structure_button.setChecked(True)
            self._table_mode_stack.setCurrentIndex(1)
        else:
            self._table_data_button.setChecked(True)
            self._table_mode_stack.setCurrentIndex(0)

    def _on_table_selected(self, table_id: str) -> None:
        if self.project_schema is None or self._structure_editor is None:
            return
        table = self.project_schema.tables.get(table_id)
        if isinstance(table, NormalTableDefinition):
            self._set_table(table)

    def _on_table_added(self, table_id: str) -> None:
        self._mark_schema_dirty()
        # Switch to structure mode so user can edit fields
        if self.project_schema is not None and self._structure_editor is not None:
            table = self.project_schema.tables.get(table_id)
            if isinstance(table, NormalTableDefinition):
                self.table_workbench.set_table(table)
                self._structure_editor.set_table(table)
                self._switch_to_table_mode("structure")

    def _on_table_deleted(self, table_id: str) -> None:
        self._mark_schema_dirty()
        # Switch to another table if current was deleted
        if self.project_schema is None or self._table_explorer is None:
            return
        current = self._table_explorer.current_table_id()
        if current is None:
            # No tables left, show sample
            if self.table_workbench is not None:
                self.table_workbench.set_table(self.table_workbench._sample_table())
            if self._structure_editor is not None:
                self._structure_editor.set_table(None)

    def _on_field_focused(self, table_id: str, field_id: str) -> None:
        if self.project_schema is None or self.inspector_panel is None:
            return
        self._load_field_inspector(table_id, field_id)

    def _load_field_inspector(self, table_id: str, field_id: str) -> None:
        if self.project_schema is None or self.inspector_panel is None:
            return
        table = self.project_schema.tables.get(table_id)
        if table is None:
            return
        field = table.field(field_id)
        if field is not None:
            self.inspector_panel.show_field(table_id, field)

    def _on_schema_modified(self, table_id: str) -> None:
        self._mark_schema_dirty()
        # Refresh workbench if field structure changed
        if self.project_schema is not None and self.table_workbench is not None:
            table = self.project_schema.tables.get(table_id)
            if isinstance(table, NormalTableDefinition):
                self.table_workbench.set_table(table)

    def _toggle_inspector(self) -> None:
        if self.inspector_panel is None:
            return
        if self.inspector_panel.isVisible():
            self.inspector_panel.clear()
        else:
            self.inspector_panel.setVisible(True)
            if not self.inspector_panel.has_content():
                pass  # Shows empty state
        self.actions["action-toggle-inspector"].setChecked(self.inspector_panel.isVisible())

    def _mark_schema_dirty(self) -> None:
        self._schema_dirty = True
        self.setWindowTitle("XTable *")

    def _clear_schema_dirty(self) -> None:
        self._schema_dirty = False
        self.setWindowTitle("XTable")

    def open_ui_kit_demo(self) -> None:
        from xtable.ui.demo import create_demo_window

        demo_window = getattr(self, "ui_kit_demo_window", None)
        if demo_window is None:
            demo_window = create_demo_window()
            self.ui_kit_demo_window = demo_window
        demo_window.show()
        demo_window.raise_()
        demo_window.activateWindow()

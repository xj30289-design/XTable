from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QWidget,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTableWidget,
    QToolButton,
    QToolBar,
)

from xtable.app.main_window import MainWindow
from xtable.domain.project import Project, ProjectSettings


class FakeDialogs:
    def __init__(self, project_root):
        self.project_root = project_root

    def get_project_create_options(self, parent):
        return {
            "root": self.project_root,
            "name": "Demo",
            "operator": "designer",
        }

    def get_existing_project_root(self, parent):
        return self.project_root

    def show_error(self, parent, title, message):
        raise AssertionError(f"{title}: {message}")


class FakeProjectService:
    def __init__(self, project_root):
        self.project = Project(
            root=project_root,
            settings=ProjectSettings(name="Demo", operator="designer"),
            config_digest="digest",
        )
        self.created = False
        self.opened = False
        self.saved = False

    def create_project(self, root, **options):
        self.created = True
        assert root == self.project.root
        assert options["name"] == "Demo"
        return self.project

    def open_project(self, root):
        self.opened = True
        assert root == self.project.root
        return self.project

    def save_project(self, project):
        self.saved = True
        assert project is self.project
        return project

    def load_schema(self, project):
        from xtable.domain.models import ProjectSchema
        return ProjectSchema()


def test_main_window_exposes_phase_one_project_actions():
    app = QApplication.instance() or QApplication([])

    window = MainWindow()
    window.show()

    assert isinstance(window, QMainWindow)
    assert window.objectName() == "xtable-main-window"
    assert window.findChild(object, "action-new-project") is not None
    assert window.findChild(object, "action-open-project") is not None
    assert window.findChild(object, "action-save-project") is not None
    assert window.findChild(object, "action-toggle-theme") is not None
    assert window.findChild(object, "action-toggle-issues") is not None
    assert window.findChild(object, "left-rail") is not None
    assert window.findChild(object, "status-bar") is not None
    assert window.findChild(object, "main-workspace") is not None

    window.close()
    app.quit()


def test_main_window_switches_core_panels_and_exposes_semantic_rail_buttons():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    pages = window.findChild(QStackedWidget, "workspace-pages")

    for object_name, title in (
        ("nav-table", "Table"),
        ("nav-enum", "Enum"),
        ("nav-meta", "Meta"),
    ):
        button = window.findChild(object, object_name)
        assert button is not None
        assert button.toolTip() == title
        button.click()
        assert pages.currentWidget().objectName() == f"page-{title.lower()}"

    window.close()
    app.quit()


def test_main_window_status_bar_has_structured_fields_and_updates_project(tmp_path):
    app = QApplication.instance() or QApplication([])
    service = FakeProjectService(tmp_path / "DemoProject")
    dialogs = FakeDialogs(tmp_path / "DemoProject")
    window = MainWindow(project_service=service, dialogs=dialogs)

    expected_fields = {
        "status-project": "未打开",
        "status-object": "table",
        "status-save": "未保存",
        "status-validation": "未运行",
        "status-task": "空闲",
        "status-issues": "0/0",
    }
    for object_name, text in expected_fields.items():
        label = window.findChild(QLabel, object_name)
        assert label.text() == text
        assert label.toolTip()

    window.findChild(object, "action-new-project").trigger()

    assert window.findChild(QLabel, "status-project").text() == "Demo"
    assert window.findChild(QLabel, "status-save").text() == "已保存"

    window.close()
    app.quit()


def test_main_window_toggles_theme_and_issue_drawer():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    theme_action = window.findChild(object, "action-toggle-theme")
    issue_action = window.findChild(object, "action-toggle-issues")
    issue_drawer = window.findChild(object, "issue-drawer")
    tabs = window.findChild(QTabWidget, "diagnostics-tabs")

    assert window.property("theme") == "light"
    theme_action.trigger()
    assert window.property("theme") == "dark"

    assert not issue_drawer.isVisible()
    issue_action.trigger()
    assert issue_drawer.isVisible()
    assert issue_drawer.property("drawer-position") == "bottom"
    assert issue_drawer.maximumHeight() >= 180
    assert tabs.tabText(tabs.currentIndex()) == "问题"

    window.close()
    app.quit()


def test_main_window_menus_toolbar_icons_and_right_aligned_theme_action():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    toolbar = window.findChild(QToolBar, "top-toolbar")
    menu_bar = window.findChild(QMenuBar, "main-menu-bar")

    assert toolbar.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert window.findChild(object, "toolbar-right-spacer") is not None
    menu_titles = [
        menu.title()
        for menu in menu_bar.findChildren(QMenu, options=Qt.FindChildOption.FindDirectChildrenOnly)
        if menu.title()
    ]
    assert menu_titles == [
        "文件",
        "编辑",
        "查看",
        "窗口",
        "帮助",
    ]

    for action_id in (
        "action-new-project",
        "action-open-project",
        "action-save-project",
        "action-import",
        "action-export",
        "action-validate",
        "action-undo",
        "action-redo",
        "action-toggle-theme",
        "action-toggle-issues",
    ):
        action = window.findChild(object, action_id)
        assert action is not None
        assert action.property("icon-id")
        assert action.toolTip()
        assert not action.icon().isNull()

    toolbar_action_ids = {
        action.objectName()
        for action in toolbar.actions()
        if action.objectName()
    }
    assert "action-toggle-issues" not in toolbar_action_ids

    window.close()
    app.quit()


def test_dark_theme_stylesheet_covers_toolbar_menu_tooltip_and_states():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    window.apply_theme("dark")
    stylesheet = window.styleSheet()

    for selector in (
        "QToolBar QToolButton",
        "QMenuBar",
        "QMenu",
        "QToolTip",
        "QStatusBar",
        "QTableWidget",
        "QHeaderView::section",
        "QTableCornerButton::section",
        "QAbstractScrollArea",
        "QScrollBar",
        "QTabWidget::pane",
        "QTabBar::tab",
        "QLineEdit",
        "QWidget#diagnostics-page",
        "QToolButton#nav-table",
        "QToolButton#nav-enum",
        "QToolButton#nav-meta",
        "QSplitter::handle",
        "drawer_border",
        "shadow_border",
        "QWidget#status-left-group",
        "QWidget#status-context-group",
        "QWidget#status-state-group",
        "QToolButton#status-issue-summary",
        "selection-background-color",
        ":hover",
        ":disabled",
        ":checked",
    ):
        assert selector in stylesheet

    window.close()
    app.quit()


def test_diagnostics_drawer_uses_vertical_splitter_and_log_tab():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    splitter = window.findChild(QSplitter, "main-vertical-splitter")
    tabs = window.findChild(QTabWidget, "diagnostics-tabs")

    assert splitter.orientation() == Qt.Orientation.Vertical
    assert tabs.count() == 2
    assert [tabs.tabText(index) for index in range(tabs.count())] == ["问题", "日志"]
    assert window.findChild(QTableWidget, "issue-table") is not None
    assert window.findChild(QTableWidget, "log-table") is not None

    before = window.findChild(object, "left-rail").width()
    window.toggle_issue_drawer("logs")
    splitter.setSizes([500, 220])

    assert window.findChild(object, "left-rail").width() == before
    assert tabs.tabText(tabs.currentIndex()) == "日志"

    window.close()
    app.quit()


def test_diagnostics_drawer_height_bounds_and_memory():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(1000, 800)
    window.show()
    drawer = window.findChild(object, "issue-drawer")

    window.configure_diagnostics_drawer_bounds()

    assert drawer.minimumHeight() == 160
    assert drawer.maximumHeight() == 400

    window.set_diagnostics_drawer_height(240)

    assert window.ui_state["diagnostics_drawer_height"] == 240
    assert window.findChild(QSplitter, "main-vertical-splitter").sizes()[-1] == 240

    window.close()
    app.quit()


def test_status_bar_issue_summary_controls_diagnostics_drawer():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    issue_button = window.findChild(QToolButton, "status-issue-summary")
    tabs = window.findChild(QTabWidget, "diagnostics-tabs")

    assert issue_button is not None
    assert issue_button.property("icon-id") == "ok"
    assert issue_button.text() == "0 / 0"

    window.update_issue_summary(errors=3, warnings=2, infos=1)

    assert issue_button.property("icon-id") == "error"
    assert issue_button.text() == "3 / 2"
    assert "Error: 3" in issue_button.toolTip()

    issue_button.click()

    assert window.findChild(object, "issue-drawer").isVisible()
    assert tabs.tabText(tabs.currentIndex()) == "问题"

    window.close()
    app.quit()


def test_status_bar_groups_are_spaced_and_issue_summary_is_left_aligned():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    status_bar = window.findChild(object, "status-bar")
    issue_summary = window.findChild(QToolButton, "status-issue-summary")

    assert window.findChild(QWidget, "status-left-group") is not None
    assert window.findChild(QWidget, "status-context-group") is not None
    assert window.findChild(QWidget, "status-state-group") is not None
    assert status_bar.layout().spacing() >= 8
    assert issue_summary is not None
    assert issue_summary.property("summary-kind") == "issue-summary"
    assert issue_summary.property("icon-id") == "ok"
    assert issue_summary.text() == "0 / 0"

    status_bar.update_issue_summary(4, 2, 1, "dark")

    assert issue_summary.property("icon-id") == "error"
    assert issue_summary.text() == "4 / 2"
    assert "Error: 4" in issue_summary.toolTip()

    issue_summary.click()

    assert window.findChild(object, "issue-drawer").isVisible()

    window.close()
    app.quit()


def test_sidebar_uses_project_svg_icons_instead_of_text_symbols():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    for object_name, icon_id in (
        ("nav-table", "table"),
        ("nav-enum", "enum"),
        ("nav-meta", "meta"),
    ):
        button = window.findChild(QToolButton, object_name)
        assert button is not None
        assert button.text() == ""
        assert button.property("icon-id") == icon_id
        assert button.iconSize() == QSize(24, 24)
        assert not button.icon().isNull()

    window.close()
    app.quit()


def test_main_window_project_actions_call_project_service(tmp_path):
    app = QApplication.instance() or QApplication([])
    service = FakeProjectService(tmp_path / "DemoProject")
    dialogs = FakeDialogs(tmp_path / "DemoProject")
    window = MainWindow(project_service=service, dialogs=dialogs)

    window.findChild(object, "action-new-project").trigger()
    assert service.created
    assert "Demo" in window.statusBar().currentMessage()

    window.findChild(object, "action-open-project").trigger()
    assert service.opened
    assert "Demo" in window.statusBar().currentMessage()

    window.findChild(object, "action-save-project").trigger()
    assert service.saved
    assert "已保存" in window.statusBar().currentMessage()

    window.close()
    app.quit()

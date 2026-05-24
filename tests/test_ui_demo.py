from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QMainWindow,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QToolButton,
)

from xtable.app.main_window import MainWindow
from xtable.ui.demo import UiKitDemoWindow, create_demo_window


def test_ui_kit_demo_window_exposes_complete_editor_shell():
    app = QApplication.instance() or QApplication([])

    window = create_demo_window()
    window.show()

    assert isinstance(window, UiKitDemoWindow)
    assert isinstance(window, QMainWindow)
    assert window.objectName() == "ui-kit-demo-window"
    assert window.findChild(object, "editor-toolbar") is not None
    assert window.findChild(object, "navigation-rail") is not None
    assert window.findChild(object, "status-bar") is not None
    assert window.findChild(object, "issue-drawer") is not None
    assert window.findChild(QTableWidget, "preview-table") is not None
    assert window.findChild(object, "field-inspector") is not None
    assert window.findChild(object, "workspace-tabs") is not None
    assert window.findChild(object, "data-list-view") is not None
    assert window.findChild(object, "json-editor-shell") is not None
    assert window.findChild(QStackedWidget, "workspace-pages") is not None
    for page_key in (
        "overview",
        "theme-lab",
        "buttons-icons",
        "dialogs",
        "diagnostics",
        "tables",
        "forms",
        "layouts",
        "table",
        "enum",
        "meta",
    ):
        assert window.findChild(object, f"nav-{page_key}") is not None
        assert window.findChild(object, f"page-{page_key}") is not None

    window.close()
    app.quit()


def test_ui_kit_demo_switches_theme_and_pages():
    app = QApplication.instance() or QApplication([])

    window = create_demo_window()
    window.show()

    assert window.property("theme") == "light"
    window.apply_theme("dark")
    assert window.property("theme") == "dark"
    assert "QFrame#field-inspector" in window.styleSheet()

    window.show_page("meta")

    assert window.findChild(QStackedWidget, "workspace-pages").currentWidget().objectName() == "page-meta"

    window.close()
    app.quit()


def test_ui_kit_demo_exposes_state_controls_for_key_components():
    app = QApplication.instance() or QApplication([])

    window = create_demo_window()
    window.show()

    assert window.findChild(QFrame, "demo-control-panel") is not None
    error_spin = window.findChild(QSpinBox, "demo-errors-input")
    warning_spin = window.findChild(QSpinBox, "demo-warnings-input")
    info_spin = window.findChild(QSpinBox, "demo-infos-input")
    drawer_slider = window.findChild(QSlider, "demo-drawer-height-input")
    table_state = window.findChild(QComboBox, "demo-table-state-input")
    field_state = window.findChild(QComboBox, "demo-field-state-input")

    error_spin.setValue(5)
    warning_spin.setValue(3)
    info_spin.setValue(1)
    drawer_slider.setValue(260)
    table_state.setCurrentText("dirty")
    field_state.setCurrentText("invalid")

    assert window.findChild(object, "status-issue-summary").text() == "5 / 3"
    assert window.findChild(object, "issue-drawer").isVisible()
    assert window.findChild(QTableWidget, "preview-table").property("table-state") == "dirty"
    assert window.findChild(object, "field-inspector").property("field-state") == "invalid"

    window.close()
    app.quit()


def test_dialogs_demo_page_exposes_themed_dialog_entry_points():
    app = QApplication.instance() or QApplication([])

    window = create_demo_window()
    window.show_page("dialogs")

    error_button = window.findChild(QToolButton, "demo-error-dialog-button")
    confirm_button = window.findChild(QToolButton, "demo-confirm-dialog-button")

    assert error_button is not None
    assert error_button.text() == ""
    assert error_button.property("icon-id") == "error"
    assert confirm_button is not None
    assert confirm_button.text() == ""
    assert confirm_button.property("icon-id") == "ok"

    window.close()
    app.quit()


def test_main_window_exposes_ui_kit_demo_entry_from_help_menu():
    app = QApplication.instance() or QApplication([])

    window = MainWindow()
    action = window.findChild(object, "action-open-ui-kit-demo")

    assert action is not None
    assert action.property("icon-id") == "diagnostics"
    assert action.toolTip() == "打开 UI Kit Demo"

    action.trigger()

    demo_window = getattr(window, "ui_kit_demo_window", None)
    assert demo_window is not None
    assert demo_window.objectName() == "ui-kit-demo-window"

    demo_window.close()
    window.close()
    app.quit()

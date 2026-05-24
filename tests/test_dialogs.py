from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLabel

from xtable.ui.dialogs import ConfirmDialog, MessageDialog, ProjectDialogs
from xtable.ui.theme import build_stylesheet


def test_message_dialog_uses_project_theme_and_semantic_parts():
    app = QApplication.instance() or QApplication([])

    dialog = MessageDialog.error("保存失败", "项目文件被占用。", theme="dark")

    assert isinstance(dialog, QDialog)
    assert dialog.objectName() == "xtable-message-dialog"
    assert dialog.property("dialog-kind") == "error"
    assert dialog.findChild(QLabel, "message-dialog-title").text() == "保存失败"
    assert dialog.findChild(QLabel, "message-dialog-body").text() == "项目文件被占用。"
    assert dialog.findChild(QLabel, "message-dialog-icon").property("icon-id") == "error"
    assert dialog.findChild(QDialogButtonBox, "message-dialog-buttons") is not None
    assert "QDialog#xtable-message-dialog" in dialog.styleSheet()
    assert "#20252b" in dialog.styleSheet()

    dialog.close()
    app.quit()


def test_project_dialogs_create_themed_error_dialog_instead_of_bare_message_box():
    app = QApplication.instance() or QApplication([])

    dialogs = ProjectDialogs()
    dialog = dialogs.create_error_dialog(None, "打开失败", "配置文件损坏", theme="dark")

    assert isinstance(dialog, MessageDialog)
    assert dialog.objectName() == "xtable-message-dialog"
    assert dialog.findChild(QLabel, "message-dialog-title").text() == "打开失败"
    assert dialog.findChild(QLabel, "message-dialog-body").text() == "配置文件损坏"
    assert "QMessageBox" not in ProjectDialogs.show_error.__code__.co_names

    dialog.close()
    app.quit()


def test_theme_stylesheet_covers_project_dialog_and_governed_components():
    stylesheet = build_stylesheet("dark")

    for selector in (
        "QDialog#xtable-message-dialog",
        "QFrame#message-dialog-icon-frame",
        "QLabel#message-dialog-title",
        "QLabel#message-dialog-body",
        "QDialogButtonBox QPushButton",
        "dialog_bg",
        "dialog_button_bg",
        "danger",
    ):
        assert selector in stylesheet


def test_ui_layer_does_not_create_bare_message_boxes():
    ui_sources = Path("src/xtable/ui").glob("*.py")

    for source_path in ui_sources:
        source = source_path.read_text(encoding="utf-8")
        assert "QMessageBox" not in source


def test_confirm_dialog_uses_text_buttons_for_rigorous_decisions():
    app = QApplication.instance() or QApplication([])

    dialog = ConfirmDialog("覆盖文件", "确认覆盖当前导出文件？", theme="dark")
    buttons = dialog.findChild(QDialogButtonBox, "confirm-dialog-buttons")

    assert dialog.objectName() == "xtable-confirm-dialog"
    assert dialog.property("dialog-kind") == "confirm"
    assert buttons is not None
    assert buttons.button(QDialogButtonBox.StandardButton.Ok).text() == "确认"
    assert buttons.button(QDialogButtonBox.StandardButton.Cancel).text() == "取消"
    assert "QDialog#xtable-message-dialog" in dialog.styleSheet()
    assert "QDialog#xtable-confirm-dialog" in dialog.styleSheet()
    assert "#20252b" in dialog.styleSheet()

    dialog.close()
    app.quit()

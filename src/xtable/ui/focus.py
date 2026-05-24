from __future__ import annotations

from typing import Protocol

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QApplication, QLineEdit, QTextEdit, QWidget


class ManagedEditor(Protocol):
    def set_active_editor(self, active: bool) -> None: ...


class EditorFocusManager:
    def __init__(self) -> None:
        self.active_editor: ManagedEditor | QWidget | None = None
        self.last_deactivate_reason = ""

    def activate(self, editor: ManagedEditor | QWidget) -> None:
        if self.active_editor is editor:
            self._set_active(editor, True)
            return
        if self.active_editor is not None:
            self._set_active(self.active_editor, False)
        self.active_editor = editor
        self._set_active(editor, True)

    def deactivate_active(self, *, reason: str = "manual") -> None:
        self.last_deactivate_reason = reason
        if self.active_editor is not None:
            self._set_active(self.active_editor, False)
        self.active_editor = None

    def _set_active(self, editor: ManagedEditor | QWidget, active: bool) -> None:
        if hasattr(editor, "set_active_editor"):
            editor.set_active_editor(active)
            return
        editor.setProperty("active-editor", active)
        editor.style().unpolish(editor)
        editor.style().polish(editor)


class ManagedLineEdit(QLineEdit):
    def __init__(self, text: str, manager: EditorFocusManager) -> None:
        super().__init__(text)
        self.manager = manager
        self.setProperty("active-editor", False)

    def activate_editor(self) -> None:
        self.manager.activate(self)

    def set_active_editor(self, active: bool) -> None:
        self.setProperty("active-editor", active)
        self.style().unpolish(self)
        self.style().polish(self)


class EditorFocusEventFilter(QObject):
    def __init__(self, manager: EditorFocusManager, root: QWidget) -> None:
        super().__init__(root)
        self.manager = manager
        self.root = root

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.FocusIn and isinstance(watched, (QLineEdit, QTextEdit)):
            self.manager.activate(watched)
        if event.type() == QEvent.Type.MouseButtonPress:
            widget = QApplication.widgetAt(event.globalPosition().toPoint()) if hasattr(event, "globalPosition") else None
            editor = self._editor_for(widget)
            if editor is not None:
                self.manager.activate(editor)
            else:
                self.manager.deactivate_active(reason="outside-click")
        return False

    def _editor_for(self, widget: QWidget | None) -> QWidget | None:
        current = widget
        while current is not None:
            if current is self.root:
                return None
            if isinstance(current, (QLineEdit, QTextEdit)) and current.isEnabled() and not current.isReadOnly():
                return current
            current = current.parentWidget()
        return None


def install_editor_focus_management(root: QWidget, manager: EditorFocusManager) -> EditorFocusEventFilter:
    event_filter = EditorFocusEventFilter(manager, root)
    root.installEventFilter(event_filter)
    for widget_type in (QLineEdit, QTextEdit):
        for editor in root.findChildren(widget_type):
            editor.installEventFilter(event_filter)
            editor.setProperty("active-editor", False)
    return event_filter

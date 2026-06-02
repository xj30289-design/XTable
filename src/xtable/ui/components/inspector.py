from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QToolButton,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QTextEdit,
    QVBoxLayout,
)

from xtable.ui.icons import icon_for


class FieldInspector(QFrame):
    def __init__(self, *, theme: str = "light") -> None:
        super().__init__()
        self.setObjectName("field-inspector")
        self.setProperty("theme", theme)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("字段属性")
        title.setObjectName("field-inspector-title")
        root.addWidget(title)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(8)

        name_input = QLineEdit("item_id")
        name_input.setObjectName("field-name-input")
        form.addRow("字段名", name_input)

        type_input = QComboBox()
        type_input.setObjectName("field-type-input")
        type_input.addItems(["Int", "String", "Bool", "Enum", "List<String>", "Json"])
        form.addRow("类型", type_input)

        required_input = QCheckBox("必填")
        required_input.setObjectName("field-required-input")
        required_input.setChecked(True)
        form.addRow("约束", required_input)

        default_input = QLineEdit("0")
        default_input.setObjectName("field-default-input")
        form.addRow("默认值", default_input)

        description_input = QTextEdit("物品配置表主键，用于程序侧读取。")
        description_input.setObjectName("field-description-input")
        description_input.setFixedHeight(78)
        form.addRow("说明", description_input)

        root.addLayout(form)
        root.addStretch()

    def set_field_state(self, state: str) -> None:
        self.setProperty("field-state", state)
        for child in self.findChildren(QLineEdit):
            child.setEnabled(state != "disabled")
            child.setReadOnly(state == "readonly")
            child.setProperty("display-mode", "readonly" if state == "readonly" else "editable")
            child.setCursor(Qt.CursorShape.ArrowCursor if state == "readonly" else Qt.CursorShape.IBeamCursor)
        for child in self.findChildren(QTextEdit):
            child.setEnabled(state != "disabled")
            child.setReadOnly(state == "readonly")
            child.setProperty("display-mode", "readonly" if state == "readonly" else "editable")
        for child in self.findChildren((QComboBox)):
            child.setEnabled(state not in {"disabled", "readonly"})
            child.setProperty("display-mode", "readonly" if state == "readonly" else "editable")
        for child in self.findChildren(QCheckBox):
            child.setEnabled(state not in {"disabled", "readonly"})
            child.setProperty("display-mode", "readonly" if state == "readonly" else "editable")


class PickerShell(QFrame):
    def __init__(self, kind: str, title: str, values: list[str], *, state: str = "normal") -> None:
        super().__init__()
        self.setObjectName(f"{kind}-picker-shell")
        self.setProperty("field-state", state)
        self.setProperty("editor-kind", kind)
        self.setProperty("ui-kit-component", "field-editor")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        label = QLabel(title)
        label.setObjectName(f"{kind}-picker-title")
        row = QHBoxLayout()
        status_button = QToolButton()
        status_button.setObjectName(f"{kind}-picker-status-button")
        status_button.setProperty("field-state", state)
        icon_id = "error" if state == "invalid" else "info" if state in {"readonly", "disabled"} else "ok"
        status_button.setProperty("icon-id", icon_id)
        status_button.setIcon(icon_for(icon_id))
        status_button.setToolTip(f"{title}: {state}")
        combo = QComboBox()
        combo.setObjectName(f"{kind}-picker-input")
        combo.addItems(values)
        combo.setEnabled(state not in {"disabled", "readonly"})
        combo.setProperty("display-mode", "readonly" if state == "readonly" else "editable")
        row.addWidget(status_button)
        row.addWidget(combo, 1)
        layout.addWidget(label)
        layout.addLayout(row)


class JsonEditorShell(QFrame):
    def __init__(self, *, state: str = "normal") -> None:
        super().__init__()
        self.setObjectName("json-editor-shell")
        self.setProperty("field-state", state)
        self.setProperty("ui-kit-component", "field-editor")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        toolbar = QHBoxLayout()
        self.validate_button = QToolButton()
        self.validate_button.setObjectName("json-editor-validate-button")
        self.validate_button.setIcon(icon_for("validate"))
        self.validate_button.setToolTip("校验 Json")
        self.format_button = QToolButton()
        self.format_button.setObjectName("json-editor-format-button")
        self.format_button.setIcon(icon_for("logs"))
        self.format_button.setToolTip("格式化 Json")
        self.minify_button = QToolButton()
        self.minify_button.setObjectName("json-editor-minify-button")
        self.minify_button.setIcon(icon_for("export"))
        self.minify_button.setToolTip("压缩 Json")
        toolbar.addWidget(QLabel("Json 内容"))
        toolbar.addStretch()
        toolbar.addWidget(self.validate_button)
        toolbar.addWidget(self.format_button)
        toolbar.addWidget(self.minify_button)
        self.editor = QTextEdit('{"id": 1001, "tags": ["shop", "event"]}')
        self.editor.setObjectName("json-editor-input")
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.editor.setEnabled(state not in {"disabled", "readonly"})
        self.editor.setReadOnly(state == "readonly")
        self.editor.setProperty("display-mode", "readonly" if state == "readonly" else "editable")
        self.status = QLabel("Line 1, Column 1")
        self.status.setObjectName("json-editor-status")
        self.status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.validate_button.clicked.connect(self.validate_json)
        self.format_button.clicked.connect(self.format_json)
        self.minify_button.clicked.connect(self.minify_json)
        self.editor.cursorPositionChanged.connect(self.update_cursor_status)
        layout.addLayout(toolbar)
        layout.addWidget(self.editor)
        layout.addWidget(self.status)
        self.update_cursor_status()

    def validate_json(self) -> bool:
        try:
            json.loads(self.editor.toPlainText())
        except json.JSONDecodeError as error:
            self.setProperty("json-valid", False)
            self.setProperty("field-state", "invalid")
            self.status.setText(f"Error line {error.lineno}, column {error.colno}: {error.msg}")
            return False
        self.setProperty("json-valid", True)
        self.setProperty("field-state", "normal")
        self.status.setText("Valid JSON")
        return True

    def format_json(self) -> None:
        try:
            data = json.loads(self.editor.toPlainText())
        except json.JSONDecodeError:
            self.validate_json()
            return
        self.editor.setPlainText(json.dumps(data, ensure_ascii=False, indent=2))
        self.update_cursor_status()
        self.validate_json()

    def minify_json(self) -> None:
        try:
            data = json.loads(self.editor.toPlainText())
        except json.JSONDecodeError:
            self.validate_json()
            return
        self.editor.setPlainText(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        self.update_cursor_status()
        self.validate_json()

    def update_cursor_status(self) -> None:
        cursor = self.editor.textCursor()
        self.status.setText(f"Line {cursor.blockNumber() + 1}, Column {cursor.positionInBlock() + 1}")


class ListEditorShell(QFrame):
    def __init__(self, *, state: str = "normal") -> None:
        super().__init__()
        self.setObjectName("list-editor-shell")
        self.setProperty("field-state", state)
        self.setProperty("ui-kit-component", "field-editor")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        values = QListWidget()
        values.setObjectName("list-editor-values")
        if state != "empty":
            values.addItems(["shop", "limited", "event"])
        values.setEnabled(state not in {"disabled", "readonly"})
        values.setProperty("display-mode", "readonly" if state == "readonly" else "editable")
        layout.addWidget(QLabel("列表值"))
        layout.addWidget(values)


class MetaEditorShell(QFrame):
    def __init__(self, *, state: str = "normal") -> None:
        super().__init__()
        self.setObjectName("meta-editor-shell")
        self.setProperty("field-state", state)
        self.setProperty("ui-kit-component", "field-editor")
        layout = QFormLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        for object_name, label, value in (
            ("meta-hp-input", "hp", "100"),
            ("meta-attack-input", "attack", "24"),
            ("meta-defense-input", "defense", "8"),
        ):
            input_widget = QLineEdit(value)
            input_widget.setObjectName(object_name)
            input_widget.setEnabled(state != "disabled")
            input_widget.setReadOnly(state == "readonly")
            input_widget.setProperty("display-mode", "readonly" if state == "readonly" else "editable")
            layout.addRow(label, input_widget)

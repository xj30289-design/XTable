from __future__ import annotations

import json

from dataclasses import replace

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
)

from xtable.domain.models import FieldDefinition, FieldType
from xtable.ui.icons import icon_for


class FieldInspector(QFrame):
    """Data-driven field properties editor.

    Emits ``fieldModified(table_id, field_id, new_FieldDefinition)`` when
    any form value changes.
    """

    fieldModified = Signal(str, str, object)  # table_id, field_id, FieldDefinition

    def __init__(self, *, theme: str = "light") -> None:
        super().__init__()
        self.setObjectName("field-inspector")
        self.setProperty("theme", theme)
        self._table_id: str = ""
        self._field: FieldDefinition | None = None
        self._suppress_signal = False

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("字段属性")
        title.setObjectName("field-inspector-title")
        root.addWidget(title)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(6)

        # Basic fields
        self._field_id_input = QLineEdit()
        self._field_id_input.setObjectName("field-id-input")
        self._field_id_input.setReadOnly(True)
        form.addRow("ID", self._field_id_input)

        self._name_input = QLineEdit()
        self._name_input.setObjectName("field-name-input")
        form.addRow("名称", self._name_input)

        self._display_name_input = QLineEdit()
        self._display_name_input.setObjectName("field-display-name-input")
        form.addRow("显示名", self._display_name_input)

        self._type_input = QComboBox()
        self._type_input.setObjectName("field-type-input")
        form.addRow("类型", self._type_input)

        self._required_input = QCheckBox("必填")
        self._required_input.setObjectName("field-required-input")
        form.addRow("约束", self._required_input)

        self._unique_input = QCheckBox("唯一")
        self._unique_input.setObjectName("field-unique-input")

        self._readonly_input = QCheckBox("只读")
        self._readonly_input.setObjectName("field-readonly-input")
        form.addRow("", self._unique_input)
        form.addRow("", self._readonly_input)

        self._default_input = QLineEdit()
        self._default_input.setObjectName("field-default-input")
        form.addRow("默认值", self._default_input)

        self._enum_id_input = QLineEdit()
        self._enum_id_input.setObjectName("field-enum-id-input")
        self._enum_id_input.setPlaceholderText("Enum ID")
        form.addRow("枚举", self._enum_id_input)

        self._target_table_input = QLineEdit()
        self._target_table_input.setObjectName("field-target-table-input")
        self._target_table_input.setPlaceholderText("目标表 ID")
        form.addRow("引用表", self._target_table_input)

        self._meta_id_input = QLineEdit()
        self._meta_id_input.setObjectName("field-meta-id-input")
        self._meta_id_input.setPlaceholderText("Meta ID")
        form.addRow("数据元", self._meta_id_input)

        self._description_input = QTextEdit()
        self._description_input.setObjectName("field-description-input")
        self._description_input.setFixedHeight(60)
        form.addRow("说明", self._description_input)

        root.addLayout(form)
        root.addStretch()

        # Populate type dropdown
        self._type_input.addItems([t.value for t in FieldType])
        self._set_conditional_visibility(FieldType.STRING)

        # Connect signals
        self._type_input.currentTextChanged.connect(self._on_type_changed)
        for widget in (
            self._name_input,
            self._display_name_input,
            self._default_input,
            self._enum_id_input,
            self._target_table_input,
            self._meta_id_input,
        ):
            widget.textChanged.connect(self._emit_modified)
        self._type_input.currentTextChanged.connect(self._emit_modified)
        self._required_input.toggled.connect(self._emit_modified)
        self._unique_input.toggled.connect(self._emit_modified)
        self._readonly_input.toggled.connect(self._emit_modified)
        self._description_input.textChanged.connect(self._emit_modified)

    def set_field(self, field: FieldDefinition | None, table_id: str = "") -> None:
        self._suppress_signal = True
        self._table_id = table_id
        self._field = field
        if field is None:
            self._clear_form()
            self._suppress_signal = False
            return
        self._field_id_input.setText(field.field_id)
        self._name_input.setText(field.name)
        self._display_name_input.setText(field.display_name)
        index = self._type_input.findText(field.field_type.value)
        if index >= 0:
            self._type_input.setCurrentIndex(index)
        self._required_input.setChecked(field.required)
        self._unique_input.setChecked(field.unique)
        self._readonly_input.setChecked(field.readonly)
        self._default_input.setText(str(field.default_value) if field.default_value is not None else "")
        self._enum_id_input.setText(field.enum_id)
        self._target_table_input.setText(field.target_table_id)
        self._meta_id_input.setText(field.meta_id)
        self._description_input.setPlainText(field.description)
        self._set_conditional_visibility(field.field_type)
        self._suppress_signal = False

    def set_field_types(self, types: list[FieldType]) -> None:
        current = self._type_input.currentText()
        self._type_input.clear()
        self._type_input.addItems([t.value for t in types])
        if current:
            index = self._type_input.findText(current)
            if index >= 0:
                self._type_input.setCurrentIndex(index)

    def clear(self) -> None:
        self._suppress_signal = True
        self._field = None
        self._table_id = ""
        self._clear_form()
        self._suppress_signal = False

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
        for child in self.findChildren(QComboBox):
            child.setEnabled(state not in {"disabled", "readonly"})
            child.setProperty("display-mode", "readonly" if state == "readonly" else "editable")
        for child in self.findChildren(QCheckBox):
            child.setEnabled(state not in {"disabled", "readonly"})
            child.setProperty("display-mode", "readonly" if state == "readonly" else "editable")

    def _on_type_changed(self, _type_str: str) -> None:
        try:
            field_type = FieldType(_type_str)
        except ValueError:
            return
        self._set_conditional_visibility(field_type)

    def _set_conditional_visibility(self, field_type: FieldType) -> None:
        """Show/hide type-specific fields."""
        row_enum = self._find_form_row(self._enum_id_input)
        row_target = self._find_form_row(self._target_table_input)
        row_meta = self._find_form_row(self._meta_id_input)
        for row in (row_enum, row_target, row_meta):
            if row is not None:
                row.setVisible(False)

        if field_type == FieldType.ENUM and row_enum is not None:
            row_enum.setVisible(True)
        elif field_type in {FieldType.REFERENCE, FieldType.LIST, FieldType.META}:
            if field_type == FieldType.REFERENCE and row_target is not None:
                row_target.setVisible(True)
            elif field_type == FieldType.META and row_meta is not None:
                row_meta.setVisible(True)

    def _find_form_row(self, widget) -> QWidget | None:
        layout = self.findChild(QFormLayout)
        if layout is None:
            return None
        for i in range(layout.rowCount()):
            if layout.itemAt(i, QFormLayout.ItemRole.FieldRole) and (
                layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget() is widget
            ):
                w = layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                if w and w.widget():
                    return w.widget().parentWidget()
        return None

    def _clear_form(self) -> None:
        self._field_id_input.clear()
        self._name_input.clear()
        self._display_name_input.clear()
        self._type_input.setCurrentIndex(0)
        self._required_input.setChecked(False)
        self._unique_input.setChecked(False)
        self._readonly_input.setChecked(False)
        self._default_input.clear()
        self._enum_id_input.clear()
        self._target_table_input.clear()
        self._meta_id_input.clear()
        self._description_input.clear()
        self._set_conditional_visibility(FieldType.STRING)
        self.setEnabled(False)

    def _emit_modified(self) -> None:
        if self._suppress_signal or self._field is None:
            return
        try:
            field_type = FieldType(self._type_input.currentText())
        except ValueError:
            return
        new_field = replace(
            self._field,
            name=self._name_input.text(),
            display_name=self._display_name_input.text(),
            field_type=field_type,
            required=self._required_input.isChecked(),
            unique=self._unique_input.isChecked(),
            readonly=self._readonly_input.isChecked(),
            default_value=self._default_input.text() or None,
            enum_id=self._enum_id_input.text(),
            target_table_id=self._target_table_input.text(),
            meta_id=self._meta_id_input.text(),
            description=self._description_input.toPlainText(),
        )
        self.fieldModified.emit(self._table_id, self._field.field_id, new_field)
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

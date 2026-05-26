from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QToolButton,
)

from xtable.domain.models import FieldDefinition, FieldType, NormalTableDefinition, ProjectSchema
from xtable.ui.components import (
    FieldInspector,
    InspectorPanel,
    JsonEditorShell,
    ListEditorShell,
    MetaEditorShell,
    PickerShell,
    PreviewTable,
    StructureEditor,
    TableExplorer,
    WorkspaceTabs,
)



def test_field_inspector_exposes_expected_inputs_without_business_binding():
    app = QApplication.instance() or QApplication([])

    inspector = FieldInspector(theme="dark")

    field = FieldDefinition(
        field_id="item_id",
        name="item_id",
        display_name="Item ID",
        field_type=FieldType.INT,
        required=True,
        description="Item config primary key",
    )
    inspector.set_field(field)

    assert inspector.objectName() == "field-inspector"
    assert inspector.findChild(QLineEdit, "field-name-input").text() == "item_id"
    assert inspector.findChild(QLineEdit, "field-id-input").text() == "item_id"
    assert inspector.findChild(QComboBox, "field-type-input").currentText() == "int"
    assert inspector.findChild(QCheckBox, "field-required-input").isChecked()
    assert inspector.findChild(QTextEdit, "field-description-input").toPlainText() == "Item config primary key"

    inspector.set_field_state("disabled")

    assert inspector.property("field-state") == "disabled"
    assert not inspector.findChild(QLineEdit, "field-name-input").isEnabled()

    # Clear should empty the form
    inspector.clear()
    assert inspector.findChild(QLineEdit, "field-name-input").text() == ""

    inspector.close()
    app.quit()


def test_field_inspector_emits_modified_signal():
    app = QApplication.instance() or QApplication([])

    inspector = FieldInspector()
    field = FieldDefinition(
        field_id="f1",
        name="f1",
        display_name="Field 1",
        field_type=FieldType.STRING,
    )
    inspector.set_field(field)

    results = []
    inspector.fieldModified.connect(lambda tid, fid, f: results.append((tid, fid, f)))

    inspector.findChild(QLineEdit, "field-name-input").setText("updated_name")

    assert len(results) > 0
    table_id, field_id, modified = results[-1]
    assert field_id == "f1"
    assert modified.name == "updated_name"

    inspector.close()
    app.quit()


def test_field_inspector_shows_conditional_fields_by_type():
    app = QApplication.instance() or QApplication([])

    inspector = FieldInspector()

    # ENUM type should show enum_id field
    enum_field = FieldDefinition(
        field_id="e1",
        name="e1",
        display_name="Enum",
        field_type=FieldType.ENUM,
        enum_id="quality",
    )
    inspector.set_field(enum_field)
    enum_input = inspector.findChild(QLineEdit, "field-enum-id-input")
    assert enum_input is not None
    assert enum_input.text() == "quality"

    # META type should show meta_id field
    meta_field = FieldDefinition(
        field_id="m1",
        name="m1",
        display_name="Meta",
        field_type=FieldType.META,
        meta_id="item_stats",
    )
    inspector.set_field(meta_field)
    meta_input = inspector.findChild(QLineEdit, "field-meta-id-input")
    assert meta_input is not None
    assert meta_input.text() == "item_stats"

    inspector.close()
    app.quit()


def test_field_editor_shells_cover_enum_reference_json_list_and_meta_states():
    app = QApplication.instance() or QApplication([])

    enum_picker = PickerShell("enum", "品质枚举", ["Common", "Rare", "Epic"], state="normal")
    reference_picker = PickerShell("reference", "引用表", ["items.item_id", "skills.skill_id"], state="readonly")
    json_editor = JsonEditorShell(state="invalid")
    list_editor = ListEditorShell(state="empty")
    meta_editor = MetaEditorShell(state="disabled")

    assert enum_picker.objectName() == "enum-picker-shell"
    assert enum_picker.property("field-state") == "normal"
    assert reference_picker.objectName() == "reference-picker-shell"
    assert reference_picker.property("field-state") == "readonly"
    assert json_editor.objectName() == "json-editor-shell"
    assert json_editor.property("field-state") == "invalid"

    # Json shell should validate and format
    assert json_editor.validate_json() is True  # default is valid
    json_editor.editor.setPlainText("invalid json")
    assert json_editor.validate_json() is False

    list_editor.close()
    meta_editor.close()
    json_editor.close()
    reference_picker.close()
    enum_picker.close()
    app.quit()



def test_workspace_tabs_open_and_close_documents():
    app = QApplication.instance() or QApplication([])

    tabs = WorkspaceTabs()
    tabs.open_document("items", "Items", dirty=False)
    tabs.open_document("skills", "Skills", dirty=False)
    assert tabs.document_count == 2

    tabs.close_document("items")
    assert tabs.document_count == 1

    tabs.close()
    app.quit()


def test_preview_table_supports_clipboard_copy_paste_and_state():
    app = QApplication.instance() or QApplication([])
    QApplication.clipboard().clear()

    table = PreviewTable()
    QApplication.clipboard().setText("A\tB")
    table.paste_tsv(QApplication.clipboard().text())

    table.set_demo_state("error")
    assert table.property("table-state") == "error"
    assert table.item(0, 3).data(Qt.ItemDataRole.UserRole) == "error"

    # Verify copy produces TSV
    table.setCurrentCell(0, 0)
    text = table.copy_selection()
    assert isinstance(text, str)

    table.close()
    app.quit()



# ── New Component Tests ──


def _make_sample_schema() -> ProjectSchema:
    schema = ProjectSchema()
    table1 = NormalTableDefinition(
        table_id="items",
        display_name="Items",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
            FieldDefinition(field_id="name", name="name", display_name="Name", field_type=FieldType.STRING),
            FieldDefinition(field_id="count", name="count", display_name="Count", field_type=FieldType.INT),
        ],
        primary_key="id",
    )
    table2 = NormalTableDefinition(
        table_id="skills",
        display_name="Skills",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
            FieldDefinition(field_id="name", name="name", display_name="Name", field_type=FieldType.STRING),
        ],
        primary_key="id",
    )
    schema.tables["items"] = table1
    schema.tables["skills"] = table2
    return schema


def test_table_explorer_initializes_with_no_schema():
    app = QApplication.instance() or QApplication([])
    explorer = TableExplorer()
    assert explorer.objectName() == "table-explorer"
    assert explorer.findChild(QListWidget, "table-explorer-list").count() == 0
    assert explorer.findChild(QPushButton, "table-explorer-add-button") is not None
    assert explorer.findChild(QPushButton, "table-explorer-delete-button") is not None
    explorer.close()
    app.quit()


def test_table_explorer_loads_and_lists_tables():
    app = QApplication.instance() or QApplication([])
    explorer = TableExplorer()
    schema = _make_sample_schema()
    explorer.load_schema(schema)
    list_widget = explorer.findChild(QListWidget, "table-explorer-list")
    assert list_widget.count() == 2
    assert list_widget.item(0).data(Qt.ItemDataRole.UserRole) == "items"
    assert list_widget.item(1).data(Qt.ItemDataRole.UserRole) == "skills"
    explorer.close()
    app.quit()


def test_table_explorer_select_emits_signal():
    app = QApplication.instance() or QApplication([])
    explorer = TableExplorer()
    explorer.load_schema(_make_sample_schema())

    results = []
    explorer.table_selected.connect(lambda tid: results.append(tid))
    explorer.set_selected("skills")
    assert "skills" in results
    explorer.close()
    app.quit()


def test_table_explorer_delete_removes_table():
    app = QApplication.instance() or QApplication([])
    explorer = TableExplorer()
    schema = _make_sample_schema()
    explorer.load_schema(schema)

    explorer.set_selected("skills")
    # Delete by modifying schema and reloading
    del schema.tables["skills"]
    explorer.load_schema(schema)
    assert explorer.findChild(QListWidget, "table-explorer-list").count() == 1
    assert explorer.findChild(QListWidget, "table-explorer-list").item(0).data(Qt.ItemDataRole.UserRole) == "items"

    explorer.close()
    app.quit()


def test_structure_editor_shows_table_params_and_field_list():
    app = QApplication.instance() or QApplication([])
    editor = StructureEditor()
    table = _make_sample_schema().tables["items"]

    editor.set_table(table)

    display_input = editor.findChild(QLineEdit, "structure-editor-display-name")
    assert display_input is not None
    assert display_input.text() == "Items"

    field_list = editor.findChild(QListWidget, "structure-editor-field-list")
    assert field_list.count() == 3

    editor.close()
    app.quit()


def test_structure_editor_field_selection_emits_signal():
    app = QApplication.instance() or QApplication([])
    editor = StructureEditor()
    table = _make_sample_schema().tables["items"]
    editor.set_table(table)

    results = []
    editor.field_focused.connect(lambda tid, fid: results.append((tid, fid)))

    field_list = editor.findChild(QListWidget, "structure-editor-field-list")
    field_list.setCurrentRow(1)

    assert len(results) == 1
    assert results[0] == ("items", "name")

    editor.close()
    app.quit()


def test_structure_editor_add_delete_field():
    app = QApplication.instance() or QApplication([])
    editor = StructureEditor()
    table = _make_sample_schema().tables["items"]
    editor.set_table(table)

    modified = []
    editor.schema_modified.connect(lambda tid: modified.append(tid))

    # Add field
    editor.findChild(QPushButton, "structure-editor-add-field-button").click()
    assert len(table.fields) == 4
    assert len(modified) == 1
    assert modified[-1] == "items"

    # Delete field
    field_list = editor.findChild(QListWidget, "structure-editor-field-list")
    field_list.setCurrentRow(3)
    editor.findChild(QPushButton, "structure-editor-delete-field-button").click()
    assert len(table.fields) == 3

    editor.close()
    app.quit()


def test_structure_editor_move_field_up_down():
    app = QApplication.instance() or QApplication([])
    editor = StructureEditor()
    table = _make_sample_schema().tables["items"]
    editor.set_table(table)

    field_list = editor.findChild(QListWidget, "structure-editor-field-list")
    field_list.setCurrentRow(1)  # "name"

    # Move field up
    editor.findChild(QPushButton, "structure-editor-up-button").click()
    assert field_list.currentRow() == 0
    assert table.fields[0].field_id == "name"

    # Move field down
    editor.findChild(QPushButton, "structure-editor-down-button").click()
    assert field_list.currentRow() == 1
    assert table.fields[1].field_id == "name"

    editor.close()
    app.quit()


def test_inspector_panel_shows_field_properties():
    app = QApplication.instance() or QApplication([])
    panel = InspectorPanel()
    assert panel.objectName() == "inspector-panel"

    field = FieldDefinition(
        field_id="f1",
        name="f1",
        display_name="Field 1",
        field_type=FieldType.INT,
    )
    panel.show_field("items", field)

    assert panel.isVisible()
    assert panel.has_content()

    panel.clear()
    assert not panel.isVisible()
    assert not panel.has_content()

    panel.close()
    app.quit()


def test_inspector_panel_empty_state():
    app = QApplication.instance() or QApplication([])
    panel = InspectorPanel()

    # When cleared, show empty state
    panel.clear()
    assert not panel.isVisible()
    assert not panel.has_content()

    label = panel.findChild(QLabel, "inspector-panel-empty")
    assert label is not None
    assert label.text() == InspectorPanel.EMPTY_LABEL

    panel.close()
    app.quit()


def test_table_explorer_add_creates_new_table():
    app = QApplication.instance() or QApplication([])
    explorer = TableExplorer()
    schema = _make_sample_schema()
    explorer.load_schema(schema)

    new_table = NormalTableDefinition(
        table_id="new_table",
        display_name="New Table",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, readonly=True),
        ],
        primary_key="id",
    )
    schema.tables["new_table"] = new_table
    explorer.load_schema(schema)
    explorer.set_selected("new_table")
    assert explorer.findChild(QListWidget, "table-explorer-list").count() == 3
    assert explorer.current_table_id() == "new_table"

    explorer.close()
    app.quit()

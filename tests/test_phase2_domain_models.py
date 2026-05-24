from __future__ import annotations

import pytest

from xtable.domain.models import (
    EnumDefinition,
    EnumItem,
    FieldDefinition,
    FieldType,
    FieldTypeDefinition,
    FieldTypeRegistry,
    MatrixTableDefinition,
    MetaDefinition,
    NormalTableDefinition,
    ProjectSchema,
    TableRow,
    TableType,
    TableTypeDefinition,
    TableTypeRegistry,
)


def test_project_schema_registers_tables_enums_meta_and_resolves_references():
    quality = EnumDefinition(
        enum_id="item_quality",
        display_name="Item Quality",
        items=[
            EnumItem(item_id="common", display_name="Common", export_value=1, sort_order=1),
            EnumItem(item_id="epic", display_name="Epic", export_value=4, sort_order=2),
        ],
        default_item_id="common",
    )
    reward_meta = MetaDefinition(
        meta_id="reward",
        display_name="Reward",
        fields=[
            FieldDefinition(field_id="item_id", name="item_id", display_name="Item", field_type=FieldType.REFERENCE, target_table_id="items"),
            FieldDefinition(field_id="count", name="count", display_name="Count", field_type=FieldType.INT, required=True),
        ],
    )
    items = NormalTableDefinition(
        table_id="items",
        display_name="Items",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, required=True, unique=True),
            FieldDefinition(field_id="quality", name="quality", display_name="Quality", field_type=FieldType.ENUM, enum_id="item_quality"),
            FieldDefinition(field_id="reward", name="reward", display_name="Reward", field_type=FieldType.META, meta_id="reward"),
        ],
        rows=[TableRow(values={"id": 1001, "quality": "epic"})],
        primary_key="id",
        feature_keys=("quality",),
    )

    schema = ProjectSchema()
    schema.add_enum(quality)
    schema.add_meta(reward_meta)
    schema.add_table(items)

    assert schema.table("items") is items
    assert schema.enum("item_quality").item("epic").export_value == 4
    assert schema.meta("reward") is reward_meta
    assert schema.resolve_field_reference(items.field("quality")) is quality
    assert schema.resolve_field_reference(items.field("reward")) is reward_meta


def test_schema_rejects_duplicate_ids_and_missing_field_references():
    schema = ProjectSchema()
    first = NormalTableDefinition(
        table_id="items",
        display_name="Items",
        fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID)],
    )
    schema.add_table(first)

    with pytest.raises(ValueError, match="Duplicate table_id"):
        schema.add_table(first)

    with pytest.raises(KeyError, match="missing"):
        first.field("missing")


def test_group_and_matrix_tables_expose_specialized_parameters():
    group_table = NormalTableDefinition.grouped(
        table_id="drops",
        display_name="Drops",
        group_key="group_id",
        fields=[
            FieldDefinition(field_id="group_id", name="group_id", display_name="Group", field_type=FieldType.STRING),
            FieldDefinition(field_id="item_id", name="item_id", display_name="Item", field_type=FieldType.REFERENCE, target_table_id="items"),
        ],
    )
    matrix = MatrixTableDefinition(
        table_id="growth",
        display_name="Growth",
        fields=[
            FieldDefinition(field_id="level", name="level", display_name="Level", field_type=FieldType.INT),
            FieldDefinition(field_id="quality", name="quality", display_name="Quality", field_type=FieldType.ENUM, enum_id="item_quality"),
            FieldDefinition(field_id="value", name="value", display_name="Value", field_type=FieldType.FLOAT),
        ],
        x_axis="level",
        y_axis="quality",
        value_field="value",
    )

    assert group_table.table_type == TableType.GROUP
    assert group_table.group_key == "group_id"
    assert matrix.table_type == TableType.MATRIX
    assert matrix.axis_fields == ("level", "quality", "value")


def test_domain_models_do_not_depend_on_qt():
    import xtable.domain.models as models

    assert "PySide6" not in models.__dict__


def test_type_registries_expose_supported_field_and_table_types():
    field_registry = FieldTypeRegistry.mvp()
    table_registry = TableTypeRegistry.mvp()

    assert field_registry.get(FieldType.JSON).display_name == "Json"
    assert field_registry.get(FieldType.META).supports_reference is True
    assert table_registry.get(TableType.NORMAL).display_name == "普通表"
    assert table_registry.get(TableType.GROUP).required_parameters == ("group_key",)
    assert table_registry.get(TableType.MATRIX).required_parameters == ("x_axis", "y_axis", "value_field")

    custom_field_registry = FieldTypeRegistry()
    custom_field_registry.register(
        FieldTypeDefinition(
            field_type=FieldType.STRING,
            display_name="Duplicate",
            storage_shape="text",
            editor_kind="line_edit",
        )
    )

    with pytest.raises(ValueError, match="Duplicate field type"):
        custom_field_registry.register(
            FieldTypeDefinition(
                field_type=FieldType.STRING,
                display_name="Duplicate",
                storage_shape="text",
                editor_kind="line_edit",
            )
        )

    with pytest.raises(ValueError, match="Duplicate table type"):
        table_registry.register(
            TableTypeDefinition(
                table_type=TableType.NORMAL,
                display_name="Duplicate",
                required_parameters=(),
            )
        )


def test_schema_rejects_missing_enum_reference_meta_reference_and_table_reference():
    schema = ProjectSchema()

    with pytest.raises(ValueError, match="missing_enum"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[
                    FieldDefinition(
                        field_id="quality",
                        name="quality",
                        display_name="Quality",
                        field_type=FieldType.ENUM,
                        enum_id="missing_enum",
                    )
                ],
            )
        )

    with pytest.raises(ValueError, match="missing_meta"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[
                    FieldDefinition(
                        field_id="reward",
                        name="reward",
                        display_name="Reward",
                        field_type=FieldType.META,
                        meta_id="missing_meta",
                    )
                ],
            )
        )

    with pytest.raises(ValueError, match="missing_table"):
        schema.add_table(
            NormalTableDefinition(
                table_id="orders",
                display_name="Orders",
                fields=[
                    FieldDefinition(
                        field_id="item_id",
                        name="item_id",
                        display_name="Item",
                        field_type=FieldType.REFERENCE,
                        target_table_id="missing_table",
                    )
                ],
            )
        )


def test_schema_rejects_invalid_table_keys_and_matrix_axis_fields():
    schema = ProjectSchema()

    with pytest.raises(ValueError, match="primary_key"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID)],
                primary_key="missing_id",
            )
        )

    with pytest.raises(ValueError, match="feature_keys"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID)],
                feature_keys=("missing_feature",),
            )
        )

    with pytest.raises(ValueError, match="group_key"):
        schema.add_table(
            NormalTableDefinition.grouped(
                table_id="drops",
                display_name="Drops",
                group_key="missing_group",
                fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID)],
            )
        )

    with pytest.raises(ValueError, match="axis"):
        schema.add_table(
            MatrixTableDefinition(
                table_id="growth",
                display_name="Growth",
                fields=[
                    FieldDefinition(field_id="level", name="level", display_name="Level", field_type=FieldType.INT),
                    FieldDefinition(field_id="value", name="value", display_name="Value", field_type=FieldType.FLOAT),
                ],
                x_axis="level",
                y_axis="level",
                value_field="value",
            )
        )


def test_schema_rejects_invalid_enum_and_meta_shapes():
    schema = ProjectSchema()

    with pytest.raises(ValueError, match="export_value"):
        schema.add_enum(
            EnumDefinition(
                enum_id="quality",
                display_name="Quality",
                items=[
                    EnumItem(item_id="common", display_name="Common", export_value=1, sort_order=1),
                    EnumItem(item_id="rare", display_name="Rare", export_value=1, sort_order=2),
                ],
            )
        )

    with pytest.raises(ValueError, match="default_item_id"):
        schema.add_enum(
            EnumDefinition(
                enum_id="quality",
                display_name="Quality",
                items=[EnumItem(item_id="common", display_name="Common", export_value=1, sort_order=1)],
                default_item_id="missing",
            )
        )

    with pytest.raises(ValueError, match="deprecated"):
        schema.add_enum(
            EnumDefinition(
                enum_id="quality",
                display_name="Quality",
                items=[EnumItem(item_id="old", display_name="Old", export_value=1, sort_order=1, deprecated=True)],
                default_item_id="old",
            )
        )

    with pytest.raises(ValueError, match="field name"):
        schema.add_meta(
            MetaDefinition(
                meta_id="reward",
                display_name="Reward",
                fields=[
                    FieldDefinition(field_id="item", name="value", display_name="Item", field_type=FieldType.STRING),
                    FieldDefinition(field_id="count", name="value", display_name="Count", field_type=FieldType.INT),
                ],
            )
        )


def test_schema_rejects_unknown_row_fields_missing_required_fields_and_bad_basic_types():
    schema = ProjectSchema()

    with pytest.raises(ValueError, match="unknown field"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.INT)],
                rows=[TableRow(values={"id": 1001, "unknown": "extra"})],
            )
        )

    with pytest.raises(ValueError, match="required"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.INT, required=True)],
                rows=[TableRow(values={})],
            )
        )

    with pytest.raises(ValueError, match="expected int"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.INT)],
                rows=[TableRow(values={"id": "1001"})],
            )
        )


def test_schema_rejects_field_type_parameter_mismatches():
    schema = ProjectSchema()
    schema.add_enum(
        EnumDefinition(
            enum_id="quality",
            display_name="Quality",
            items=[EnumItem(item_id="common", display_name="Common", export_value=1, sort_order=1)],
        )
    )

    with pytest.raises(ValueError, match="enum_id"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[FieldDefinition(field_id="quality", name="quality", display_name="Quality", field_type=FieldType.ENUM)],
            )
        )

    with pytest.raises(ValueError, match="element_type"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[FieldDefinition(field_id="tags", name="tags", display_name="Tags", field_type=FieldType.LIST)],
            )
        )

    with pytest.raises(ValueError, match="reference parameters"):
        schema.add_table(
            NormalTableDefinition(
                table_id="items",
                display_name="Items",
                fields=[
                    FieldDefinition(
                        field_id="name",
                        name="name",
                        display_name="Name",
                        field_type=FieldType.STRING,
                        enum_id="quality",
                    )
                ],
            )
        )


def test_schema_rejects_missing_reference_target_field_and_validates_meta_references():
    schema = ProjectSchema()
    schema.add_table(
        NormalTableDefinition(
            table_id="items",
            display_name="Items",
            fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID)],
        )
    )

    with pytest.raises(ValueError, match="missing_field"):
        schema.add_table(
            NormalTableDefinition(
                table_id="orders",
                display_name="Orders",
                fields=[
                    FieldDefinition(
                        field_id="item_id",
                        name="item_id",
                        display_name="Item",
                        field_type=FieldType.REFERENCE,
                        target_table_id="items",
                        target_field_id="missing_field",
                    )
                ],
            )
        )

    schema.add_meta(
        MetaDefinition(
            meta_id="reward",
            display_name="Reward",
            fields=[
                FieldDefinition(
                    field_id="item",
                    name="item",
                    display_name="Item",
                    field_type=FieldType.REFERENCE,
                    target_table_id="items",
                    target_field_id="id",
                )
            ],
        )
    )
    schema.validate_structure()

    broken = ProjectSchema()
    broken.add_meta(
        MetaDefinition(
            meta_id="reward",
            display_name="Reward",
            fields=[
                FieldDefinition(
                    field_id="item",
                    name="item",
                    display_name="Item",
                    field_type=FieldType.REFERENCE,
                    target_table_id="missing_items",
                )
            ],
        )
    )

    with pytest.raises(ValueError, match="missing_items"):
        broken.validate_structure()

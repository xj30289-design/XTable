from __future__ import annotations

import pytest

from xtable.domain.models import (
    EnumDefinition,
    EnumItem,
    FieldDefinition,
    FieldType,
    GroupTableDefinition,
    MatrixTableDefinition,
    MetaDefinition,
    NormalTableDefinition,
    ProjectSchema,
    TableRow,
)
from xtable.domain.serialization import migrate_project_schema_dict, project_schema_from_dict, project_schema_to_dict


def build_sample_schema() -> ProjectSchema:
    schema = ProjectSchema()
    schema.add_enum(
        EnumDefinition(
            enum_id="quality",
            display_name="Quality",
            items=[
                EnumItem(item_id="common", display_name="Common", export_value=1, sort_order=1),
                EnumItem(item_id="rare", display_name="Rare", export_value=2, sort_order=2),
            ],
            default_item_id="common",
            export_name="quality",
        )
    )
    schema.add_meta(
        MetaDefinition(
            meta_id="reward",
            display_name="Reward",
            fields=[
                FieldDefinition(field_id="count", name="count", display_name="Count", field_type=FieldType.INT, required=True),
                FieldDefinition(field_id="tags", name="tags", display_name="Tags", field_type=FieldType.LIST, element_type=FieldType.STRING),
            ],
            references=("items",),
        )
    )
    schema.add_table(
        NormalTableDefinition(
            table_id="items",
            display_name="Items",
            fields=[
                FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID, required=True, unique=True),
                FieldDefinition(field_id="quality", name="quality", display_name="Quality", field_type=FieldType.ENUM, enum_id="quality"),
                FieldDefinition(field_id="reward", name="reward", display_name="Reward", field_type=FieldType.META, meta_id="reward"),
            ],
            rows=[TableRow(values={"id": 1001, "quality": "rare"})],
            primary_key="id",
            feature_keys=("quality",),
            tags=("gameplay",),
        )
    )
    schema.add_table(
        GroupTableDefinition(
            table_id="drops",
            display_name="Drops",
            fields=[
                FieldDefinition(field_id="group_id", name="group_id", display_name="Group", field_type=FieldType.STRING),
                FieldDefinition(
                    field_id="item_id",
                    name="item_id",
                    display_name="Item",
                    field_type=FieldType.REFERENCE,
                    target_table_id="items",
                    target_field_id="id",
                ),
            ],
            group_key="group_id",
            group_sort="name",
        )
    )
    schema.add_table(
        MatrixTableDefinition(
            table_id="growth",
            display_name="Growth",
            fields=[
                FieldDefinition(field_id="level", name="level", display_name="Level", field_type=FieldType.INT),
                FieldDefinition(field_id="quality", name="quality", display_name="Quality", field_type=FieldType.ENUM, enum_id="quality"),
                FieldDefinition(field_id="value", name="value", display_name="Value", field_type=FieldType.FLOAT),
            ],
            x_axis="level",
            y_axis="quality",
            value_field="value",
        )
    )
    return schema


def test_project_schema_round_trips_through_dict():
    schema = build_sample_schema()

    payload = project_schema_to_dict(schema)
    restored = project_schema_from_dict(payload)

    assert payload["schema_format_version"] == 1
    assert restored.table("items").field("quality").field_type is FieldType.ENUM
    assert restored.table("items").feature_keys == ("quality",)
    assert restored.table("items").tags == ("gameplay",)
    assert restored.table("items").rows[0].values == {"id": 1001, "quality": "rare"}
    assert isinstance(restored.table("drops"), GroupTableDefinition)
    assert restored.table("drops").group_key == "group_id"
    assert isinstance(restored.table("growth"), MatrixTableDefinition)
    assert restored.table("growth").axis_fields == ("level", "quality", "value")
    assert restored.meta("reward").field("tags").element_type is FieldType.STRING
    assert restored.enum("quality").default_item_id == "common"


def test_project_schema_from_dict_rejects_unknown_field_and_table_types():
    schema = build_sample_schema()
    payload = project_schema_to_dict(schema)
    payload["tables"][0]["fields"][0]["field_type"] = "missing_type"

    with pytest.raises(ValueError, match="Unknown field_type"):
        project_schema_from_dict(payload)

    payload = project_schema_to_dict(schema)
    payload["tables"][0]["table_type"] = "missing_table_type"

    with pytest.raises(ValueError, match="Unknown table_type"):
        project_schema_from_dict(payload)


def test_project_schema_codec_rejects_unsupported_format_version():
    payload = project_schema_to_dict(build_sample_schema())
    payload["schema_format_version"] = 999

    with pytest.raises(ValueError, match="Unsupported schema_format_version"):
        project_schema_from_dict(payload)


def test_project_schema_from_dict_migrates_legacy_version_zero_payloads():
    legacy_payload = project_schema_to_dict(build_sample_schema())
    legacy_payload["version"] = 0
    legacy_payload.pop("schema_format_version")
    for table in legacy_payload["tables"]:
        table.pop("table_type")

    migrated = migrate_project_schema_dict(legacy_payload)
    restored = project_schema_from_dict(legacy_payload)

    assert migrated["schema_format_version"] == 1
    assert all(table["table_type"] == "normal_table" for table in migrated["tables"])
    assert restored.table("items").field("quality").enum_id == "quality"


def test_project_schema_rejects_meta_reference_cycles():
    schema = ProjectSchema()
    schema.add_meta(
        MetaDefinition(
            meta_id="a",
            display_name="A",
            fields=[FieldDefinition(field_id="b", name="b", display_name="B", field_type=FieldType.META, meta_id="b")],
        )
    )
    schema.add_meta(
        MetaDefinition(
            meta_id="b",
            display_name="B",
            fields=[FieldDefinition(field_id="a", name="a", display_name="A", field_type=FieldType.META, meta_id="a")],
        )
    )

    with pytest.raises(ValueError, match="Meta reference cycle"):
        schema.validate_structure()


def test_project_schema_reports_table_reference_cycles_without_rejecting_them():
    schema = ProjectSchema()
    items = NormalTableDefinition(
        table_id="items",
        display_name="Items",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID),
        ],
    )
    characters = NormalTableDefinition(
        table_id="characters",
        display_name="Characters",
        fields=[
            FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID),
            FieldDefinition(
                field_id="weapon_id",
                name="weapon_id",
                display_name="Weapon",
                field_type=FieldType.REFERENCE,
                target_table_id="items",
                target_field_id="id",
            ),
        ],
    )
    schema.add_table(items)
    schema.add_table(characters)
    items.fields.append(
        FieldDefinition(
            field_id="owner_id",
            name="owner_id",
            display_name="Owner",
            field_type=FieldType.REFERENCE,
            target_table_id="characters",
            target_field_id="id",
        )
    )

    assert schema.table_reference_graph() == {
        "items": {"characters"},
        "characters": {"items"},
    }
    assert schema.find_table_reference_cycles() == (("characters", "items", "characters"),)
    schema.validate_structure()


def test_project_schema_from_dict_allows_table_reference_cycles_to_load():
    schema = ProjectSchema()
    schema.add_table(
        NormalTableDefinition(
            table_id="items",
            display_name="Items",
            fields=[
                FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID),
            ],
        )
    )
    schema.add_table(
        NormalTableDefinition(
            table_id="characters",
            display_name="Characters",
            fields=[
                FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID),
                FieldDefinition(
                    field_id="weapon_id",
                    name="weapon_id",
                    display_name="Weapon",
                    field_type=FieldType.REFERENCE,
                    target_table_id="items",
                    target_field_id="id",
                ),
            ],
        )
    )
    schema.table("items").fields.append(
        FieldDefinition(
            field_id="owner_id",
            name="owner_id",
            display_name="Owner",
            field_type=FieldType.REFERENCE,
            target_table_id="characters",
            target_field_id="id",
        )
    )
    payload = project_schema_to_dict(schema)

    restored = project_schema_from_dict(payload)

    assert restored.find_table_reference_cycles() == (("characters", "items", "characters"),)

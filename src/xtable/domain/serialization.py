from __future__ import annotations

from copy import deepcopy
from typing import Any

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
    TableDefinition,
    TableRow,
    TableType,
)


SCHEMA_FORMAT_VERSION = 1


def project_schema_to_dict(schema: ProjectSchema) -> dict[str, Any]:
    return {
        "schema_format_version": SCHEMA_FORMAT_VERSION,
        "enums": [_enum_to_dict(enum) for enum in schema.enums.values()],
        "metas": [_meta_to_dict(meta) for meta in schema.metas.values()],
        "tables": [_table_to_dict(table) for table in schema.tables.values()],
    }


def project_schema_from_dict(data: dict[str, Any]) -> ProjectSchema:
    data = migrate_project_schema_dict(data)
    version = data.get("schema_format_version")
    if version != SCHEMA_FORMAT_VERSION:
        raise ValueError(f"Unsupported schema_format_version: {version}")

    schema = ProjectSchema()
    for enum_data in data.get("enums", []):
        schema.add_enum(_enum_from_dict(enum_data))
    for meta_data in data.get("metas", []):
        schema.add_meta(_meta_from_dict(meta_data))
    for table in [_table_from_dict(table_data) for table_data in data.get("tables", [])]:
        if table.table_id in schema.tables:
            raise ValueError(f"Duplicate table_id: {table.table_id}")
        schema.tables[table.table_id] = table
    schema.validate_structure()
    return schema


def migrate_project_schema_dict(data: dict[str, Any]) -> dict[str, Any]:
    migrated = deepcopy(data)
    version = migrated.get("schema_format_version")
    if version == SCHEMA_FORMAT_VERSION:
        return migrated
    if version is None and migrated.get("version", 0) == 0:
        migrated["schema_format_version"] = SCHEMA_FORMAT_VERSION
        migrated.pop("version", None)
        for table_data in migrated.get("tables", []):
            table_data.setdefault("table_type", TableType.NORMAL.value)
        return migrated
    raise ValueError(f"Unsupported schema_format_version: {version}")


def _field_to_dict(field: FieldDefinition) -> dict[str, Any]:
    return {
        "field_id": field.field_id,
        "name": field.name,
        "display_name": field.display_name,
        "field_type": field.field_type.value,
        "description": field.description,
        "default_value": field.default_value,
        "required": field.required,
        "unique": field.unique,
        "readonly": field.readonly,
        "value_range": list(field.value_range) if field.value_range is not None else None,
        "export_name": field.export_name,
        "validation_rules": list(field.validation_rules),
        "enum_id": field.enum_id,
        "target_table_id": field.target_table_id,
        "target_field_id": field.target_field_id,
        "element_type": field.element_type.value if field.element_type is not None else None,
        "meta_id": field.meta_id,
    }


def _field_from_dict(data: dict[str, Any]) -> FieldDefinition:
    try:
        field_type = FieldType(data["field_type"])
    except ValueError as error:
        raise ValueError(f"Unknown field_type: {data.get('field_type')}") from error

    element_type = data.get("element_type")
    try:
        resolved_element_type = FieldType(element_type) if element_type is not None else None
    except ValueError as error:
        raise ValueError(f"Unknown element_type: {element_type}") from error

    value_range = data.get("value_range")
    return FieldDefinition(
        field_id=data["field_id"],
        name=data["name"],
        display_name=data["display_name"],
        field_type=field_type,
        description=data.get("description", ""),
        default_value=data.get("default_value"),
        required=bool(data.get("required", False)),
        unique=bool(data.get("unique", False)),
        readonly=bool(data.get("readonly", False)),
        value_range=tuple(value_range) if value_range is not None else None,
        export_name=data.get("export_name", ""),
        validation_rules=tuple(data.get("validation_rules", ())),
        enum_id=data.get("enum_id", ""),
        target_table_id=data.get("target_table_id", ""),
        target_field_id=data.get("target_field_id", ""),
        element_type=resolved_element_type,
        meta_id=data.get("meta_id", ""),
    )


def _row_to_dict(row: TableRow) -> dict[str, Any]:
    return {"values": row.values}


def _row_from_dict(data: dict[str, Any]) -> TableRow:
    return TableRow(values=dict(data.get("values", {})))


def _table_to_dict(table: TableDefinition) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "table_id": table.table_id,
        "display_name": table.display_name,
        "description": table.description,
        "table_type": table.table_type.value,
        "fields": [_field_to_dict(field) for field in table.fields],
        "rows": [_row_to_dict(row) for row in table.rows],
        "primary_key": table.primary_key,
        "feature_keys": list(table.feature_keys),
        "tags": list(table.tags),
        "source_path": table.source_path,
        "encoding": table.encoding,
        "last_modified_at": table.last_modified_at,
    }
    if isinstance(table, NormalTableDefinition):
        payload.update(
            {
                "default_sort_field": table.default_sort_field,
                "readonly_fields": list(table.readonly_fields),
            }
        )
    if isinstance(table, GroupTableDefinition):
        payload.update(
            {
                "group_key": table.group_key,
                "group_sort": table.group_sort,
                "group_boundary_style": table.group_boundary_style,
                "allow_non_contiguous_group": table.allow_non_contiguous_group,
            }
        )
    if isinstance(table, MatrixTableDefinition):
        payload.update(
            {
                "x_axis": table.x_axis,
                "y_axis": table.y_axis,
                "value_field": table.value_field,
                "x_axis_label": table.x_axis_label,
                "y_axis_label": table.y_axis_label,
                "axis_order": table.axis_order,
                "missing_cell_policy": table.missing_cell_policy,
                "duplicate_cell_policy": table.duplicate_cell_policy,
            }
        )
    return payload


def _table_from_dict(data: dict[str, Any]) -> TableDefinition:
    try:
        table_type = TableType(data.get("table_type", TableType.NORMAL.value))
    except ValueError as error:
        raise ValueError(f"Unknown table_type: {data.get('table_type')}") from error

    common = {
        "table_id": data["table_id"],
        "display_name": data["display_name"],
        "fields": [_field_from_dict(field) for field in data.get("fields", [])],
        "rows": [_row_from_dict(row) for row in data.get("rows", [])],
        "description": data.get("description", ""),
        "primary_key": data.get("primary_key", ""),
        "feature_keys": tuple(data.get("feature_keys", ())),
        "tags": tuple(data.get("tags", ())),
        "source_path": data.get("source_path", ""),
        "encoding": data.get("encoding", ""),
        "last_modified_at": data.get("last_modified_at", ""),
    }
    if table_type == TableType.GROUP:
        return GroupTableDefinition(
            **common,
            group_key=data.get("group_key", ""),
            group_sort=data.get("group_sort", "original"),
            group_boundary_style=data.get("group_boundary_style", "section"),
            allow_non_contiguous_group=bool(data.get("allow_non_contiguous_group", False)),
        )
    if table_type == TableType.MATRIX:
        return MatrixTableDefinition(
            **common,
            x_axis=data.get("x_axis", ""),
            y_axis=data.get("y_axis", ""),
            value_field=data.get("value_field", ""),
            x_axis_label=data.get("x_axis_label", ""),
            y_axis_label=data.get("y_axis_label", ""),
            axis_order=data.get("axis_order", "field"),
            missing_cell_policy=data.get("missing_cell_policy", "error"),
            duplicate_cell_policy=data.get("duplicate_cell_policy", "error"),
        )
    return NormalTableDefinition(
        **common,
        default_sort_field=data.get("default_sort_field", ""),
        readonly_fields=tuple(data.get("readonly_fields", ())),
    )


def _enum_to_dict(enum: EnumDefinition) -> dict[str, Any]:
    return {
        "enum_id": enum.enum_id,
        "display_name": enum.display_name,
        "description": enum.description,
        "default_item_id": enum.default_item_id,
        "allow_deprecated_display": enum.allow_deprecated_display,
        "export_name": enum.export_name,
        "created_at": enum.created_at,
        "updated_at": enum.updated_at,
        "items": [
            {
                "item_id": item.item_id,
                "display_name": item.display_name,
                "export_value": item.export_value,
                "sort_order": item.sort_order,
                "description": item.description,
                "deprecated": item.deprecated,
                "deprecated_reason": item.deprecated_reason,
                "updated_by": item.updated_by,
                "updated_at": item.updated_at,
            }
            for item in enum.items
        ],
    }


def _enum_from_dict(data: dict[str, Any]) -> EnumDefinition:
    return EnumDefinition(
        enum_id=data["enum_id"],
        display_name=data["display_name"],
        items=[
            EnumItem(
                item_id=item["item_id"],
                display_name=item["display_name"],
                export_value=item.get("export_value"),
                sort_order=int(item.get("sort_order", 0)),
                description=item.get("description", ""),
                deprecated=bool(item.get("deprecated", False)),
                deprecated_reason=item.get("deprecated_reason", ""),
                updated_by=item.get("updated_by", ""),
                updated_at=item.get("updated_at", ""),
            )
            for item in data.get("items", [])
        ],
        description=data.get("description", ""),
        default_item_id=data.get("default_item_id", ""),
        allow_deprecated_display=bool(data.get("allow_deprecated_display", True)),
        export_name=data.get("export_name", ""),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
    )


def _meta_to_dict(meta: MetaDefinition) -> dict[str, Any]:
    return {
        "meta_id": meta.meta_id,
        "display_name": meta.display_name,
        "description": meta.description,
        "export_name": meta.export_name,
        "max_depth": meta.max_depth,
        "complexity_threshold": meta.complexity_threshold,
        "references": list(meta.references),
        "created_at": meta.created_at,
        "updated_at": meta.updated_at,
        "fields": [_field_to_dict(field) for field in meta.fields],
    }


def _meta_from_dict(data: dict[str, Any]) -> MetaDefinition:
    return MetaDefinition(
        meta_id=data["meta_id"],
        display_name=data["display_name"],
        fields=[_field_from_dict(field) for field in data.get("fields", [])],
        description=data.get("description", ""),
        export_name=data.get("export_name", ""),
        max_depth=int(data.get("max_depth", 3)),
        complexity_threshold=data.get("complexity_threshold"),
        references=tuple(data.get("references", ())),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
    )

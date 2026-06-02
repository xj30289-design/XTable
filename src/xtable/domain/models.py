from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FieldType(StrEnum):
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    ENUM = "enum"
    ID = "id"
    REFERENCE = "reference"
    LIST = "list"
    META = "meta"
    JSON = "json"


class TableType(StrEnum):
    NORMAL = "normal_table"
    GROUP = "group_table"
    MATRIX = "matrix_table"


@dataclass(frozen=True)
class FieldTypeDefinition:
    field_type: FieldType
    display_name: str
    storage_shape: str
    editor_kind: str
    supports_reference: bool = False
    supports_range: bool = False
    supports_unique: bool = False
    supports_required: bool = True


@dataclass(frozen=True)
class TableTypeDefinition:
    table_type: TableType
    display_name: str
    required_parameters: tuple[str, ...]
    supports_primary_key: bool = True
    supports_feature_keys: bool = True


class FieldTypeRegistry:
    def __init__(self) -> None:
        self.definitions: dict[FieldType, FieldTypeDefinition] = {}

    @classmethod
    def mvp(cls) -> FieldTypeRegistry:
        registry = cls()
        for definition in (
            FieldTypeDefinition(FieldType.STRING, "字符串", "text", "line_edit", supports_range=True, supports_unique=True),
            FieldTypeDefinition(FieldType.INT, "整数", "integer", "number_input", supports_range=True, supports_unique=True),
            FieldTypeDefinition(FieldType.FLOAT, "浮点数", "number", "number_input", supports_range=True),
            FieldTypeDefinition(FieldType.BOOL, "布尔值", "boolean", "checkbox"),
            FieldTypeDefinition(FieldType.ENUM, "枚举", "enum_item_id", "picker", supports_reference=True),
            FieldTypeDefinition(FieldType.ID, "ID", "stable_id", "line_edit", supports_unique=True),
            FieldTypeDefinition(FieldType.REFERENCE, "引用", "foreign_key", "reference_picker", supports_reference=True),
            FieldTypeDefinition(FieldType.LIST, "列表", "array", "list_editor"),
            FieldTypeDefinition(FieldType.META, "Meta", "object", "meta_editor", supports_reference=True),
            FieldTypeDefinition(FieldType.JSON, "Json", "json", "json_editor"),
        ):
            registry.register(definition)
        return registry

    def register(self, definition: FieldTypeDefinition) -> None:
        if definition.field_type in self.definitions:
            raise ValueError(f"Duplicate field type: {definition.field_type}")
        self.definitions[definition.field_type] = definition

    def get(self, field_type: FieldType) -> FieldTypeDefinition:
        return self.definitions[field_type]


class TableTypeRegistry:
    def __init__(self) -> None:
        self.definitions: dict[TableType, TableTypeDefinition] = {}

    @classmethod
    def mvp(cls) -> TableTypeRegistry:
        registry = cls()
        for definition in (
            TableTypeDefinition(TableType.NORMAL, "普通表", ()),
            TableTypeDefinition(TableType.GROUP, "分组表", ("group_key",)),
            TableTypeDefinition(TableType.MATRIX, "二维表", ("x_axis", "y_axis", "value_field"), supports_primary_key=False, supports_feature_keys=False),
        ):
            registry.register(definition)
        return registry

    def register(self, definition: TableTypeDefinition) -> None:
        if definition.table_type in self.definitions:
            raise ValueError(f"Duplicate table type: {definition.table_type}")
        self.definitions[definition.table_type] = definition

    def get(self, table_type: TableType) -> TableTypeDefinition:
        return self.definitions[table_type]


@dataclass(frozen=True)
class FieldDefinition:
    field_id: str
    name: str
    display_name: str
    field_type: FieldType
    description: str = ""
    default_value: Any = None
    required: bool = False
    unique: bool = False
    readonly: bool = False
    value_range: tuple[Any, Any] | None = None
    export_name: str = ""
    validation_rules: tuple[str, ...] = ()
    enum_id: str = ""
    target_table_id: str = ""
    target_field_id: str = ""
    element_type: FieldType | None = None
    meta_id: str = ""

    @property
    def resolved_export_name(self) -> str:
        return self.export_name or self.name

    def validate_shape(self) -> None:
        reference_parameters = {
            "enum_id": self.enum_id,
            "target_table_id": self.target_table_id,
            "target_field_id": self.target_field_id,
            "meta_id": self.meta_id,
        }
        if self.field_type == FieldType.ENUM:
            if not self.enum_id:
                raise ValueError(f"Field {self.field_id} requires enum_id")
            self._assert_no_reference_parameters({"enum_id"})
            return
        if self.field_type == FieldType.REFERENCE:
            if not self.target_table_id:
                raise ValueError(f"Field {self.field_id} requires target_table_id")
            self._assert_no_reference_parameters({"target_table_id", "target_field_id"})
            return
        if self.field_type == FieldType.LIST:
            if self.element_type is None:
                raise ValueError(f"Field {self.field_id} requires element_type")
            self._assert_no_reference_parameters(set())
            return
        if self.field_type == FieldType.META:
            if not self.meta_id:
                raise ValueError(f"Field {self.field_id} requires meta_id")
            self._assert_no_reference_parameters({"meta_id"})
            return
        if any(reference_parameters.values()) or self.element_type is not None:
            raise ValueError(f"Field {self.field_id} has invalid reference parameters")

    def _assert_no_reference_parameters(self, allowed: set[str]) -> None:
        values = {
            "enum_id": self.enum_id,
            "target_table_id": self.target_table_id,
            "target_field_id": self.target_field_id,
            "meta_id": self.meta_id,
        }
        invalid = [name for name, value in values.items() if value and name not in allowed]
        if invalid:
            raise ValueError(f"Field {self.field_id} has invalid reference parameters: {', '.join(invalid)}")


@dataclass(frozen=True)
class TableRow:
    values: dict[str, Any] = field(default_factory=dict)

    def value_for(self, field_name: str, default: Any = None) -> Any:
        return self.values.get(field_name, default)


@dataclass
class TableDefinition:
    table_id: str
    display_name: str
    fields: list[FieldDefinition]
    rows: list[TableRow] = field(default_factory=list)
    description: str = ""
    primary_key: str = ""
    feature_keys: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    source_path: str = ""
    encoding: str = ""
    last_modified_at: str = ""
    table_type: TableType = TableType.NORMAL

    def field(self, field_id_or_name: str) -> FieldDefinition:
        for candidate in self.fields:
            if candidate.field_id == field_id_or_name or candidate.name == field_id_or_name:
                return candidate
        raise KeyError(f"Unknown field: {field_id_or_name}")

    @property
    def field_ids(self) -> tuple[str, ...]:
        return tuple(field.field_id for field in self.fields)

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields)


@dataclass
class NormalTableDefinition(TableDefinition):
    table_type: TableType = TableType.NORMAL
    default_sort_field: str = ""
    readonly_fields: tuple[str, ...] = ()

    @classmethod
    def grouped(
        cls,
        *,
        table_id: str,
        display_name: str,
        fields: list[FieldDefinition],
        group_key: str,
        rows: list[TableRow] | None = None,
        description: str = "",
    ) -> GroupTableDefinition:
        return GroupTableDefinition(
            table_id=table_id,
            display_name=display_name,
            fields=fields,
            rows=rows or [],
            description=description,
            group_key=group_key,
        )


@dataclass
class GroupTableDefinition(TableDefinition):
    group_key: str = ""
    group_sort: str = "original"
    group_boundary_style: str = "section"
    allow_non_contiguous_group: bool = False
    table_type: TableType = TableType.GROUP


@dataclass
class MatrixTableDefinition(TableDefinition):
    x_axis: str = ""
    y_axis: str = ""
    value_field: str = ""
    x_axis_label: str = ""
    y_axis_label: str = ""
    axis_order: str = "field"
    missing_cell_policy: str = "error"
    duplicate_cell_policy: str = "error"
    table_type: TableType = TableType.MATRIX

    @property
    def axis_fields(self) -> tuple[str, str, str]:
        return (self.x_axis, self.y_axis, self.value_field)


@dataclass(frozen=True)
class EnumItem:
    item_id: str
    display_name: str
    export_value: Any
    sort_order: int
    description: str = ""
    deprecated: bool = False
    deprecated_reason: str = ""
    updated_by: str = ""
    updated_at: str = ""


@dataclass
class EnumDefinition:
    enum_id: str
    display_name: str
    items: list[EnumItem]
    description: str = ""
    default_item_id: str = ""
    allow_deprecated_display: bool = True
    export_name: str = ""
    created_at: str = ""
    updated_at: str = ""

    def item(self, item_id: str) -> EnumItem:
        for candidate in self.items:
            if candidate.item_id == item_id:
                return candidate
        raise KeyError(f"Unknown enum item: {item_id}")


@dataclass
class MetaDefinition:
    meta_id: str
    display_name: str
    fields: list[FieldDefinition]
    description: str = ""
    export_name: str = ""
    max_depth: int = 3
    complexity_threshold: int | None = None
    references: tuple[str, ...] = ()
    created_at: str = ""
    updated_at: str = ""

    def field(self, field_id_or_name: str) -> FieldDefinition:
        for candidate in self.fields:
            if candidate.field_id == field_id_or_name or candidate.name == field_id_or_name:
                return candidate
        raise KeyError(f"Unknown meta field: {field_id_or_name}")


class ProjectSchema:
    def __init__(self) -> None:
        self.tables: dict[str, TableDefinition] = {}
        self.enums: dict[str, EnumDefinition] = {}
        self.metas: dict[str, MetaDefinition] = {}

    def add_table(self, table: TableDefinition) -> None:
        if table.table_id in self.tables:
            raise ValueError(f"Duplicate table_id: {table.table_id}")
        self._validate_table(table)
        self.tables[table.table_id] = table

    def add_enum(self, enum: EnumDefinition) -> None:
        if enum.enum_id in self.enums:
            raise ValueError(f"Duplicate enum_id: {enum.enum_id}")
        self._validate_enum(enum)
        self.enums[enum.enum_id] = enum

    def add_meta(self, meta: MetaDefinition) -> None:
        if meta.meta_id in self.metas:
            raise ValueError(f"Duplicate meta_id: {meta.meta_id}")
        self._validate_meta(meta)
        self.metas[meta.meta_id] = meta

    def table(self, table_id: str) -> TableDefinition:
        return self.tables[table_id]

    def enum(self, enum_id: str) -> EnumDefinition:
        return self.enums[enum_id]

    def meta(self, meta_id: str) -> MetaDefinition:
        return self.metas[meta_id]

    def resolve_field_reference(self, field: FieldDefinition) -> TableDefinition | EnumDefinition | MetaDefinition:
        if field.field_type == FieldType.ENUM:
            return self.enums[field.enum_id]
        if field.field_type == FieldType.REFERENCE:
            return self.tables[field.target_table_id]
        if field.field_type == FieldType.META:
            return self.metas[field.meta_id]
        raise ValueError(f"Field {field.field_id} does not reference another model")

    def validate_structure(self) -> None:
        for enum in self.enums.values():
            self._validate_enum(enum)
        for meta in self.metas.values():
            self._validate_meta(meta)
            for field_definition in meta.fields:
                self._validate_field_reference(field_definition)
        for table in self.tables.values():
            self._validate_table(table)

    def _validate_enum(self, enum: EnumDefinition) -> None:
        item_ids = [item.item_id for item in enum.items]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError(f"Duplicate enum item in {enum.enum_id}")
        export_values = [item.export_value for item in enum.items]
        if len(export_values) != len(set(export_values)):
            raise ValueError(f"Duplicate export_value in enum {enum.enum_id}")
        if enum.default_item_id:
            default_item = None
            for item in enum.items:
                if item.item_id == enum.default_item_id:
                    default_item = item
                    break
            if default_item is None:
                raise ValueError(f"Enum {enum.enum_id} default_item_id does not exist: {enum.default_item_id}")
            if default_item.deprecated:
                raise ValueError(f"Enum {enum.enum_id} default_item_id is deprecated: {enum.default_item_id}")

    def _validate_meta(self, meta: MetaDefinition) -> None:
        self._assert_unique_field_collection(meta.fields, owner=f"meta {meta.meta_id}")
        for field_definition in meta.fields:
            field_definition.validate_shape()

    def _validate_table(self, table: TableDefinition) -> None:
        self._assert_unique_field_collection(table.fields, owner=f"table {table.table_id}")
        for field_definition in table.fields:
            field_definition.validate_shape()
            self._validate_field_reference(field_definition)
        self._validate_table_parameters(table)
        self._validate_rows(table)

    def _assert_unique_field_collection(self, fields: list[FieldDefinition], *, owner: str) -> None:
        field_ids = [field.field_id for field in fields]
        field_names = [field.name for field in fields]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError(f"Duplicate field_id in {owner}")
        if len(field_names) != len(set(field_names)):
            raise ValueError(f"Duplicate field name in {owner}")

    def _validate_field_reference(self, field_definition: FieldDefinition) -> None:
        if field_definition.field_type == FieldType.ENUM and field_definition.enum_id not in self.enums:
            raise ValueError(f"Field {field_definition.field_id} references missing enum_id: {field_definition.enum_id}")
        if field_definition.field_type == FieldType.META and field_definition.meta_id not in self.metas:
            raise ValueError(f"Field {field_definition.field_id} references missing meta_id: {field_definition.meta_id}")
        if field_definition.field_type == FieldType.REFERENCE:
            if field_definition.target_table_id not in self.tables:
                raise ValueError(f"Field {field_definition.field_id} references missing table: {field_definition.target_table_id}")
            target_table = self.tables[field_definition.target_table_id]
            if field_definition.target_field_id:
                try:
                    target_table.field(field_definition.target_field_id)
                except KeyError as error:
                    raise ValueError(
                        f"Field {field_definition.field_id} references missing target_field_id: {field_definition.target_field_id}"
                    ) from error

    def _validate_table_parameters(self, table: TableDefinition) -> None:
        field_names = set(table.field_names)
        field_ids = set(table.field_ids)
        allowed_fields = field_names | field_ids
        if table.primary_key and table.primary_key not in allowed_fields:
            raise ValueError(f"Table {table.table_id} primary_key does not exist: {table.primary_key}")
        missing_features = [feature for feature in table.feature_keys if feature not in allowed_fields]
        if missing_features:
            raise ValueError(f"Table {table.table_id} feature_keys do not exist: {', '.join(missing_features)}")
        if isinstance(table, GroupTableDefinition) and table.group_key not in allowed_fields:
            raise ValueError(f"Table {table.table_id} group_key does not exist: {table.group_key}")
        if isinstance(table, MatrixTableDefinition):
            axis_fields = [table.x_axis, table.y_axis, table.value_field]
            if not all(axis_fields):
                raise ValueError(f"Table {table.table_id} axis fields cannot be empty")
            missing_axis = [axis for axis in axis_fields if axis not in allowed_fields]
            if missing_axis:
                raise ValueError(f"Table {table.table_id} axis fields do not exist: {', '.join(missing_axis)}")
            if len(axis_fields) != len(set(axis_fields)):
                raise ValueError(f"Table {table.table_id} axis fields must be distinct")

    def _validate_rows(self, table: TableDefinition) -> None:
        fields_by_name = {field.name: field for field in table.fields}
        fields_by_id = {field.field_id: field for field in table.fields}
        allowed_keys = set(fields_by_name) | set(fields_by_id)
        for row_index, row in enumerate(table.rows):
            unknown_keys = [key for key in row.values if key not in allowed_keys]
            if unknown_keys:
                raise ValueError(f"Table {table.table_id} row {row_index} has unknown field: {', '.join(unknown_keys)}")
            for field_definition in table.fields:
                has_value = field_definition.name in row.values or field_definition.field_id in row.values
                value = row.values.get(field_definition.name, row.values.get(field_definition.field_id))
                if field_definition.required and (not has_value or value in {"", None}):
                    raise ValueError(f"Table {table.table_id} row {row_index} missing required field: {field_definition.name}")
                if has_value and value is not None and value != "":
                    self._validate_basic_value_type(table.table_id, row_index, field_definition, value)

    def _validate_basic_value_type(self, table_id: str, row_index: int, field_definition: FieldDefinition, value: Any) -> None:
        if field_definition.field_type in {FieldType.INT, FieldType.ID} and not isinstance(value, int):
            raise ValueError(f"Table {table_id} row {row_index} field {field_definition.name} expected int")
        if field_definition.field_type == FieldType.FLOAT and not isinstance(value, (int, float)):
            raise ValueError(f"Table {table_id} row {row_index} field {field_definition.name} expected float")
        if field_definition.field_type == FieldType.BOOL and not isinstance(value, bool):
            raise ValueError(f"Table {table_id} row {row_index} field {field_definition.name} expected bool")
        if field_definition.field_type == FieldType.STRING and not isinstance(value, str):
            raise ValueError(f"Table {table_id} row {row_index} field {field_definition.name} expected string")
        if field_definition.field_type == FieldType.LIST and not isinstance(value, list):
            raise ValueError(f"Table {table_id} row {row_index} field {field_definition.name} expected list")

from __future__ import annotations

import json
import os
import stat
import errno

import pytest

from xtable.application.project_service import (
    FileFailureKind,
    ProjectConflictError,
    ProjectFileError,
    ProjectService,
)
from xtable.domain.models import EnumDefinition, EnumItem, FieldDefinition, FieldType, NormalTableDefinition, ProjectSchema
from xtable.domain.project import ProjectSettings


def test_create_project_writes_reopenable_config_and_directories(tmp_path):
    service = ProjectService()
    project = service.create_project(
        tmp_path / "DemoProject",
        name="Demo",
        operator="designer",
    )

    assert project.settings.name == "Demo"
    assert project.root.exists()
    assert (project.root / "xtable.project.json").exists()
    assert (project.root / "tables").is_dir()
    for directory in (
        "tables",
        "rules",
        "enums",
        "types",
        "settings",
        "logs",
        "cache",
        "recovery",
    ):
        assert (project.root / directory).is_dir()

    reopened = service.open_project(project.root)

    assert reopened.settings == project.settings


def test_create_project_config_contains_schema_paths_export_and_metadata(tmp_path):
    service = ProjectService()
    project = service.create_project(
        tmp_path / "DemoProject",
        name="Demo",
        operator="designer",
    )

    config = json.loads(project.config_path.read_text(encoding="utf-8"))

    assert config["schema_version"] == 1
    assert config["project_id"]
    assert config["created_at"]
    assert config["updated_at"]
    assert config["paths"] == {
        "tables_dir": "tables",
        "rules_dir": "rules",
        "enums_dir": "enums",
        "types_dir": "types",
        "settings_dir": "settings",
        "logs_dir": "logs",
        "cache_dir": "cache",
        "recovery_dir": "recovery",
        "exports_dir": "exports",
    }
    assert config["export"]["default_dir"] == "exports"
    assert config["export"]["default_format"] == "xlsx"
    assert config["export"]["validate_before_export"] is True
    assert config["ui"]["theme"] == "light"
    assert config["safety"]["atomic_save"] is True


def test_open_legacy_project_migrates_missing_schema_defaults(tmp_path):
    service = ProjectService()
    root = tmp_path / "LegacyProject"
    root.mkdir()
    (root / "xtable.project.json").write_text(
        json.dumps({"name": "Legacy", "operator": "old-user"}),
        encoding="utf-8",
    )

    project = service.open_project(root)

    assert project.settings.name == "Legacy"
    assert project.settings.paths["exports_dir"] == "exports"
    assert project.settings.export["validate_before_export"] is True

    service.save_project(project)
    migrated = json.loads(project.config_path.read_text(encoding="utf-8"))

    assert migrated["schema_version"] == 1
    assert migrated["paths"]["exports_dir"] == "exports"


def test_save_project_preserves_external_changes_by_rejecting_stale_snapshot(tmp_path):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")
    config_path = project.root / "xtable.project.json"

    external = json.loads(config_path.read_text(encoding="utf-8"))
    external["operator"] = "external-user"
    config_path.write_text(json.dumps(external), encoding="utf-8")

    project.settings = ProjectSettings(name="Demo", operator="local-user")

    with pytest.raises(ProjectConflictError):
        service.save_project(project)


def test_save_project_rejects_read_only_config(tmp_path):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")
    config_path = project.root / "xtable.project.json"
    config_path.chmod(stat.S_IREAD)

    try:
        with pytest.raises(ProjectConflictError):
            service.save_project(project)
    finally:
        config_path.chmod(stat.S_IREAD | stat.S_IWRITE)


def test_save_project_reports_write_failures_as_conflicts(tmp_path, monkeypatch):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")

    def fail_write(path, settings):
        raise OSError("disk write failed")

    monkeypatch.setattr(service, "_write_config", fail_write)

    with pytest.raises(ProjectConflictError) as error:
        service.save_project(project)

    assert error.value.kind is FileFailureKind.WRITE_FAILED


def test_save_project_keeps_original_config_when_atomic_replace_fails(tmp_path, monkeypatch):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")
    config_path = project.root / "xtable.project.json"
    before = config_path.read_text(encoding="utf-8")
    project.settings = ProjectSettings(name="Changed")

    def fail_replace(source, target):
        raise PermissionError("target is locked")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(ProjectConflictError) as error:
        service.save_project(project)

    assert error.value.kind is FileFailureKind.LOCKED
    assert config_path.read_text(encoding="utf-8") == before
    assert not list(project.root.glob("*.tmp"))
    assert project.config_digest == service._file_digest(config_path)


def test_save_project_fsyncs_project_directory_after_atomic_replace(tmp_path, monkeypatch):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")
    called = []

    monkeypatch.setattr(service, "_fsync_directory", lambda path: called.append(path))

    service.save_project(project)

    assert called == [project.root]


def test_save_project_classifies_common_io_failures(tmp_path, monkeypatch):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")

    scenarios = [
        (PermissionError(errno.EACCES, "denied"), FileFailureKind.PERMISSION_DENIED),
        (OSError(errno.ENOSPC, "no space"), FileFailureKind.NO_SPACE),
        (FileNotFoundError(errno.ENOENT, "missing"), FileFailureKind.PATH_MISSING),
    ]

    for os_error, expected_kind in scenarios:
        monkeypatch.setattr(service, "_write_config", lambda path, settings: None)
        monkeypatch.setattr(os, "replace", lambda source, target, error=os_error: (_ for _ in ()).throw(error))

        with pytest.raises(ProjectConflictError) as error:
            service.save_project(project)

        assert error.value.kind is expected_kind


def test_open_project_reports_invalid_json(tmp_path):
    service = ProjectService()
    root = tmp_path / "BrokenProject"
    root.mkdir()
    (root / "xtable.project.json").write_text("{broken", encoding="utf-8")

    with pytest.raises(ProjectFileError) as error:
        service.open_project(root)

    assert error.value.kind is FileFailureKind.INVALID_CONFIG


def test_open_project_reports_missing_required_fields(tmp_path):
    service = ProjectService()
    root = tmp_path / "BrokenProject"
    root.mkdir()
    (root / "xtable.project.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ProjectFileError) as error:
        service.open_project(root)

    assert error.value.kind is FileFailureKind.INVALID_CONFIG


def test_recent_projects_ignores_damaged_store(tmp_path):
    service = ProjectService(app_data_dir=tmp_path / "app-data")
    service.recent_projects.path.parent.mkdir(parents=True)
    service.recent_projects.path.write_text("not json", encoding="utf-8")

    assert service.recent_projects.load() == []

    project = service.create_project(tmp_path / "DemoProject", name="Demo")

    assert service.recent_projects.load()[0].path == project.root


def test_recent_projects_are_updated_without_duplicates(tmp_path):
    service = ProjectService(app_data_dir=tmp_path / "app-data")
    first = service.create_project(tmp_path / "First", name="First")
    second = service.create_project(tmp_path / "Second", name="Second")

    service.open_project(first.root)

    recent = service.recent_projects.load()

    assert [item.path for item in recent] == [
        first.root.resolve(),
        second.root.resolve(),
    ]
    assert [item.name for item in recent] == ["First", "Second"]


def test_project_service_saves_and_loads_schema_file(tmp_path):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")
    schema = ProjectSchema()
    schema.add_enum(
        EnumDefinition(
            enum_id="quality",
            display_name="Quality",
            items=[EnumItem(item_id="common", display_name="Common", export_value=1, sort_order=1)],
        )
    )
    schema.add_table(
        NormalTableDefinition(
            table_id="items",
            display_name="Items",
            fields=[
                FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID),
                FieldDefinition(field_id="quality", name="quality", display_name="Quality", field_type=FieldType.ENUM, enum_id="quality"),
            ],
        )
    )

    saved = service.save_schema(project, schema)
    loaded = service.load_schema(saved)

    assert (project.root / "settings" / "schema.json").exists()
    assert saved.schema_digest
    assert loaded.table("items").field("quality").enum_id == "quality"


def test_project_service_load_schema_returns_empty_schema_when_file_missing(tmp_path):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")

    schema = service.load_schema(project)

    assert schema.tables == {}
    assert schema.enums == {}
    assert schema.metas == {}


def test_project_service_rejects_stale_schema_save(tmp_path):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")
    schema = ProjectSchema()
    saved = service.save_schema(project, schema)

    schema_path = project.root / "settings" / "schema.json"
    original = json.loads(schema_path.read_text(encoding="utf-8"))
    original["external"] = True
    schema_path.write_text(json.dumps(original), encoding="utf-8")

    with pytest.raises(ProjectConflictError) as error:
        service.save_schema(saved, schema)

    assert error.value.kind is FileFailureKind.EXTERNALLY_MODIFIED


def test_project_service_rejects_schema_save_without_loaded_digest_when_file_exists(tmp_path):
    service = ProjectService()
    project = service.create_project(tmp_path / "DemoProject", name="Demo")
    schema = ProjectSchema()
    schema.add_table(
        NormalTableDefinition(
            table_id="items",
            display_name="Items",
            fields=[FieldDefinition(field_id="id", name="id", display_name="ID", field_type=FieldType.ID)],
        )
    )
    service.save_schema(project, schema)

    reopened = service.open_project(project.root)
    before = (project.root / "settings" / "schema.json").read_text(encoding="utf-8")

    with pytest.raises(ProjectConflictError) as error:
        service.save_schema(reopened, ProjectSchema())

    assert error.value.kind is FileFailureKind.EXTERNALLY_MODIFIED
    assert (project.root / "settings" / "schema.json").read_text(encoding="utf-8") == before

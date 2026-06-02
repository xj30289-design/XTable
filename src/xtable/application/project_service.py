from __future__ import annotations

import hashlib
import json
import os
import errno
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from xtable.domain.project import Project, ProjectSettings


CONFIG_FILE_NAME = "xtable.project.json"
PROJECT_DIRECTORIES = (
    "tables",
    "rules",
    "enums",
    "types",
    "settings",
    "logs",
    "cache",
    "recovery",
    "exports",
)
DEFAULT_PATHS = {
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
DEFAULT_EXPORT = {
    "default_dir": "exports",
    "default_format": "xlsx",
    "overwrite_policy": "prompt",
    "validate_before_export": True,
}
DEFAULT_SAFETY = {
    "atomic_save": True,
    "detect_external_changes": True,
    "write_temp_suffix": ".tmp",
}


class FileFailureKind(Enum):
    MISSING = "missing"
    INVALID_CONFIG = "invalid_config"
    EXTERNALLY_MODIFIED = "externally_modified"
    READ_ONLY = "read_only"
    LOCKED = "locked"
    PERMISSION_DENIED = "permission_denied"
    NO_SPACE = "no_space"
    PATH_MISSING = "path_missing"
    WRITE_FAILED = "write_failed"


class ProjectError(RuntimeError):
    """Base class for project file failures."""


class ProjectFileError(ProjectError):
    """Raised when a project file cannot be read or interpreted."""

    def __init__(self, message: str, kind: FileFailureKind) -> None:
        super().__init__(message)
        self.kind = kind


class ProjectConflictError(ProjectFileError):
    """Raised when saving would overwrite unsafe external file state."""


@dataclass(frozen=True)
class RecentProject:
    name: str
    path: Path


class RecentProjectsStore:
    def __init__(self, app_data_dir: Path | None = None, limit: int = 10) -> None:
        base_dir = app_data_dir or (Path.home() / ".xtable")
        self.path = base_dir / "recent_projects.json"
        self.limit = limit

    def load(self) -> list[RecentProject]:
        if not self.path.exists():
            return []
        try:
            raw_items = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [
            RecentProject(name=item["name"], path=Path(item["path"]))
            for item in raw_items
            if isinstance(item, dict) and "name" in item and "path" in item
        ]

    def record(self, project: Project) -> None:
        resolved = project.root.resolve()
        items = [
            item for item in self.load()
            if item.path.resolve() != resolved
        ]
        items.insert(0, RecentProject(name=project.settings.name, path=resolved))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {"name": item.name, "path": str(item.path)}
            for item in items[: self.limit]
        ]
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class ProjectService:
    def __init__(self, app_data_dir: Path | None = None) -> None:
        self.recent_projects = RecentProjectsStore(app_data_dir)

    def create_project(
        self,
        root: Path,
        *,
        name: str,
        operator: str = "",
        default_encoding: str = "utf-8",
        log_retention_days: int = 30,
        theme: str = "light",
    ) -> Project:
        root = root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        for directory in PROJECT_DIRECTORIES:
            (root / directory).mkdir(parents=True, exist_ok=True)

        settings = ProjectSettings(
            name=name,
            operator=operator,
            default_encoding=default_encoding,
            log_retention_days=log_retention_days,
            theme=theme,
            project_id=str(uuid.uuid4()),
            created_at=self._now_iso(),
            updated_at=self._now_iso(),
            paths=DEFAULT_PATHS.copy(),
            export=DEFAULT_EXPORT.copy(),
            ui={"theme": theme},
            safety=DEFAULT_SAFETY.copy(),
        )
        config_path = root / CONFIG_FILE_NAME
        self._write_config_atomic(config_path, settings)
        project = Project(
            root=root,
            settings=settings,
            config_digest=self._file_digest(config_path),
        )
        self.recent_projects.record(project)
        return project

    def open_project(self, root: Path) -> Project:
        root = root.resolve()
        config_path = root / CONFIG_FILE_NAME
        if not config_path.exists():
            raise ProjectFileError(
                f"Project config not found: {config_path}",
                FileFailureKind.MISSING,
            )

        settings = self._read_config(config_path)
        project = Project(
            root=root,
            settings=settings,
            config_digest=self._file_digest(config_path),
        )
        self.recent_projects.record(project)
        return project

    def save_project(self, project: Project) -> Project:
        config_path = project.config_path
        if config_path.exists():
            if not self._has_owner_write_bit(config_path):
                raise ProjectConflictError(
                    f"Project config is read-only: {config_path}",
                    FileFailureKind.READ_ONLY,
                )
            current_digest = self._file_digest(config_path)
            if current_digest != project.config_digest:
                raise ProjectConflictError(
                    f"Project config changed outside XTable: {config_path}",
                    FileFailureKind.EXTERNALLY_MODIFIED,
                )

        try:
            project.settings = self._with_updated_timestamp(project.settings)
            self._write_config_atomic(config_path, project.settings)
        except OSError as error:
            raise ProjectConflictError(
                f"Project config could not be saved: {config_path}",
                self._classify_os_error(error),
            ) from error
        project.config_digest = self._file_digest(config_path)
        self.recent_projects.record(project)
        return project

    def _read_config(self, path: Path) -> ProjectSettings:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            name = data["name"]
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Project name is required")
            ui = self._merge_dict({"theme": data.get("theme", "light")}, data.get("ui", {}))
            theme = str(ui.get("theme", data.get("theme", "light")))
            return ProjectSettings(
                name=name,
                operator=data.get("operator", ""),
                default_encoding=data.get("default_encoding", "utf-8"),
                log_retention_days=int(data.get("log_retention_days", 30)),
                theme=theme,
                schema_version=int(data.get("schema_version", 1)),
                project_id=data.get("project_id", str(uuid.uuid4())),
                created_at=data.get("created_at", self._now_iso()),
                updated_at=data.get("updated_at", data.get("created_at", self._now_iso())),
                paths=self._merge_dict(DEFAULT_PATHS, data.get("paths", {})),
                export=self._merge_dict(DEFAULT_EXPORT, data.get("export", {})),
                ui=ui,
                safety=self._merge_dict(DEFAULT_SAFETY, data.get("safety", {})),
            )
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise ProjectFileError(
                f"Project config is invalid: {path}",
                FileFailureKind.INVALID_CONFIG,
            ) from error

    def _write_config_atomic(self, path: Path, settings: ProjectSettings) -> None:
        temp_path = path.with_name(f".{path.name}.tmp")
        try:
            self._write_config(temp_path, settings)
            os.replace(temp_path, path)
            self._fsync_directory(path.parent)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _write_config(self, path: Path, settings: ProjectSettings) -> None:
        payload: dict[str, Any] = {
            "schema_version": settings.schema_version,
            "project_id": settings.project_id,
            "name": settings.name,
            "operator": settings.operator,
            "default_encoding": settings.default_encoding,
            "log_retention_days": settings.log_retention_days,
            "theme": settings.theme,
            "created_at": settings.created_at,
            "updated_at": settings.updated_at,
            "paths": settings.paths or DEFAULT_PATHS.copy(),
            "export": settings.export or DEFAULT_EXPORT.copy(),
            "ui": settings.ui or {"theme": settings.theme},
            "safety": settings.safety or DEFAULT_SAFETY.copy(),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        with path.open("w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())

    def _file_digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _has_owner_write_bit(self, path: Path) -> bool:
        return bool(path.stat().st_mode & os.stat(path).st_mode & 0o200)

    def _classify_os_error(self, error: OSError) -> FileFailureKind:
        if getattr(error, "winerror", None) in (32, 33):
            return FileFailureKind.LOCKED
        if error.errno == errno.ENOSPC:
            return FileFailureKind.NO_SPACE
        if error.errno == errno.ENOENT:
            return FileFailureKind.PATH_MISSING
        if error.errno == errno.EACCES:
            return FileFailureKind.PERMISSION_DENIED
        if isinstance(error, PermissionError):
            return FileFailureKind.LOCKED
        return FileFailureKind.WRITE_FAILED

    def _fsync_directory(self, path: Path) -> None:
        try:
            directory_fd = os.open(path, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(directory_fd)
        except OSError:
            pass
        finally:
            os.close(directory_fd)

    def _merge_dict(self, defaults: dict[str, Any], overrides: object) -> dict[str, Any]:
        merged = defaults.copy()
        if isinstance(overrides, dict):
            merged.update(overrides)
        return merged

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _with_updated_timestamp(self, settings: ProjectSettings) -> ProjectSettings:
        return ProjectSettings(
            name=settings.name,
            operator=settings.operator,
            default_encoding=settings.default_encoding,
            log_retention_days=settings.log_retention_days,
            theme=settings.theme,
            schema_version=settings.schema_version,
            project_id=settings.project_id,
            created_at=settings.created_at,
            updated_at=self._now_iso(),
            paths=settings.paths or DEFAULT_PATHS.copy(),
            export=settings.export or DEFAULT_EXPORT.copy(),
            ui=settings.ui or {"theme": settings.theme},
            safety=settings.safety or DEFAULT_SAFETY.copy(),
        )

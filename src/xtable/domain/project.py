from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_ENCODING = "utf-8"
DEFAULT_LOG_RETENTION_DAYS = 30
DEFAULT_THEME = "light"


@dataclass(frozen=True)
class ProjectSettings:
    name: str
    operator: str = ""
    default_encoding: str = DEFAULT_ENCODING
    log_retention_days: int = DEFAULT_LOG_RETENTION_DAYS
    theme: str = DEFAULT_THEME
    schema_version: int = 1
    project_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    paths: dict[str, str] = field(default_factory=dict)
    export: dict[str, object] = field(default_factory=dict)
    ui: dict[str, object] = field(default_factory=dict)
    safety: dict[str, object] = field(default_factory=dict)


@dataclass
class Project:
    root: Path
    settings: ProjectSettings
    config_digest: str
    schema_digest: str = ""

    @property
    def config_path(self) -> Path:
        return self.root / "xtable.project.json"

from __future__ import annotations

from pathlib import Path


def test_repository_provides_windows_editor_launcher():
    launcher = Path("open_editor.bat")

    assert launcher.exists()

    content = launcher.read_text(encoding="utf-8")

    assert "python -m xtable.app.main" in content
    assert "GOTO :eof" in content

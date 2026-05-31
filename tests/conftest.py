"""Pytest fixtures: isolate every test in its own temp data dir."""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_storage(monkeypatch):
    tmp = Path(tempfile.mkdtemp(prefix="dia-test-"))
    monkeypatch.setenv("UPLOAD_DIR", str(tmp / "uploads"))
    monkeypatch.setenv("CHROMA_DIR", str(tmp / "chroma"))
    monkeypatch.setenv("SQLITE_PATH", str(tmp / "app.db"))
    monkeypatch.setenv("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

    # Reset cached singletons so they pick up the new env.
    from backend.utils import config

    config.get_settings.cache_clear()
    yield

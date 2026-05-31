from pathlib import Path

import pytest

from backend.rag.extractor import (
    UnsupportedFileTypeError,
    extract_text,
)


def test_extract_txt(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("hello world", encoding="utf-8")
    assert extract_text(p) == "hello world"


def test_extract_unsupported_raises(tmp_path: Path):
    p = tmp_path / "x.xyz"
    p.write_text("nope")
    with pytest.raises(UnsupportedFileTypeError):
        extract_text(p)

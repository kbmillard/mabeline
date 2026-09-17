"""Tests for path_resolver."""

from __future__ import annotations

import tempfile
from pathlib import Path

from catalog.path_resolver import (
    is_valid_data_file,
    latest_release_dir,
    resolve_newest,
)


def test_rejects_html_stub():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "bad.json"
        p.write_text("<html><body>Missing Key</body></html>", encoding="utf-8")
        ok, reason = is_valid_data_file(p, stub_bytes=10)
        assert not ok
        assert reason == "html_stub"


def test_rejects_tiny_stub():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "tiny.csv"
        p.write_text("a,b\n1,2", encoding="utf-8")
        ok, reason = is_valid_data_file(p, stub_bytes=500)
        assert not ok
        assert "below_stub" in (reason or "")


def test_resolve_newest_by_mtime():
    with tempfile.TemporaryDirectory() as td:
        old = Path(td) / "old.csv"
        new = Path(td) / "new.csv"
        old.write_text("x" * 600, encoding="utf-8")
        new.write_text("y" * 600, encoding="utf-8")
        import os
        import time

        os.utime(old, (time.time() - 10000, time.time() - 10000))
        chosen = resolve_newest([old, new], stub_bytes=500)
        assert chosen == new


def test_latest_release_dir_sort():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "release=2026-07-05").mkdir()
        (base / "release=2026-07-09").mkdir()
        latest = latest_release_dir(base)
        assert latest is not None
        assert latest.name == "release=2026-07-09"

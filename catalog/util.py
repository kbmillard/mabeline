from __future__ import annotations

import hashlib
import json
from pathlib import Path

from catalog.config import MD5_MAX_BYTES


def file_signature(path: Path, *, with_md5: bool = False) -> dict:
    st = path.stat()
    sig = {
        "bytes": st.st_size,
        "mtime": int(st.st_mtime),
    }
    if with_md5 and st.st_size <= MD5_MAX_BYTES:
        h = hashlib.md5()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
                h.update(chunk)
        sig["md5"] = h.hexdigest()
    return sig


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def append_log(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip() + "\n")


def rel_under(base: Path, path: Path) -> str:
    return str(path.relative_to(base)).replace("\\", "/")

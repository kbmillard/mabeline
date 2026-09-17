from __future__ import annotations

import csv as _csv
import json
import shutil
import sys
from pathlib import Path

# FCC ULS .dat and similar dumps can have very large single fields.
_csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

import pyarrow as pa
import pyarrow.csv as pa_csv
import pyarrow.parquet as pq

from catalog.config import (
    PARQUET_DEFER_MIN_BYTES,
    SKIP_PARQUET_NAMES,
    SKIP_PARQUET_SUFFIXES,
    UNWRAPPED,
    run_dir,
    utc_now,
)
from catalog.util import append_log, file_signature, rel_under, write_json

# geojson above this size is streamed feature-by-feature instead of json.loads
GEOJSON_STREAM_MIN_BYTES = 64 * 1024 * 1024
_PARQUET_COMPRESSION = "zstd"


def _json_safe(value):
    """Flatten nested containers to JSON strings so PyArrow can build clean columns."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), default=str)
    return value


def _rows_to_table(rows: list[dict]) -> pa.Table:
    """Build an Arrow table from heterogeneous row dicts.

    Uses union-of-keys ordering; retries with all values stringified if type
    inference across rows conflicts (mixed int/str in the same field).
    """
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)
    columns = {k: [_json_safe(row.get(k)) for row in rows] for k in keys}
    try:
        return pa.table(columns)
    except (pa.ArrowInvalid, pa.ArrowTypeError, pa.ArrowNotImplementedError):
        stringified = {
            k: [None if v is None else str(v) for v in col] for k, col in columns.items()
        }
        return pa.table(stringified)


def _write_table(table: pa.Table, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, dest, compression=_PARQUET_COMPRESSION)
    return table.num_rows


def _write_rows_parquet(rows: list[dict], dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        empty = pa.table({"_empty": pa.array([], type=pa.string())})
        return _write_table(empty, dest)
    return _write_table(_rows_to_table(rows), dest)


def _parquet_out(run_id: str, family: str, rel_src: str) -> Path:
    rel_parquet = Path(rel_src).with_suffix(".parquet")
    return run_dir(run_id) / family / rel_parquet


def _should_convert(path: Path) -> tuple[bool, str]:
    if path.name in SKIP_PARQUET_NAMES:
        return False, "skip_name"
    ext = path.suffix.lower()
    if ext in SKIP_PARQUET_SUFFIXES:
        return False, f"skip_ext_{ext}"
    size = path.stat().st_size
    if size == 0:
        return False, "empty_source"
    if size >= PARQUET_DEFER_MIN_BYTES:
        return False, "deferred_bulk"
    if ext == ".parquet":
        return False, "already_parquet"
    if ext in {".csv", ".tsv", ".txt", ".dat", ".json", ".jsonl", ".geojson"}:
        return True, "tabular"
    if ext in {".xlsx", ".xls"}:
        return True, "spreadsheet"
    if ext == ".xml":
        return False, "skip_xml"
    return False, "unsupported"


def _source_key(sig: dict) -> str:
    if "md5" in sig:
        return sig["md5"]
    return f"sz{sig['bytes']}_mt{sig['mtime']}"


def _feature_to_row(feat: dict) -> dict:
    props = feat.get("properties") or {}
    geom = feat.get("geometry")
    row = dict(props)
    row["_geometry_json"] = json.dumps(geom, separators=(",", ":"), default=str) if geom else None
    row["_feature_type"] = feat.get("type")
    row["_feature_id"] = feat.get("id")
    return row


def _stream_geojson_features(src: Path):
    """Stream features with ijson; keep whatever parses before a truncated tail."""
    import ijson

    with src.open("rb") as fh:
        try:
            for feat in ijson.items(fh, "features.item", use_float=True):
                yield feat
        except ijson.JSONError:
            return


def _iter_geojson_features(src: Path):
    """Yield GeoJSON features; stream large/truncated files, tolerate broken tails."""
    if src.stat().st_size >= GEOJSON_STREAM_MIN_BYTES:
        yield from _stream_geojson_features(src)
        return
    try:
        payload = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # Truncated/malformed small export: salvage via streaming parser.
        yield from _stream_geojson_features(src)
        return
    for feat in payload.get("features") or []:
        yield feat


def _convert_geojson(src: Path, dest: Path) -> int:
    rows = [_feature_to_row(feat) for feat in _iter_geojson_features(src)]
    return _write_rows_parquet(rows, dest)


def _sniff_delimiter(sample: str, default: str = ",") -> str:
    try:
        return _csv.Sniffer().sniff(sample, delimiters="|\t,;").delimiter
    except _csv.Error:
        return default


def _read_csv_typed(src: Path, *, delimiter: str) -> pa.Table:
    read_opts = pa_csv.ReadOptions(use_threads=True)
    parse_opts = pa_csv.ParseOptions(delimiter=delimiter, newlines_in_values=True)
    try:
        return pa_csv.read_csv(src, read_options=read_opts, parse_options=parse_opts)
    except (pa.ArrowInvalid, pa.ArrowTypeError, UnicodeDecodeError):
        return _read_csv_stdlib(src, delimiter=None)


def _read_csv_stdlib(src: Path, *, delimiter: str | None) -> pa.Table:
    """Read a delimited file as all-string rows; sniff the delimiter when unknown."""
    with src.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        if delimiter is None:
            sample = fh.read(65536)
            fh.seek(0)
            delimiter = _sniff_delimiter(sample)
        rows = list(_csv.reader(fh, delimiter=delimiter))
    if not rows:
        return pa.table({"_empty": pa.array([], type=pa.string())})
    header = [h or f"col_{i}" for i, h in enumerate(rows[0])]
    data = [
        {header[i]: (r[i] if i < len(r) else None) for i in range(len(header))}
        for r in rows[1:]
    ]
    return _rows_to_table(data) if data else pa.table({h: pa.array([], type=pa.string()) for h in header})


class UnparseableSource(Exception):
    """Source is not the data we expected (e.g. an HTML error page saved as .json)."""


def _read_json_table(src: Path) -> pa.Table:
    try:
        payload = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UnparseableSource(f"not_valid_json: {exc}") from exc
    if isinstance(payload, dict):
        # Table-like dict-of-records (e.g. SEC company_tickers) -> rows.
        values = list(payload.values())
        if values and all(isinstance(v, dict) for v in values):
            rows = values
        else:
            rows = [payload]
    elif isinstance(payload, list):
        rows = payload if all(isinstance(v, dict) for v in payload) else [{"value": v} for v in payload]
    else:
        rows = [{"value": payload}]
    return _rows_to_table(rows) if rows else pa.table({"_empty": pa.array([], type=pa.string())})


def _read_jsonl_table(src: Path) -> pa.Table:
    rows = []
    with src.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append(obj if isinstance(obj, dict) else {"value": obj})
    return _rows_to_table(rows) if rows else pa.table({"_empty": pa.array([], type=pa.string())})


def _convert_tabular(src: Path, dest: Path) -> int:
    ext = src.suffix.lower()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if ext == ".geojson":
        return _convert_geojson(src, dest)
    if ext == ".jsonl":
        return _write_table(_read_jsonl_table(src), dest)
    if ext == ".json":
        return _write_table(_read_json_table(src), dest)
    if ext == ".tsv":
        return _write_table(_read_csv_typed(src, delimiter="\t"), dest)
    if ext in {".dat", ".txt"}:
        # Fixed identifier dumps (FCC ULS pipe-delimited, BEA readmes): all-string, sniffed.
        return _write_table(_read_csv_stdlib(src, delimiter=None), dest)
    return _write_table(_read_csv_typed(src, delimiter=","), dest)


def _rows_from_matrix(matrix: list[list]) -> list[dict]:
    if not matrix:
        return []
    headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(matrix[0])]
    return [
        {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
        for row in matrix[1:]
    ]


def _convert_spreadsheet(src: Path, dest: Path) -> tuple[bool, str, int]:
    ext = src.suffix.lower()
    if ext == ".xls":
        return _convert_xls(src, dest)
    try:
        import openpyxl  # type: ignore
    except ImportError:
        return False, "openpyxl_not_installed", 0
    try:
        wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001  (corrupt/truncated xlsx: skip, don't fail run)
        return False, f"xlsx_unreadable: {type(exc).__name__}", 0
    ws = wb.active
    matrix = [list(r) for r in ws.iter_rows(values_only=True)]
    if not matrix:
        return False, "empty_sheet", 0
    n = _write_rows_parquet(_rows_from_matrix(matrix), dest)
    return True, "ok", n


def _convert_xls(src: Path, dest: Path) -> tuple[bool, str, int]:
    try:
        import xlrd  # type: ignore
    except ImportError:
        return False, "xlrd_not_installed", 0
    try:
        book = xlrd.open_workbook(src)
    except Exception as exc:  # noqa: BLE001
        return False, f"xls_unreadable: {type(exc).__name__}", 0
    sheet = book.sheet_by_index(0)
    if sheet.nrows == 0:
        return False, "empty_sheet", 0
    matrix = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
    n = _write_rows_parquet(_rows_from_matrix(matrix), dest)
    return True, "ok", n


def convert_file(
    family: str,
    src: Path,
    run_id: str,
    *,
    force: bool = False,
) -> dict:
    rel = rel_under(UNWRAPPED / family, src)
    ok, reason = _should_convert(src)
    entry = {
        "family": family,
        "source": rel,
        "status": "skipped",
        "reason": reason,
    }
    if not ok:
        return entry

    sig = file_signature(src, with_md5=True)
    entry.update({"source_bytes": sig["bytes"], "source_sig": _source_key(sig)})
    dest = _parquet_out(run_id, family, rel)
    sidecar = dest.with_suffix(".parquet.meta.json")

    if not force and sidecar.exists():
        try:
            meta = json.loads(sidecar.read_text(encoding="utf-8"))
            if meta.get("source_sig") == entry["source_sig"] and dest.exists():
                entry["status"] = "skipped"
                entry["reason"] = "unchanged"
                entry["parquet"] = rel_under(run_dir(run_id), dest)
                return entry
        except json.JSONDecodeError:
            pass

    try:
        if reason == "spreadsheet":
            ok_x, msg, rows = _convert_spreadsheet(src, dest)
            if not ok_x:
                entry["status"] = "skipped"
                entry["reason"] = msg
                return entry
        else:
            try:
                rows = _convert_tabular(src, dest)
            except UnparseableSource as exc:
                entry["status"] = "skipped"
                entry["reason"] = str(exc)
                dest.unlink(missing_ok=True)
                return entry
        entry["status"] = "converted"
        entry["parquet"] = rel_under(run_dir(run_id), dest)
        entry["rows"] = rows
        write_json(
            sidecar,
            {
                "source": rel,
                "source_sig": entry["source_sig"],
                "parquet": entry["parquet"],
                "rows": rows,
                "updated_at": utc_now(),
            },
        )
    except Exception as exc:  # noqa: BLE001
        entry["status"] = "error"
        entry["error"] = repr(exc)
        if dest.exists():
            dest.unlink(missing_ok=True)
        sidecar.unlink(missing_ok=True)
    return entry


def copy_existing_parquet(family: str, src: Path, run_id: str) -> dict:
    rel = rel_under(UNWRAPPED / family, src)
    dest = _parquet_out(run_id, family, rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return {"family": family, "source": rel, "status": "skipped", "reason": "dest_exists"}
    shutil.copy2(src, dest)
    sig = file_signature(src, with_md5=False)
    write_json(
        dest.with_suffix(".parquet.meta.json"),
        {
            "source": rel,
            "source_sig": _source_key(sig),
            "parquet": rel_under(run_dir(run_id), dest),
            "copied_from_parquet": True,
            "updated_at": utc_now(),
        },
    )
    return {
        "family": family,
        "source": rel,
        "status": "copied",
        "parquet": rel_under(run_dir(run_id), dest),
    }


def parquet_family(family_dir: Path, run_id: str, *, force: bool = False, log_path: Path | None = None) -> dict:
    family = family_dir.name
    results = []
    for path in sorted(family_dir.rglob("*")):
        if not path.is_file() or path.name.endswith(".unwrap.done") or path.name == "manifest.json":
            continue
        if path.suffix.lower() == ".parquet":
            results.append(copy_existing_parquet(family, path, run_id))
            continue
        entry = convert_file(family, path, run_id, force=force)
        results.append(entry)
        if log_path and entry.get("status") == "converted":
            append_log(log_path, f"parquet {family}/{entry.get('source')} rows={entry.get('rows')}")

    converted = sum(1 for r in results if r["status"] in {"converted", "copied"})
    errors = sum(1 for r in results if r["status"] == "error")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    return {
        "family": family,
        "converted": converted,
        "skipped": skipped,
        "errors": errors,
        "files": results,
        "updated_at": utc_now(),
    }


def parquet_all(run_id: str, *, force: bool = False, families: list[str] | None = None, log_path: Path | None = None) -> dict:
    selected = families or sorted(p.name for p in UNWRAPPED.iterdir() if p.is_dir())
    family_results = []
    for name in selected:
        family_dir = UNWRAPPED / name
        if not family_dir.is_dir():
            continue
        family_results.append(parquet_family(family_dir, run_id, force=force, log_path=log_path))

    receipt = {
        "run_id": run_id,
        "updated_at": utc_now(),
        "dedupe_method": "source_sig sidecar in warehouse/catalog_parquet_v1",
        "converted_count": sum(r["converted"] for r in family_results),
        "skipped_count": sum(r["skipped"] for r in family_results),
        "error_count": sum(r["errors"] for r in family_results),
        "families": family_results,
    }
    out_manifest = run_dir(run_id) / "parquet_manifest.json"
    write_json(out_manifest, receipt)
    return receipt

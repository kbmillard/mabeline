---
name: mabeline-moving-connect
description: Query and wire Mabeline on-disk transportation data through the SCTG commodity spine. Use for moving-commodity ties, FAF5/CFS/FMCSA/rail/maritime questions, bin/mabel-catalog work, or when the user asks what's moving, #1 cargo, or how sources connect. Answers from raw _unwrapped data first, not receipt names or moneyball pitches. **Creed: newest first** — check file age and source vintage before ranking.
---

# The Mabeline Project — Moving Connect

## Thesis

```text
commodity moving a lot = the signal
```

Connect = every movement source answers the same question on **SCTG**: how much of this commodity is moving, by mode and corridor.

Not anchor. Not penny stocks. Not metal-lead pitches unless explicitly requested.

## Repo isolate + guardrail

Codex work stays **inside this repo's truth layer**: `_unwrapped/` bytes, `build_reports/` receipts, `.cursor/rules/`, this skill. Do not invent gaps from model memory — **exhaust open public bulk URLs and disk first** (`bin/mabel-catalog gaps`), then `missing-data-plan`. Guardrails beat improvisation.

## Before answering

0. **Newest first** — check `mtime`, `as_of`, and source year (FAF `tons_2024`, CFS 2022). Refresh FMCSA/EIA via `bin/mabel-catalog today` or `gaps` when stale.
1. **Query raw data** — run DuckDB or `bin/mabel-catalog` on disk. Do not guess from memory or cite JSON receipts when a one-line SQL answer exists.
2. **Answer the question first** — one direct line (e.g. "Coal, 15.4% of FAF5 2024 tons"). Details after.
3. **Finish the connect** — if wiring is requested, implement and run; do not stop at "next_layers" lists.

## Canonical paths

| Layer | Path |
|-------|------|
| All families | `_unwrapped/` (~248GB, see `manifest.json`) |
| **Today manifest** | `_unwrapped/today/2026-07-09/` (symlinks to freshest transport bytes) |
| FAF5 flows | `_unwrapped/faf5_freight/release=2026-07-05/faf5_csv/FAF5.7.1.csv` |
| CFS shipments | `_unwrapped/trade/release=2026-07-05/cfs_2022_pums/cfs_2022_pums.csv` |
| FMCSA census | `_unwrapped/fmcsa_carriers/company_census.csv` |
| FMCSA inspections | `_unwrapped/fmcsa_carriers/mcmis/vehicle_inspection_file.csv` |
| Crude imports (**newest**) | `_unwrapped/maritime/release=2026-07-09/PET_IMPORTS/PET_IMPORTS.txt` |
| EIA coal series (**newest**) | `_unwrapped/rail/release=2026-07-09/COAL/COAL.txt` |
| STB EP724 (**newest**) | `_unwrapped/stb_rail/release=2026-07-09/ep724-*.csv` |
| STB rail (legacy) | `_unwrapped/stb_rail/` |
| PHMSA pipelines | `_unwrapped/phmsa_pipelines/` |

**Spine code still reads `release=2026-07-05` PET** in `commodity_economy.py` — receipts stale until wired. Prefer newest paths above for ad-hoc queries.

Python constants: `catalog.config.ROOT`, `UNWRAPPED`; `catalog.freight_movement.FAF_CSV`, `SCTG2_LABELS`, `MODE_LABELS`.

CLI: `bin/mabel-catalog <command>` from repo root (`.venv/bin/python -m catalog`).

## SCTG spine (connect key)

```text
SCTG code
  ├─ FAF5: tons_{year}, dms_mode, dms_orig, dms_dest  (thousand tons)
  ├─ CFS 2022: shipment weight by SCTG
  ├─ FMCSA: CRGO_* cert flags + inspection shipper→carrier (no SCTG per stop)
  ├─ PET_IMPORTS: crude by port/refinery (SCTG 17/12 family)
  ├─ STB rail: commodity filings (not fully wired in catalog yet)
  └─ PHMSA: pipeline mileage (not fully wired yet)
```

**Wired today:** `moving-commodity` (FAF5+CFS), `transport-economy` (+FMCSA inspections), `commodity-economy` (+EIA imports, USGS).

**Not wired yet:** STB, PHMSA, full rail tonnage onto ranked index.

## FAF5 rules

- Units in file: **thousand tons**, million ton-miles, million dollars.
- Year columns on disk: `tons_2022`, `tons_2023`, `tons_2024`, then `tons_2030`, `tons_2035`, `tons_2040`, `tons_2045`, `tons_2050`. **No `tons_2026`.** Latest base year = **2024**.
- Modes: `1` Truck, `2` Rail, `3` Water, `4` Air, `5` Multiple, `6` Pipeline, `7` Other.
- 2024 #1 by tons: **Coal (SCTG 19)** ~15.4% national modeled flow.

## Quick raw query (default for "what's #1")

```bash
cd /Users/kyle/Documents/mabeline && .venv/bin/python -c "
import duckdb
from catalog.freight_movement import FAF_CSV, SCTG2_LABELS
con = duckdb.connect()
rows = con.execute('''
  SELECT sctg2, SUM(TRY_CAST(tons_2024 AS DOUBLE)) ktons
  FROM read_csv_auto(?, header=true, ignore_errors=true)
  WHERE sctg2 IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 5
''', [str(FAF_CSV)]).fetchall()
total = con.execute('SELECT SUM(TRY_CAST(tons_2024 AS DOUBLE)) FROM read_csv_auto(?, header=true, ignore_errors=true)', [str(FAF_CSV)]).fetchone()[0]
for s, kt in rows:
    print(SCTG2_LABELS.get(str(s).zfill(2)[:2], s), f'{100*kt/total:.1f}%')
"
```

## FMCSA rules

- Join inspections to census on `DOT_NUMBER`.
- Cargo cert flags: active value is **`X`**, not `Y`.
- **`CRGO_*` census flags alone are untrusted** for ranked carrier lists (fraud/noise at high fleet counts). Use inspection `SHIPPER_NAME` ties; filter fleet size when ranking.
- CSV reads: `read_csv_auto(..., header=true, ignore_errors=true)` — file has malformed rows.
- Inspections document **shipper name** (~63% of rows); that is not SCTG commodity per truck. Top lane in ties = **general_freight** (retail logistics), not national tonnage rank.
- Example frozen query: Dollar General → **716** distinct DOTs; top = D G LOGISTICS LLC (1,420 stops), Werner (1,313), Schneider (407).

## Catalog commands (movement focus)

| Command | Purpose |
|---------|---------|
| `today` | **Newest-first ingest** → gaps + unwrap + `_unwrapped/today/YYYY-MM-DD/` |
| `gaps` | Exhaust open-source bulk (Census IMDB/EXDB, STB R-1, BSEE, FMCSA, EIA) |
| `missing-data-plan` | Post-exhaust scan — wiring debt vs real gaps only |
| `moving-commodity` | **Canonical simple tie** — FAF5 % + CFS % on SCTG |
| `freight-movement` | FAF5 national/corridor/mode receipt |
| `transport-economy` | SCTG + FAF5 + CFS + FMCSA + inspections (heavier) |
| `commodity-economy` | FAF5 + CFS + PET_IMPORTS + USGS slate |
| `thg-build` | Materialize `temporal_edge_events` from FMCSA + macro + EIA + Iran origin_pressure + IMDB + SMS + PHMSA + identity |
| `thg-baseline` | Month-over-month `temporal_change_scores_v1` (+ corridor parquet) |
| `thg-linear` | Full wire: build → baseline → radar → dollar-to-million |
| `thg-query` | Developer one-liner: truck delta vs FAF residual + top corridors (+ Iran oil join for SCTG 17) |
| `htgnn-train` / `htgnn-score` | Scaled subsample embeddings (default 250k edges) on THG |
| `find-cargo` | FMCSA shipper→carrier inspection ties |
| `sync-financial` | Copy receipts → `financial/src/data/` |

Avoid leading with `moneyball`, `forward-screen`, or `money-spider` unless user asks.

## THG hello-world (events are the product)

```bash
cd /Users/kyle/Documents/mabeline
bin/mabel-catalog thg-query --sctg2 19 --month 202605
```

Or DuckDB directly on quantized events:

```bash
.venv/bin/python -c "
import duckdb
from catalog.graph.schema_v1 import OUTPUTS
p = str(OUTPUTS['events'])
con = duckdb.connect()
print(con.execute('''
  SELECT edge_type, COUNT(*) n, ROUND(SUM(weight),1) w
  FROM read_parquet(?)
  WHERE json_extract_string(attrs_json, \"$.sctg2\") = '19'
     OR (edge_type = 'hauls_commodity' AND dst_id = '19')
  GROUP BY 1 ORDER BY w DESC
''', [p]).fetchall())
"
```

Graph artifacts: `warehouse/th_graph_v1/temporal_edge_events_v1.parquet`, `temporal_change_scores_v1.parquet`, `node_embeddings_v1.parquet`.

## Scoring (moving-commodity)

```text
moving_a_lot_score = 0.6 * faf5_pct_of_national + 0.4 * cfs_pct_of_shipments
```

Rank by this for "what's moving a lot." Do not rank by FMCSA carrier count (that puts mixed freight / FedEx on top).

## Output locations

- Receipts: `build_reports/`
- CSV exports: `exports/`
- Log: `reports/build_status.log`

## Anti-patterns

- Naming receipt files instead of answering from raw data
- Claiming 2026 FAF5 columns exist
- Therapist/girlfriend tone; engagement bait ("want me to…?") at end
- Cloud-style advice without opening `_unwrapped/`
- Treating moneyball/penny screen as the product story
- Stopping at half-wired pipelines when user asked for the connect
- Listing missing data before `gaps` exhaust and disk validation
- Treating API keys as blockers when public bulk ZIPs exist on census.gov / stb.gov

## When wiring new layers

1. Map source field → SCTG (or document explicit gap)
2. Add leg in `catalog/moving_commodity.py` or dedicated module
3. Run command, verify top-3 unchanged or explain why
4. Write receipt + CSV export
5. Add to `catalog/financial_sync.py` `RECEIPT_SOURCES` if dashboard needs it

## Additional reference

- Full path table and JSON line formats: [reference.md](reference.md)

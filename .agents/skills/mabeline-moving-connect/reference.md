# The Mabeline Project — moving connect — reference

## Repo layout

```text
/Users/kyle/Documents/mabeline/
  _unwrapped/          # canonical raw (read-only unless acquiring)
  catalog/             # DuckDB pipelines
  bin/mabel-catalog    # CLI entry
  build_reports/       # generated JSON receipts
  exports/             # generated CSV
  financial/           # Next.js dashboard (separate git)
  manifest.json        # 61 families, byte totals
```

## FAF5.7.1.csv key columns

- `sctg2` — 2-digit SCTG commodity
- `dms_orig`, `dms_dest` — FAF zone codes
- `dms_mode` — mode code (see MODE_LABELS in `catalog/freight_movement.py`)
- `tons_2024`, `tmiles_2024`, `value_2024` — and forecast years 2030–2050

## CFS 2022 PUMS

- Shipment-level survey; aggregate by SCTG for shipment ton %.
- Path: `_unwrapped/trade/release=2026-07-05/cfs_2022_pums/cfs_2022_pums.csv`

## PET_IMPORTS.txt

- JSON lines per series; `units`: thousand barrels; monthly `data` arrays.
- Crude imports by port/refinery — ties to petroleum movement (SCTG 12/17), not full SCTG grid.

## rail/COAL.txt

- EIA JSON lines: coal consumption/heat content by state/sector — supplementary coal evidence, not FAF5 tonnage.

## SCTG2_LABELS (partial)

| Code | Commodity |
|------|-----------|
| 02 | Cereal grains |
| 12 | Gasoline & jet fuel |
| 17 | Petroleum products |
| 19 | Coal |
| 31 | Mixed freight |
| 41 | Waste/scrap |

Full map: `catalog/freight_movement.py` → `SCTG2_LABELS`.

## FMCSA CRGO flags (census)

Examples: `CRGO_GRAINFEED`, `CRGO_LIQGAS`, `CRGO_COALCOKE`, `CRGO_CHEM`, `CRGO_GENFREIGHT`, `CRGO_GARBAGE`.
Active = `'X'`.

## transport_economy SCTG_WIRE

Maps select SCTG → FMCSA `crgo` tuple + inspection `lanes` — see `catalog/transport_economy.py`.

## Cursor memory (not in repo)

Chat transcripts: `~/.cursor/projects/Users-kyle-Documents-mabeline/agent-transcripts/`
Repo has no `.cursor/` except skills you add under `.cursor/skills/`.

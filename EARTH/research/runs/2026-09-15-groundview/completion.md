# GroundView software completion

> **Superseded.** Full P0–P18 blueprint: [`BLUEPRINT.md`](./BLUEPRINT.md). Live ledger: `SkyView/GROUNDVIEW_STATUS.md`.

Phases 0–14 are software-complete on fixtures and replay. Empirical RF remains FIELD_VALIDATION_REQUIRED.

## Gates

P0 hygiene (parked `wip/mabeline-layers`, branched `wip/groundview` from chrome `6e67a6b`) → Foundation (`groundview_event_v1`, one `normalize_event`, storage boundary, deterministic IDs, clock provenance) → P1 matcher/cluster → P2 globe → P3 tracks → P4 node → P5 decoder lab → P6 experiments → P7–P9 camera/OCR/bind (optional) → P10 federation (same normalizer) → P11 playback → P12 health → P13 calibrate beside v1 → P14 GROUNDVIEW product surface, default OFF.

## Files

- `SkyView/src/data/groundview/{constants,canonical,match,cluster,clock,presentation}.mjs`
- `SkyView/src/data/groundview.js` (Cesium layer)
- `SkyView/server/providers/groundview/{engine,store,http,normalize,ids}.js` plus `rf/`, `receiver-node/`, `federation/`, `camera/`, `identity/`, `binding/`
- `SkyView/fixtures/groundview/synthetic.mjs`
- `SkyView/scripts/groundview-replay.mjs`
- `SkyView/GROUNDVIEW_STATUS.md`

## APIs

`/api/groundview/snapshot`, `/replay`, `/receivers`, `/observations`, `/passes`, `/fingerprints`, `/matches`, `/tracks`, `/playback?at=`, `/health`, `/node/events`, `/node/heartbeat`, `/experiments/replay`, `/camera-observations`, `/visual-identities`, `/bindings`

## Storage

Observed append-only JSON at `.gev-cache/groundview/state.json`. Derived/inferred keyed by versioned snapshots. Memory-only on Vercel. Node ingest 503 on Vercel.

## Matcher path

Hard gates → `100*(0.50 overlap + 0.30 shared_count_strength + 0.20 jaccard)` → caps 19/49/69/84/100 → competition among feasible candidates only → clamp 0–100. No `confirmed`.

## Replay / tests

```bash
cd SkyView
node --test src/data/groundview/*.test.mjs
node scripts/groundview-replay.mjs
```

## Actual 89.29

Canonical 7-vs-5 subset (`A,B,C,D,E,F,G` vs `A,B,D,E,F`) scores **89.29** (`100*(0.5*1 + 0.3*(5/6) + 0.2*(5/7))`).

## Enable locally

`npm run dev` in SkyView → The Mabeline Project → GROUNDVIEW. Chips: RECEIVERS, TRUCK PASSES, MATCHES, TRACKS. Passes are receiver coverage, not vehicle GPS.

## STATUS resume

`SkyView/GROUNDVIEW_STATUS.md`

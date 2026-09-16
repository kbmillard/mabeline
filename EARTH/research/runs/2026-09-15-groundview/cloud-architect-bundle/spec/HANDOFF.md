# GroundView cloud-architect handoff

Paste this entire file. You cannot see the laptop. Do not pretend you opened a local path, queried a receiver, or deployed GroundView. The inventories below are the corpus, snapshotted 2026-09-15 from the live SkyView checkout. This tar is the source tree, not a running SDR.

You are not building a second globe, a scraper, or a warehouse merge. You are reviewing GroundView as it exists after software phases 0–14, and advising only on what a cloud architect can honestly do next given hosting, truth-model, and git constraints.

---

## Status of the 1–14 plan

**Software path P0–P14 is complete** on fixtures and replay. There is no remaining software gate from the original plan.

| Phase | Software | Empirical |
| --- | --- | --- |
| P0 hygiene | done | n/a |
| Foundation envelope / `normalize_event` / store / IDs / clock | done | n/a |
| P1 matcher + cluster | done; canonical **89.29** | field capture rate FIELD_VALIDATION_REQUIRED |
| P2 GROUNDVIEW globe layer | done; default OFF | n/a |
| P3 tracks A→B→C, forks, weak edges | done | n/a |
| P4 receiver node `/node/events` + heartbeat | done | live node FIELD_VALIDATION_REQUIRED |
| P5 decoder lab | done | real decoder accuracy FIELD_VALIDATION_REQUIRED |
| P6 experiments | done | n/a |
| P7–P9 camera / OCR / bind | software path done | camera/OCR field accuracy FIELD_VALIDATION_REQUIRED |
| P10 federation | same `normalize_event` | n/a |
| P11 replay + `/playback?at=` | done | n/a |
| P12 `/health` | done | n/a |
| P13 calibrate | v1 frozen; future matcher must sit **beside** v1 | precision/recall FIELD_VALIDATION_REQUIRED |
| P14 product surface | GROUNDVIEW chips; click cards | n/a |

**Not done, by design:** live rtl_433, empirical RF, real-road travel times, camera/OCR in the field. A green fixture run is not a capture-rate claim.

**Do not overwrite `groundview_match_v1`.** A later matcher is `groundview_match_v2` beside v1.

---

## What GroundView is

Parent: The Mabeline Project. Application: SkyView (not a second app). Surface: local SkyView globe. Production earth does **not** ship GroundView.

Core question: can persistent RF (TPMS etc.) from one passing tractor-trailer form a composite fingerprint so the same road unit can be recognized at a downstream receiver?

Road unit v1 = tractor + attached trailer traveling together. No tractor/trailer split required.

Cesium is a **projection**, not truth. Passes are drawn at **receiver coverage**, never as invented vehicle GPS. Confidence never uses the label `confirmed`.

Provenance:

- OBSERVED = received/measured
- DERIVED = deterministic processing of observed
- INFERRED = probabilistic identity / continuity

Never silently promote DERIVED/INFERRED to OBSERVED.

Canonical identity: `protocol:model:sensor_id` under `groundview_canonical_v1`. Example rtl_433: `rtl433_protocol:model:sensor_id`.

---

## Matcher contract (`groundview_match_v1`) frozen

Hard gates (travel window, direction) → base score → overlap caps → competition among **feasible** candidates only → clamp 0–100.

```
base = 100 * (0.50 * overlap_coefficient + 0.30 * shared_count_strength + 0.20 * jaccard)
shared_count_strength = min(shared_count / 6, 1)
caps by shared_count: 0→0, 1→19, 2→49, 3→69, 4→84, ≥5→100
```

Canonical fixture: set A `{A,B,C,D,E,F,G}` vs set B `{A,B,D,E,F}` → **89.29**  
`100 * (0.5*1 + 0.3*(5/6) + 0.2*(5/7))`.

Labels: weak / possible / strong / very_strong. **Forbidden: confirmed.**

Owner-verified on the globe 2026-09-15: click card read `Match very_strong 89.29` / `INFERRED · not confirmed` / `shared 5` / `groundview_match_v1`. Receiver card: `OBSERVED receiver site` / `Coverage pin, not a vehicle GPS fix`.

---

## Synthetic fixture (not a real radio network)

Three placeholder receivers on a made-up eastbound Kansas City corridor:

| id | lat | lon | meaning |
| --- | --- | --- | --- |
| GV-RX-01 | 39.0997 | -94.5786 | Wikipedia KC centroid; lands in a residential grid. Not a sited SDR. |
| GV-RX-02 | 39.1142 | -94.5410 | placeholder |
| GV-RX-03 | 39.1300 | -94.5000 | placeholder |

Links: 60–600 s travel windows. Replay: 36 packets, 9 passes, 20 matches, 5 tracks.

Do not treat these coordinates as field sites or recommend moving them without a real receiver survey.

---

## Hosting and git (binding)

- Working tree: SkyView branch `wip/groundview`, **local only. Do not push. Do not `vercel --prod` GroundView.**
- Chrome production earth: Vercel project `earth` / https://skyprairie.io/earth. Ships **without** GroundView.
- Pipeline offices (PHMSA) were removed from chrome `main` `2cb1fc0` and deployed; unrelated to GroundView. Share-link token `p` now fail-closed.
- GroundView share-link token: `k` (enabled-only). Presentation chips are local UI, not share-link options.
- Storage: `.gev-cache/groundview/state.json` locally. **Memory-only when `VERCEL` is set.** `POST /api/groundview/node/events` returns **503 on Vercel**. Long-lived ingest needs a persistent host, not a new Vercel project invented for preference.
- Do not mix Mabeline warehouse / financial / Dispatch / Place-of-Performance dirt into GroundView.
- Anchor/NAICS/SIC/spine rules still apply to any Mabeline join you propose: NAICS is not identity; unknown is not zero; raw data is immutable.

---

## APIs (local Vite plugin `groundview-proxy`)

Prefix `/api/groundview`

GET: `/snapshot`, `/playback?at=`, `/receivers`, `/observations`, `/passes`, `/fingerprints`, `/matches`, `/tracks`, `/cameras`, `/camera-observations`, `/visual-identities`, `/bindings`, `/experiments`, `/health`

POST: `/replay` (`{fixture:'synthetic'}`), `/receivers`, `/node/events`, `/node/heartbeat`, `/experiments/replay`, `/camera-observations`, `/visual-identities`, `/bindings`

Empty local store auto-seeds the synthetic fixture so the globe is exercisable without SDR.

---

## File map in this tar

```
HANDOFF.md                          this file
spec/                               authoritative spec copy + STATUS + notes
skyview-groundview/                 engine, store, HTTP, Cesium layer, tests, fixture
skyview-wiring/                     chrome integration files as they exist on wip/groundview
evidence/replay.json                `node scripts/groundview-replay.mjs` output
```

Authoritative spec on the laptop: Desktop `GroundView.rtf` (copy under `spec/`). Matcher version strings must match `src/data/groundview/constants.mjs`.

---

## What a cloud architect may recommend

Allowed:

- Persistent host options for node ingest (not a second globe, not a new Vercel project unless the owner asks).
- How GroundView could later join Mabeline **without** treating RF matches as GPS tracks or warehouse identity.
- Field protocol: rtl_433 NDJSON → same `normalize_event` → do not fork a second pipeline.
- `groundview_match_v2` design notes that keep v1 outputs reproducible.

Reject:

- “Put GroundView on skyprairie.io/earth this week.”
- “Confirmed trucks on the globe.”
- “Download OSM / a commercial GPS feed first.”
- “Overwrite v1 weights after looking at one capture.”
- Treating the residential GV-RX-01 pin as a real tower.
- Mixing FMCSA / Dispatch / warehouse identity into the matcher.

---

## Local how-to (owner already did this)

```bash
cd SkyView
npm run dev          # e.g. http://127.0.0.1:4173/
node --test src/data/groundview/*.test.mjs
node scripts/groundview-replay.mjs
```

DATA LAYERS → The Mabeline Project → GROUNDVIEW (starts off). Chips: RECEIVERS / TRUCK PASSES / MATCHES / TRACKS. Click entities for cards.

Post-plan chrome extras on the same working tree (not in P0–P14): WGS84 coordinate parse in the LOCATION bar; click cards via `trackedReadout` allowlisting `groundview`.

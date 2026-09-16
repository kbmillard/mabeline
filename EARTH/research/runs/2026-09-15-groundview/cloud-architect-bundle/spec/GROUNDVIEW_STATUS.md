# GROUNDVIEW_STATUS

Persistent multi-session ledger. Do not treat this file as a substitute for the Desktop `GROUNDVIEW_PROJECT` spec.

## Specification

- authoritative_prompt_path: `/Users/kyle/Desktop/GroundView.rtf` (copy: `EARTH/research/runs/2026-09-15-groundview/`)
- working_branch: `wip/groundview` (local only; do not push)
- last_reviewed_commit: `6e67a6b` (chrome production baseline; verified 2026-09-15)
- parked_unrelated_work: `wip/mabeline-layers` @ `2daf72b` (Dispatch, offices, divisions, Place-of-Performance)

## Execution

- active_phases: none (software path P0–P14 complete on fixtures/replay)
- software_complete: [P0, Foundation, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14]
- field_validation_required: [empirical RF capture, live rtl_433, camera/OCR field accuracy]
- blocked: []
- invalidated_by_upstream_change: []

## Authoritative versions

- event_schema: `groundview_event_v1`
- canonicalization: `groundview_canonical_v1`
- clustering: `groundview_cluster_v1`
- matcher: `groundview_match_v1`
- track_builder: `groundview_track_v1`
- camera_detector: optional / not field-validated
- visual_recognizer: optional / not field-validated
- binding: optional / not field-validated

## Repository integration map

- provider_pattern: Vite plugin `groundview-proxy` via `server/providers/local.js`
- api_pattern: `/api/groundview/*` (`snapshot`, `replay`, `matches`, `tracks`, `node/events`, `health`, `playback`)
- storage_pattern: `.gev-cache/groundview/state.json` behind `createGroundViewStore`; memory-only when `VERCEL` is set
- cesium_lifecycle_pattern: `src/data/groundview.js` CustomDataSource init/enable/disable/update/destroy
- layer_state_pattern: id `groundview`, token `k`, enabled-only; presentation chips are local UI
- selection_pattern: pick owner `groundview:` + entity context with provenance and score components
- credit_pattern: `src/data/dataCredits.js` key `groundview`, `showOnScreen=false`
- test_commands: `npm test`; focused `node --test src/data/groundview/*.test.mjs`; replay `node scripts/groundview-replay.mjs`
- hosted_unavailable_pattern: `POST /api/groundview/node/events` returns 503 on Vercel; no Vercel disk store

## Git / prod rules in force

- No `vercel --prod`
- No new Vercel project
- No mix of financial/warehouse/Dispatch into GroundView commits
- Production earth remains chrome HEAD only

## Phase gates

| phase | status | commit | commands | evidence |
| --- | --- | --- | --- | --- |
| P0 | PASS | wip/groundview from 6e67a6b | inspect remotes/HEAD; park `wip/mabeline-layers`; STATUS; spec copy | dirty Mabeline tree preserved locally |
| Foundation | PASS | local | envelope + `normalize_event` + store + IDs + clock | adapters share one normalizer |
| P1 | PASS | local | `node --test src/data/groundview/*.test.mjs` | canonical 89.29; competition universe |
| P2 | PASS | local | layer id `groundview` under The Mabeline Project | Cesium projection only |
| P3 | PASS | local | tracks A→B→C, forks, weak edges | no permanent vehicle id |
| P4 | PASS | local | `/node/events` + heartbeat | same `normalize_event` |
| P5 | PASS | local | decoder lab `rf/lab.js` | capture_ref provenance |
| P6 | PASS | local | `runExperiment` | snapshots + metrics |
| P7–P9 | PASS | local | camera/OCR/bind fixtures | RF works with camera absent; OCR INFERRED |
| P10 | PASS | local | federation peer uses same normalizer | no second pipeline |
| P11 | PASS | local | `replay` + `playback?at=` | historical rebuild from immutable observations |
| P12 | PASS | local | `/health` | receiver/clock/decoder/ingest/cluster/matcher |
| P13 | PASS | local | `calibrate` | v1 beside future matcher note |
| P14 | PASS | local | default OFF; chips RECEIVERS/PASSES/MATCHES/TRACKS | off-state equals baseline globe |

## Tests last run

- tests last run: `npm test` → 3131 pass, 9 fail, 1 skip. GroundView 21/21 pass. Remaining fails are pre-existing chrome CSS/path/preview issues (creditAttribution, CCTV /private vs /var, mapSourceFocus LOCATION markup, previewServing vite tmp path), not GroundView.
- replay: `node scripts/groundview-replay.mjs` → canonical_89_29 = 89.29

## Architectural decisions

- Preserve unrelated dirty work on `wip/mabeline-layers`; GroundView from `6e67a6b` (no reset).
- Storage: JSON under `.gev-cache/groundview/` behind `createGroundViewStore`; memory-only when `VERCEL` is set.
- Layer share-link token `k`; presentation filters are local UI, not share-link options.
- Cesium is a projection of `/api/groundview/*` state. Passes sit at receiver coverage.
- Local empty stores seed the synthetic fixture so GROUNDVIEW is exercisable without SDR.

## How to enable locally

1. `cd SkyView && npm run dev`
2. Open DATA LAYERS → The Mabeline Project → **GROUNDVIEW**
3. Chips: RECEIVERS, TRUCK PASSES, MATCHES, TRACKS
4. Replay without UI: `node scripts/groundview-replay.mjs`

## Next safe resume action

Field capture (rtl_433 live) when hardware exists. Do not overwrite `groundview_match_v1`. A future matcher must run beside v1.

## Rerun before continuing

`node --test src/data/groundview/*.test.mjs` and `node scripts/groundview-replay.mjs`

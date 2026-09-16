# GROUNDVIEW_STATUS

Persistent multi-session ledger. Do not treat this file as a substitute for the committed P15–P18 execution spec.

## Specification

- **unified_blueprint:** `EARTH/research/runs/2026-09-15-groundview/BLUEPRINT.md` (P0–P18 narrative; see also END_STATE for P19+)
- **end_state:** `SkyView/GROUNDVIEW_END_STATE.md`
- **field_method:** `SkyView/GROUNDVIEW_FIELD_METHOD.md`
- **operations:** `SkyView/GROUNDVIEW_OPERATIONS.md`
- **traceability:** `SkyView/GROUNDVIEW_TRACEABILITY.md`
- **mega_prompt_archive:** `EARTH/research/runs/2026-09-15-groundview/GroundView-Mega-Prompt.md`
- **verification_pack:** `EARTH/research/runs/2026-09-15-groundview/verification/mega-prompt-verification.md`
- **authoritative_execution_spec:** `SkyView/GROUNDVIEW_SPEC.md`
- **authoritative_execution_spec_archive:** `EARTH/research/runs/2026-09-15-groundview/GroundView-P15-P18.md`
- **historical_completed_p0_p14_spec:** `EARTH/research/runs/2026-09-15-groundview/GroundView.md` (historical/completed; not current execution instructions)
- **historical_completed_p0_p14_rtf:** `EARTH/research/runs/2026-09-15-groundview/GroundView.rtf`
- working_branch: `wip/groundview` (local only; do not push)
- last_reviewed_commit: `6e67a6b` (chrome production baseline; verified 2026-09-15)
- parked_unrelated_work: `wip/mabeline-layers` @ `2daf72b` (Dispatch, offices, divisions, Place-of-Performance)

A future session must determine from this file that **P0–P15 are PASS**, **P16–P18 are SOFTWARE_COMPLETE**, **P19–P30 / GV-C1–C14 software instruments are SOFTWARE_FOUNDATION_READY** (or listed PASS where software-complete), and **all empirical field claims remain FIELD_VALIDATION_REQUIRED until physical evidence exists**.

## Execution

- active_phases: **P19 physical ACTIVE_ACQUISITION — next step = buy \$450 cart (`field/BUY.md`)** then survey → freeze → capture → analyze → P20+
- budget_lock_usd: **450** (lean dual-receiver, Mac host, no Pi)
- software_complete: [P0, Foundation, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P17, P18]
- software_foundation_ready: [requirements/traceability, manifest-v2, clock-quality, receiver-profile, comparability reports, blinded-eval schemas, GV-C1–C14 foundations, P19–P30 field/ops instruments]
- p19_interpretation: one-site physical RF reality. **FIELD_VALIDATION_REQUIRED / ACTIVE_ACQUISITION**. Host prep DONE on Mac (`rtl_433` 25.12, secrets file, spool, `groundview-field-day.sh`). Still missing: USB SDR, antenna, Site A survey, clock freeze. No fabricated capture rates.
- p20_p23_interpretation: empirical **BLOCKED_ON_P19** (see `field/sessions/p20_p23_blocked_status.json`); promotion without field labels remains RETAIN_V1; journeys stay OFF.
- field_validation_required: [P19 live capture, P20 dual-site, P21 labelled eval, P22 corridor, P23 authoritative motion, P25+ ops]
- blocked: []
- invalidated_by_upstream_change: []

## Physical field pack (this session)

| Artifact | Path |
| --- | --- |
| BOM + budget lock | `EARTH/.../field/BOM.md` (**\$450**) |
| Buy cart | `EARTH/.../field/BUY.md` |
| Secrets setup | `EARTH/.../field/SECRETS_SETUP.md` (file already on this Mac) |
| Field day one-shot | `SkyView/scripts/groundview-field-day.sh` |
| Site A | `EARTH/.../field/sites/SITE_A.md` + `SITE_A_SURVEY.json` |
| Sites B/C | `EARTH/.../field/sites/SITE_B_C.md` |
| Install | `EARTH/.../field/INSTALL.md` |
| Capture | `SkyView/scripts/groundview-field-capture.sh` + `groundview-field-ingest-stream.mjs` |
| Freeze / analyze | `groundview-field-freeze.mjs`, `groundview-field-analyze.mjs` |
| P19 acquisition ledger | `field/sessions/p19_acquisition_status.json` → outcome FIELD_VALIDATION_REQUIRED |
| P20–P23 blocked status | `field/sessions/p20_p23_blocked_status.json` |

## Full gate matrix — P19–P30

| item | software gate | empirical gate | notes |
| --- | --- | --- | --- |
| P19 one-site RF | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | `p19FieldSession.mjs` + `scripts/groundview-p19-field.mjs`; missing hardware prerequisites |
| P20 two-site A→B | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | `p20p21Field.mjs`; requires P19 PASS |
| P21 blinded eval / promotion | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | freeze/join/promotion retain v1 without field labels |
| P22 corridor continuity | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | ≥3 sites; unlocks journey/gap empirical authority when PASS |
| P23 branch-safe transit | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | presentation flags stay OFF until P22 PASS |
| P24 storage migration | SOFTWARE_FOUNDATION_READY | N/A (conditional) | migrate only if measured bottleneck; currently `migrate_now=false` |
| P25 regional network | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | health/profiles/clocks/spool/retention/on-call plan |
| P26 multi-region | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | federation interfaces; real ops earned |
| P27 episode service | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | query/playback; no second globe |
| P28 Mabeline bridge | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | edge exists; cannot contaminate matcher-v1 |
| P29 surface | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED | chips/cards/playback/provenance; journeys OFF by default |
| P30 hardening / expand | SOFTWARE_FOUNDATION_READY | auth-gated | `vercel_prod_allowed=false` without explicit order |

## Full gate matrix — GV-C1–C14

| capability | software gate | empirical authority |
| --- | --- | --- |
| GV-C1 journey | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED (unlock via P22) |
| GV-C2 road network | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED |
| GV-C3 live track state | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED |
| GV-C4 prediction | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED |
| GV-C5 gap bridging | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED (unlock via P22) |
| GV-C6 facility | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED |
| GV-C7 destination | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED |
| GV-C8 Mabeline edge | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED |
| GV-C9 network ops | SOFTWARE_FOUNDATION_READY | FIELD_VALIDATION_REQUIRED (P25) |
| GV-C10 capacity | SOFTWARE_FOUNDATION_READY | measured before P24 |
| GV-C11 security lifecycle | SOFTWARE_FOUNDATION_READY | ops decisions pending |
| GV-C12 anonymous recurrence | SOFTWARE_FOUNDATION_READY | no longitudinal identity claims |
| GV-C13 fusion research | SOFTWARE_FOUNDATION_READY | beside v1; never feeds matcher-v1 |
| GV-C14 live ground layer | SOFTWARE_FOUNDATION_READY | OBSERVED vs INFERRED chrome; flags default OFF |

## P16–P18 execution clarifications (locked)

- **P16 source_event_id:** assigned at durable spool boundary before retryable; stable across adapter/uploader restart, network retry, and central duplicate ACK.
- **P17 drill semantics:** drill coordinates/travel windows/links are test inputs only; reports must state metrics are pipeline validation, not real RF performance.
- **P18 research boundary:** drill labels validate research-runner mechanics only; no v2 justified from drill data; `groundview_match_v1` remains authoritative until independently labelled field evidence exists.

## Authoritative versions

- event_schema: `groundview_event_v1`
- storage_schema: `groundview_store_v1`
- canonicalization: `groundview_canonical_v1`
- clustering: `groundview_cluster_v1`
- matcher: `groundview_match_v1` (pre-field competition defect corrected: shares pass A OR pass B)
- research_matcher: `groundview_match_research_v0` (mechanics only; not production)
- fusion_research: `groundview_fusion_research_v0` (beside v1; never feeds matcher)
- anonymous_recurrence: `groundview_anonymous_recurrence_research_v0`
- comparability_report: `groundview_comparability_report_v1`
- receiver_spool: `groundview_receiver_spool_v1`
- track_builder: `groundview_track_v1`
- receiver_auth: `groundview_receiver_auth_v1`
- requirements: `groundview_requirements_v1`
- run_manifest: `groundview_run_manifest_v2` (additive beside legacy manifests)
- clock_quality: `groundview_clock_quality_v1`
- receiver_profile: `groundview_receiver_profile_v1`
- ground_truth: `groundview_ground_truth_v1`
- evaluation_plan: `groundview_evaluation_plan_v1`
- matcher_promotion: `groundview_matcher_promotion_v1`
- journey: `groundview_journey_v1`
- road_network: `groundview_road_network_v1`
- transit_state: `groundview_transit_state_v1`
- evidence_bundle: `groundview_evidence_bundle_v1`
- episode_service: `groundview_episode_service_v1`
- multi_region: `groundview_multi_region_v1`
- surface_contract: `groundview_surface_contract_v1`
- camera_detector: optional / not field-validated
- visual_recognizer: optional / not field-validated
- binding: optional / not field-validated

## Repository integration map

- provider_pattern: Vite plugin `groundview-proxy` via `server/providers/local.js` (`surface: 'all'`). Field-only factory: `createGroundViewFieldHttp`.
- api_pattern: `/api/groundview/*` (`snapshot`, `replay`, `matches`, `tracks`, `node/events`, `node/heartbeat`, `health`, `playback`)
- canonical_hmac_paths: `/api/groundview/node/events`, `/api/groundview/node/heartbeat`
- storage_pattern: `.gev-cache/groundview/state.json` behind `createGroundViewStore`; memory-only when `VERCEL` is set; **single writer process**; fail-closed except ENOENT
- cesium_lifecycle_pattern: `src/data/groundview.js` CustomDataSource; journeys/envelopes/gaps adapters present, default OFF
- layer_state_pattern: id `groundview`, token `k`, enabled-only; presentation chips are local UI
- selection_pattern: pick owner `groundview:` + entity context with provenance and score components
- credit_pattern: `src/data/dataCredits.js` key `groundview`, `showOnScreen=false`
- test_commands: `node --test src/data/groundview/*.test.mjs`; replay `node scripts/groundview-replay.mjs`; verify `node scripts/groundview-verify-pack.mjs`; P19 `node scripts/groundview-p19-field.mjs --check`
- receiver_node_pattern: `server/providers/groundview/receiver-node/`; CLI `scripts/groundview-receiver-node.mjs`
- hosted_unavailable_pattern: node ingest returns 503 on Vercel; no Vercel disk store

## Git / prod rules in force

- No `vercel --prod`
- No new Vercel project
- No mix of financial/warehouse/Dispatch into GroundView commits
- Production earth remains chrome HEAD only
- Do not push `wip/groundview` unless explicitly instructed

## Implementation defaults (P15)

- `GROUNDVIEW_MODE` unset (local Vite): `fixture`
- tests: `test`
- field: explicit `field` only; never inferred from empty store or `VERCEL`
- max raw body: `1048576` bytes
- max events per batch: `500`
- HMAC timestamp skew: `300` seconds
- secrets: `GROUNDVIEW_RECEIVER_SECRETS_FILE` JSON map; never in observations, manifests, logs, or this file
- mixed-batch contract: authentic request claims nonce once; valid events persist; schema/receiver-mismatch rows report `rejected` in the same durable transaction (not a partial ACK lie)

## Phase gates

| phase | status | commit | commands | evidence |
| --- | --- | --- | --- | --- |
| P0–P15 | PASS | wip/groundview from 6e67a6b | see prior rows | regression 36/9/20/5/89.29 |
| P16 | SOFTWARE_COMPLETE | local | receiver-node spool/uploader/drills | field FIELD_VALIDATION_REQUIRED |
| P17 | SOFTWARE_COMPLETE | local | `scripts/groundview-p17-experiment.mjs` | drill-not-empirical |
| P18 | SOFTWARE_COMPLETE | local | `scripts/groundview-p18-research.mjs` | v2_justified=false |
| P19 software | SOFTWARE_FOUNDATION_READY | local | foundations + finish-line | instruments + field kit |
| P19 empirical | FIELD_VALIDATION_REQUIRED | — | `groundview-p19-field.mjs --check` | missing SDR/antenna/site/clock; host+secrets ready |
| P20–P23 software | SOFTWARE_FOUNDATION_READY | local | `p20p21Field` / `p22p23Corridor` | empirical gated |
| P24 | SOFTWARE_FOUNDATION_READY | local | ops review; no migrate | bottleneck not measured |
| P25–P27 software | SOFTWARE_FOUNDATION_READY | local | `opsMaturity.mjs` | empirical gated |
| P28–P30 software | SOFTWARE_FOUNDATION_READY | local | bridge/surface/hardening | no unauthorized prod |
| §74/75 verify | PASS (software) | local | `groundview-verify-pack.mjs` | artifact under EARTH/verification |

## Finish-line evidence (this session)

- Restored lost `wip/groundview` working tree from agent transcript Writes (was wiped from disk)
- `node --test src/data/groundview/*.test.mjs` → **83/83 pass**
- `node scripts/groundview-replay.mjs` → **36/9/20/5/89.29**
- Phase 0 residuals: GV-C12 `anonymousRecurrence.mjs`, GV-C13 `fusionResearch.mjs`, `comparability.mjs`, Cesium journey/envelope/gap adapters default OFF, §74 verification artifact
- P19 readiness: missing `[sdr, antenna, site, clock]`; ready `[host, secrets]`; budget lock \$450; `field/BUY.md` + `groundview-field-day.sh`
- No fabricated field metrics; matcher-v1 untouched; no `vercel --prod`

## Tests last run

- GroundView **83/83**; replay **36/9/20/5/89.29**
- chrome `npm test` pre-existing non-GroundView fails remain out of scope

## Architectural decisions

- Preserve unrelated dirty work on `wip/mabeline-layers`; GroundView from `6e67a6b` (no reset).
- Cesium is a projection of `/api/groundview/*` state. Passes sit at receiver coverage. Journeys/envelopes/gaps require explicit enable and remain INFERRED.
- Competition: shares pass A OR pass B. 20-match gate retained. 89.29 pre-competition frozen.
- Fusion / recurrence research never feeds `groundview_match_v1`.
- P24 storage migration only if measured bottleneck.
- Empirical PASS requires physical evidence; soft-stop after scaffolding is not allowed for software, but fabricating field PASS is forbidden.

## How to enable locally

1. `cd SkyView && npm run dev` (`GROUNDVIEW_MODE` unset → fixture)
2. Open DATA LAYERS → The Mabeline Project → **GROUNDVIEW**
3. Chips: RECEIVERS, TRUCK PASSES, MATCHES, TRACKS (JOURNEYS/ENVELOPES/GAPS exist, default OFF)
4. Replay: `node scripts/groundview-replay.mjs`
5. Verify pack: `node scripts/groundview-verify-pack.mjs`
6. P19 readiness: `node scripts/groundview-p19-field.mjs --check`
7. Field mode: `GROUNDVIEW_MODE=field` (no synthetic seed)

## Next physical path (locked — do this next)

Durability note: **DONE** — GroundView is committed on `wip/groundview` @ `d317655` (clean tree). EARTH field/research pack on mabeline @ `43749a0`. Stay on `wip/groundview` for product work.

| Step | Action | Status |
| --- | --- | --- |
| 0 | Commit durability (avoid wipe on branch switch) | **DONE** |
| 1 | Buy/assemble kit — **\$450 lock**, cart in `field/BUY.md` (2× V4 + antennas) | **NEXT (operator)** |
| 2 | Secrets `~/.config/groundview/receiver-secrets.json` + `env.sh` | **DONE** |
| 2b | Host soft: `rtl_433` 25.12, chrony CLI, spool dirs, `groundview-field-day.sh` | **DONE** |
| 3 | Survey Site A; fill `field/sites/SITE_A_SURVEY.json` | pending (needs hardware + site) |
| 4 | Freeze install / clock_quality | pending |
| 5 | Capture: `bash scripts/groundview-field-day.sh all` | pending |
| 6 | Fill denominators from observation only (no fabrication) | pending |
| 7 | Analyze → STATUS P19 PASS or honest findings | pending |
| 8 | Then P20+ per `field/P20_P23_EXECUTION.md` | blocked on P19 |

Do not invent rates. Do not overwrite `groundview_match_v1`. Do not `vercel --prod`. Do not push unless instructed.

## Next safe resume action

**Operator: buy the \$450 cart in `field/BUY.md`.** Everything else agent-side for P19 prep is done. After boxes arrive: survey Site A → `bash scripts/groundview-field-day.sh all`.

## Rerun before continuing

`node --test src/data/groundview/*.test.mjs` && `node scripts/groundview-replay.mjs` && `node scripts/groundview-verify-pack.mjs`

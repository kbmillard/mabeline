# GroundView blueprint (P0–P18)

**One document for everything built through P18, plus pointer to P19+.**  
Snapshot date: 2026-09-15 (P19+ foundations added same day). Working branch: `SkyView` `wip/groundview` (local only).

This file merges product definition, architecture, phase history, contracts, file map, evidence, and next actions through P18. Live gate ledger: [`SkyView/GROUNDVIEW_STATUS.md`](../../../SkyView/GROUNDVIEW_STATUS.md). End-state / P19–P30 program: [`SkyView/GROUNDVIEW_END_STATE.md`](../../../SkyView/GROUNDVIEW_END_STATE.md). Mega prompt archive: [`GroundView-Mega-Prompt.md`](./GroundView-Mega-Prompt.md).

---

## 1. What GroundView is

| | |
| --- | --- |
| Parent | The Mabeline Project |
| Application | SkyView (not a second app / globe) |
| Surface | Local SkyView Cesium layer under DATA LAYERS → The Mabeline Project → **GROUNDVIEW** |
| Production | `skyprairie.io/earth` ships **without** GroundView |
| Core question | Can persistent RF (e.g. TPMS) from one passing tractor–trailer form a composite fingerprint so the same road unit is recognized at a downstream receiver? |
| Road unit v1 | Tractor + attached trailer traveling together (no tractor/trailer split required) |

Cesium is a **projection of API state**, not truth. Passes are drawn at **receiver coverage**, never as invented vehicle GPS. Confidence never uses the label `confirmed`.

---

## 2. Current status (authoritative snapshot)

| Claim | State |
| --- | --- |
| P0–P15 | **PASS** |
| P16–P18 | **SOFTWARE_COMPLETE** |
| P19–P30 / GV-C1–C14 software | **SOFTWARE_FOUNDATION_READY** (finish-line instruments landed) |
| P19 empirical | **FIELD_VALIDATION_REQUIRED** (SDR/site/host/secrets/clock missing) |
| Empirical / field P20–P27 | **FIELD_VALIDATION_REQUIRED** |
| P24 migration | **not activated** (`migrate_now=false`) |
| P30 prod deploy | **auth-gated** (`vercel_prod_allowed=false`) |
| Regression gate | Replay **36 packets / 9 passes / 20 matches / 5 tracks / 89.29** |
| Tests | `node --test src/data/groundview/*.test.mjs` → **83/83** |
| Matcher | `groundview_match_v1` frozen and preferred |
| Research matcher | `groundview_match_research_v0` (mechanics only; **v2_justified=false**) |
| Fusion research | `groundview_fusion_research_v0` (beside v1; never feeds matcher) |
| Verification pack | `EARTH/.../verification/mega-prompt-verification.md` (§74/75) |
| Active phases | P19 physical acquisition |
| Push / prod | Do **not** push `wip/groundview`; do **not** `vercel --prod` |

**Next safe action:** **P19 empirical** when hardware exists (real SDR + surveyed site + profile + clock-quality). Until then do not claim field-complete and do not overwrite v1.

For P19–P30 scientific path and GV-C1–C14 capability map, read [`GROUNDVIEW_END_STATE.md`](../../../SkyView/GROUNDVIEW_END_STATE.md).

---

## 3. Truth model and provenance

| Provenance | Meaning |
| --- | --- |
| **OBSERVED** | Received / measured (immutable raw RF observations) |
| **DERIVED** | Deterministic processing of observed (canonical identity, passes) |
| **INFERRED** | Probabilistic identity / continuity (matches, tracks) |
| **CONFIG** | Configured site / receiver pin (not OBSERVED vehicle GPS) |

Never silently promote DERIVED/INFERRED to OBSERVED.

Canonical identity under `groundview_canonical_v1`: `protocol:model:sensor_id` (rtl_433: `rtl433_protocol:model:sensor_id`). Authority for identity projections is **DERIVED**; raw protocol/model/sensor evidence stays on the OBSERVED observation.

---

## 4. End-to-end architecture

```text
rtl_433 JSON (live or recorded NDJSON)
        │
        ▼
receiver adapter  ──► append-only local spool  ──► signed bounded batch uploader
                      (source_event_id here)         (HMAC GV1, fresh nonce)
        │                                              │
        │                                              ▼
        │                         POST /api/groundview/node/events  (field surface)
        │                                              │
        │                                              ▼
        └──────────────►  normalize_event (single path)  ──► OBSERVED store
                                                                  │
                    ┌─────────────────────────────────────────────┤
                    ▼                                             ▼
            DERIVED: canonical + cluster + passes         INFERRED: match v1 + tracks
                    │                                             │
                    └──────────────► /api/groundview/snapshot ──► Cesium layer
```

**Modes (`GROUNDVIEW_MODE`):**

| Mode | When | Synthetic seed |
| --- | --- | --- |
| `fixture` | Default local Vite (unset) | Allowed (`synthetic_fixture`) |
| `test` | Automated tests | Allowed |
| `field` | Explicit only | **Forbidden** — rejects `synthetic_fixture` |

Never infer mode from empty store or `VERCEL`.

---

## 5. Phase history (everything built)

### P0 – P14 — software foundation (PASS)

| Phase | Built |
| --- | --- |
| P0 | Hygiene: `wip/groundview` from chrome `6e67a6b`; park `wip/mabeline-layers` |
| Foundation | `groundview_event_v1`, one `normalize_event`, store, deterministic IDs, clock provenance |
| P1 | Matcher + cluster; canonical **89.29** |
| P2 | GROUNDVIEW Cesium layer under The Mabeline Project |
| P3 | Tracks A→B→C, forks, weak edges; no permanent vehicle id |
| P4 | `/node/events` + `/node/heartbeat` |
| P5 | Decoder lab (`rf/lab.js`) |
| P6 | Experiments / run manifests |
| P7–P9 | Camera / OCR / bind (optional; RF works without camera) |
| P10 | Federation peer — same normalizer (no second pipeline) |
| P11 | Replay + `/playback?at=` |
| P12 | `/health` |
| P13 | Calibrate beside v1 (future matcher must not overwrite v1) |
| P14 | Product surface: default OFF; chips RECEIVERS / PASSES / MATCHES / TRACKS |

### P15 — durable field ingest readiness (PASS)

One trustworthy GroundView writer for irreplaceable physical observations. **Not** cloud infrastructure.

| Step | Built |
| --- | --- |
| P15.0 | Spec authority: `GROUNDVIEW_SPEC.md`; historical banner on P0–P14 doc |
| P15.1 | `event_schema_version`; explicit mode; DERIVED canonical projections; version coexistence |
| P15.2 | Competition = shares pass A **OR** pass B; **20-match** gate kept; 89.29 is **pre-competition** |
| P15.3 | Store fail-closed: mutex, ENOENT-only empty, temp+fsync+rename |
| P15.4 | Fixture / field / test isolation; field rejects synthetic seed |
| P15.5 | HMAC-SHA256 `GV1` on canonical paths; fresh nonce; timing-safe; skew |
| P15.6 | Bounded batch; accepted/duplicate/rejected; ACK only after durable commit; Vercel 503 |
| P15.7 | Exact run manifests; delete+replay reproducibility |
| P15.8 | Unknown protocol ≠ decoder_failure; receiver CONFIG; match/track INFERRED |
| P15.9 | `createGroundViewFieldHttp` — ingest without admin mutation routes |
| P15.10 | Full regression gate |

### P16 — single-receiver node software (SOFTWARE_COMPLETE)

Field-complete remains **FIELD_VALIDATION_REQUIRED**.

Built:

- Field-drill fixture (`GV-RX-FIELD-01/02`, not KC synthetic coords)
- Append-only spool (`groundview_receiver_spool_v1`); **`source_event_id` assigned at spool boundary**
- Signed uploader (fresh nonce per attempt; same ids on retry)
- Adapter + CLI
- Failure drills: restart, network loss, central down, skew, duplicate ACK

### P17 — two-site experiment software (SOFTWARE_COMPLETE)

Built: two-site drill link + experiment runner → JSON/CSV with score/ambiguity/provenance distributions.  
Every report banners: **pipeline validation only — not real RF performance.**

### P18 — matcher research runner software (SOFTWARE_COMPLETE)

Built: `groundview_match_research_v0` with **artificial** candidate config beside frozen v1.  
Authoritative outcome: **insufficient independently labelled physical evidence → no v2 justified → `groundview_match_v1` remains preferred.**

---

## 6. Locked clarifications (do not reopen)

1. **P16 `source_event_id`:** assigned at durable spool before retryable; stable across adapter/uploader restart, network retry, central duplicate ACK.
2. **P17 drill semantics:** drill coordinates / travel windows / links are test inputs only; reports are not RF evidence.
3. **P18 research boundary:** drill labels prove runner mechanics only; never promote a candidate from drill data.

Also locked from P15:

- **20-match gate** on the KC synthetic replay — do not relax.
- **89.29 is pre-competition** (`capped_score` / formula); post-competition may differ on other rows.
- Fresh **nonce per HTTP attempt**; `source_event_id` = event idempotency.

---

## 7. Matcher contract (`groundview_match_v1`)

Frozen. Do not edit weights/caps/competition in place for “v2”.

```
hard gates (travel window, direction, shared ≥ 1)
  → base = 100 * (0.50 * overlap_coefficient
                + 0.30 * shared_count_strength
                + 0.20 * jaccard)
  → shared_count_strength = min(shared_count / 6, 1)
  → caps by shared_count: 0→0, 1→19, 2→49, 3→69, 4→84, ≥5→100
  → competition among feasible candidates that share pass A OR pass B
  → clamp 0–100
```

Canonical fixture subset: set A `{A,B,C,D,E,F,G}` vs B `{A,B,D,E,F}` → **89.29**  
`100 * (0.5*1 + 0.3*(5/6) + 0.2*(5/7))`.

Labels: `weak` / `possible` / `strong` / `very_strong`. **Forbidden: `confirmed`.**  
`very_strong` is not ground truth.

Research path: [`SkyView/src/data/groundview/matchResearch.mjs`](../../../SkyView/src/data/groundview/matchResearch.mjs) — parameters only; does not mutate v1 history.

---

## 8. Auth, batch, and storage contracts

| Item | Value |
| --- | --- |
| Auth version | `groundview_receiver_auth_v1` |
| Canonical paths | `/api/groundview/node/events`, `/api/groundview/node/heartbeat` |
| Signature | HMAC-SHA256 `GV1` string; header `v1=<hex>` |
| Nonce | Fresh per HTTP attempt; claimed in same durable transaction as persist |
| Body limit | 1_048_576 bytes |
| Batch limit | 500 events |
| Timestamp skew | 300 seconds |
| Secrets | `GROUNDVIEW_RECEIVER_SECRETS_FILE` JSON map — never in observations/logs/STATUS |
| Central store | `.gev-cache/groundview/state.json` via `createGroundViewStore` |
| Vercel | Memory-only; node ingest **503** |
| Writer | Single writer process; fail-closed except ENOENT |

Mixed batch: authentic request claims nonce once; valid events persist; schema/receiver-mismatch rows report `rejected` in the same durable transaction (not a partial ACK lie).

---

## 9. Fixtures

### KC synthetic (P0–P15 regression — not a real radio network)

| id | lat | lon |
| --- | --- | --- |
| GV-RX-01 | 39.0997 | -94.5786 |
| GV-RX-02 | 39.1142 | -94.5410 |
| GV-RX-03 | 39.1300 | -94.5000 |

Links: 60–600 s eastbound travel windows.  
Replay: **36 / 9 / 20 / 5 / 89.29**.  
`source_type`: `synthetic_fixture`.

### Software field drill (P16–P18 — not surveyed)

| id | lat | lon | notes |
| --- | --- | --- | --- |
| GV-RX-FIELD-01 | 41.8781 | -87.6298 | `site_kind: software_drill` |
| GV-RX-FIELD-02 | 41.8910 | -87.6100 | `survey_status: FIELD_VALIDATION_REQUIRED` |

Link travel window is a **test input**. Uploaded events use `source_type: receiver_node` with `capture_ref: field_drill_recording`. Never serialize as `synthetic_fixture`.

---

## 10. HTTP API (`/api/groundview`)

Wired via Vite plugin `groundview-proxy` in `server/providers/local.js`.

**GET:** `/snapshot`, `/playback?at=`, `/receivers`, `/observations`, `/passes`, `/fingerprints`, `/matches`, `/tracks`, `/cameras`, `/camera-observations`, `/visual-identities`, `/bindings`, `/experiments`, `/health`

**POST:** `/replay`, `/receivers`, `/node/events`, `/node/heartbeat`, `/experiments/replay`, `/camera-observations`, `/visual-identities`, `/bindings`

**Field surface** (`createGroundViewFieldHttp`): only `POST /node/events`, `POST /node/heartbeat`, `GET /health`, `GET /snapshot`.

Share-link token: `k` (enabled-only). Presentation chips are local UI, not share-link options.

---

## 11. Complete file map

### Spec / ledger / research

| Path | Role |
| --- | --- |
| `SkyView/GROUNDVIEW_STATUS.md` | Live multi-session ledger |
| `SkyView/GROUNDVIEW_SPEC.md` | Authoritative P15–P18 execution spec |
| `EARTH/research/runs/2026-09-15-groundview/BLUEPRINT.md` | **This document** |
| `EARTH/research/runs/2026-09-15-groundview/GroundView-P15-P18.md` | Spec archive copy |
| `EARTH/research/runs/2026-09-15-groundview/GroundView.md` | Historical P0–P14 (not current execution) |
| `EARTH/research/runs/2026-09-15-groundview/HANDOFF.md` | Pre-P15 cloud handoff (superseded narratively) |
| `EARTH/research/runs/2026-09-15-groundview/completion.md` | P0–P14 completion note (superseded narratively) |

### Client / Cesium

| Path | Role |
| --- | --- |
| `SkyView/src/data/groundview.js` | Cesium CustomDataSource layer |
| `SkyView/src/data/groundview/constants.mjs` | Versions, weights, caps, modes |
| `SkyView/src/data/groundview/canonical.mjs` | Canonical identity |
| `SkyView/src/data/groundview/cluster.mjs` | Pass clustering |
| `SkyView/src/data/groundview/match.mjs` | **Frozen** matcher v1 |
| `SkyView/src/data/groundview/matchResearch.mjs` | Research runner (beside v1) |
| `SkyView/src/data/groundview/clock.mjs` | Clock provenance |
| `SkyView/src/data/groundview/presentation.mjs` | Presentation helpers |

### Server

| Path | Role |
| --- | --- |
| `SkyView/server/providers/groundview/engine.js` | Ingest, rebuild, replay |
| `SkyView/server/providers/groundview/store.js` | Durable JSON store |
| `SkyView/server/providers/groundview/http.js` | All + field HTTP factories |
| `SkyView/server/providers/groundview/normalize.js` | Adapters → envelope |
| `SkyView/server/providers/groundview/rf/normalizeEvent.js` | Single `normalize_event` |
| `SkyView/server/providers/groundview/receiverAuth.js` | HMAC GV1 |
| `SkyView/server/providers/groundview/receiver-node/adapter.js` | Receiver node |
| `SkyView/server/providers/groundview/receiver-node/spool.js` | Append-only spool |
| `SkyView/server/providers/groundview/receiver-node/uploader.js` | Signed batch uploader |
| `SkyView/server/providers/groundview/rf/lab.js` | Decoder lab |
| `SkyView/server/providers/groundview/federation/*` | Peer ingest |
| `SkyView/server/providers/groundview/camera/*` | Camera replay |
| `SkyView/server/providers/groundview/binding/*` | RF↔camera bind |
| `SkyView/server/providers/groundview/health.js` | Health helpers |
| `SkyView/server/providers/groundview/ids.js` | Deterministic IDs |

### Fixtures / scripts / tests

| Path | Role |
| --- | --- |
| `SkyView/fixtures/groundview/synthetic.mjs` | KC synthetic |
| `SkyView/fixtures/groundview/field-drill.mjs` | P16–P18 drill |
| `SkyView/scripts/groundview-replay.mjs` | Regression replay |
| `SkyView/scripts/groundview-receiver-node.mjs` | Spool ingest CLI |
| `SkyView/scripts/groundview-p17-experiment.mjs` | Two-site report |
| `SkyView/scripts/groundview-p18-research.mjs` | Matcher research |
| `SkyView/src/data/groundview/*.test.mjs` | Unit/integration gates (55) |

Chrome wiring (layer state, tracked readout, credits, local provider) lives in the same `wip/groundview` tree under `src/data/layerState.js`, `trackedReadout.js`, `dataCredits.js`, `server/providers/local.js`.

---

## 12. Authoritative versions

| Concern | Version |
| --- | --- |
| Event schema | `groundview_event_v1` |
| Storage | `groundview_store_v1` |
| Canonicalization | `groundview_canonical_v1` |
| Clustering | `groundview_cluster_v1` |
| Matcher | `groundview_match_v1` |
| Research matcher | `groundview_match_research_v0` |
| Tracks | `groundview_track_v1` |
| Receiver auth | `groundview_receiver_auth_v1` |
| Receiver spool | `groundview_receiver_spool_v1` |
| Binding | `groundview_bind_v1` (optional) |

---

## 13. Evidence

```bash
cd SkyView
node --test src/data/groundview/*.test.mjs   # 55/55
node scripts/groundview-replay.mjs           # 36/9/20/5 / 89.29
node scripts/groundview-p17-experiment.mjs   # drill report (non-empirical banner)
node scripts/groundview-p18-research.mjs     # v2_justified: false
```

P15.10 also verified layer/readout gates (59/59) and globe provenance: receivers CONFIG, passes DERIVED, matches/tracks INFERRED (`not_confirmed`).

---

## 14. Non-negotiables / explicitly out

- No second globe or second app  
- No `confirmed` label; no fake vehicle GPS  
- No FMCSA / Dispatch / warehouse / FPDS in the matcher  
- No PostgreSQL / K8s / microservices by preference  
- No production GroundView on Vercel / `skyprairie.io/earth`  
- No push of `wip/groundview` unless explicitly instructed  
- No overwrite of `groundview_match_v1`  
- No fabricating physical capture results  
- No promoting research candidates from drill labels  

Parked unrelated work: `wip/mabeline-layers` @ `2daf72b` (Dispatch, offices, divisions, Place-of-Performance).

---

## 15. How to run locally

```bash
cd SkyView
npm run dev
# DATA LAYERS → The Mabeline Project → GROUNDVIEW (starts OFF)
# Chips: RECEIVERS, TRUCK PASSES, MATCHES, TRACKS

node scripts/groundview-replay.mjs
node scripts/groundview-receiver-node.mjs
GROUNDVIEW_MODE=field   # empty until authenticated physical/drill events; no synthetic seed
```

---

## 16. Document authority map

| Need | Open |
| --- | --- |
| **Narrative blueprint of everything** | **This file** |
| Pass/fail ledger + next action | `SkyView/GROUNDVIEW_STATUS.md` |
| Full P15–P18 execution contracts | `SkyView/GROUNDVIEW_SPEC.md` |
| Historical P0–P14 wording | `EARTH/.../GroundView.md` (banner: not current execution) |

When STATUS and this blueprint disagree on a gate, **STATUS wins** for pass/fail; then update this blueprint.

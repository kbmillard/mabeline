# GroundView execution specification (P15–P18)

**Status:** current authoritative execution spec for GroundView after P0–P14.

**Authority:** A future session must be able to determine from repository state alone that P0–P14 are complete and P15 is the current implementation phase.

- Historical completed P0–P14 specification: `EARTH/research/runs/2026-09-15-groundview/GroundView.md` (do not treat as current execution instructions).
- This file is the current execution spec: `SkyView/GROUNDVIEW_SPEC.md`.
- Archive copy: `EARTH/research/runs/2026-09-15-groundview/GroundView-P15-P18.md`.
- Ledger: `SkyView/GROUNDVIEW_STATUS.md`.

P15 is **durable field ingest readiness** (one trustworthy GroundView writer for irreplaceable physical observations). It is not GroundView cloud infrastructure. Do not start P16 until P15.0–P15.10 pass. Do not expand architecture. Do not invent matcher v2. Do not `vercel --prod`. Do not push `wip/groundview` unless instructed.

## P15_EXECUTION_CLARIFICATIONS

```python
P15_EXECUTION_CLARIFICATIONS = {
    "spec_authority": {
        "required_before_code_changes": True,
        "actions": [
            "Preserve the existing P0-P14 GroundView specification as historical project documentation.",
            "Add the approved P15-P18 specification to the repository in a clearly authoritative committed path.",
            "Do not overwrite historical research material in a way that erases the P0-P14 record.",
            "Update GROUNDVIEW_STATUS.md to identify the exact current authoritative execution-spec path.",
            "Mark the older P0-P14 document as historical/completed rather than current execution instructions.",
        ],
        "rule": (
            "A future Cursor session must be able to determine from repository state alone "
            "that P0-P14 are complete and P15 is the current implementation phase."
        ),
    },
    "matcher_fixture_count": {
        "clarification": (
            "Correcting competition semantics should normally change competition metadata and "
            "post-competition scores, not candidate generation. Therefore the expected synthetic "
            "match-record count remains 20 unless inspection shows that downstream code filters "
            "candidate records based on post-competition score."
        ),
        "rule": (
            "Do not proactively relax the 20-match regression gate. "
            "If correcting competition semantics changes the record count, identify the exact "
            "code path responsible and determine whether that behavior is itself authoritative "
            "before changing the fixture expectation."
        ),
        "tracks_note": (
            "rebuildTracks filters confidence_score > 0. Track count may move while match count "
            "stays 20. Explain before changing either baseline."
        ),
        "precompetition_89_29": (
            "89.29 is the pre-competition capped/base score for the canonical 7-vs-5 subset. "
            "A post-competition confidence_score change on that row is competition metadata, "
            "not a formula regression."
        ),
    },
    "receiver_auth_retry_semantics": {
        "rules": [
            "Each HTTP upload attempt uses a fresh nonce, including retries of the same source events.",
            "source_event_id provides event-level idempotency across retries.",
            "nonce provides request-level replay protection and must not be reused for a retry.",
            "Authenticate the exact canonical GroundView route identity, not an unstable proxy-specific external prefix.",
            "Define the signed path once: /api/groundview/node/events and /api/groundview/node/heartbeat.",
            "Test it behind the actual repository middleware/proxy arrangement.",
        ],
        "atomicity": (
            "If nonce replay state is persisted in the same GroundView store, nonce claim and "
            "durable event acceptance must have transactionally coherent behavior. "
            "Do not create a state where the API returns durable acceptance before events are committed. "
            "A retry after transport ambiguity must use a new nonce and the same source_event_ids, "
            "allowing normal idempotency to report duplicates."
        ),
    },
    "implementation_defaults": {
        "GROUNDVIEW_MODE_unset_local": "fixture",
        "GROUNDVIEW_MODE_tests": "test",
        "GROUNDVIEW_MODE_field": "explicit field only",
        "max_raw_body_bytes": 1048576,
        "max_events_per_batch": 500,
        "hmac_timestamp_skew_seconds": 300,
        "canonical_hmac_paths": [
            "/api/groundview/node/events",
            "/api/groundview/node/heartbeat",
        ],
        "storage": "harden .gev-cache/groundview/state.json; single writer process; no PostgreSQL in P15",
    },
}
```

Source: Desktop `/Users/kyle/Desktop/GroundView.rtf` extracted 2026-09-15.

---

GROUNDVIEW_PROJECT = {
    # =========================================================================
    # PROJECT IDENTITY
    # =========================================================================

    "project": {
        "name": "GroundView",
        "parent": "The Mabeline Project",
        "application": "SkyView",
        "surface": "/EARTH",
        "repository": "SkyView",
        "working_branch": "wip/groundview",

        "purpose": (
            "GroundView uses persistent RF sensor emissions observed at fixed receiver sites "
            "to build composite physical fingerprints for passing commercial road units and "
            "to evaluate whether the same road unit can be recognized at downstream receivers."
        ),

        "road_unit_v1": (
            "tractor + attached trailer traveling together"
        ),

        "current_execution_stage": (
            "P0-P14 software foundations are complete on fixtures/replay. "
            "The next work is P15 Cloud / Field Readiness, followed by P16 single real receiver, "
            "P17 two-site downstream field experiment, and only then P18 field-calibrated matcher-v2 research."
        ),

        "execution_objective": (
            "Prepare the existing GroundView implementation for physical RF evidence using the "
            "smallest durable architecture that preserves GroundView's truth model, deterministic "
            "replay, versioning, frozen matcher-v1 behavior, and SkyView integration."
        ),
    },

    # =========================================================================
    # CURRENT PROJECT STATE
    # =========================================================================

    "current_state": {
        "software_phases_complete": [
            "P0",
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
            "P6",
            "P7",
            "P8",
            "P9",
            "P10",
            "P11",
            "P12",
            "P13",
            "P14",
        ],

        "fixture_replay_baseline": {
            "packets": 36,
            "passes": 9,
            "matches": 20,
            "tracks": 5,
            "canonical_precompetition_score": 89.29,
        },

        "known_runtime_state": [
            "GroundView default is OFF.",
            "Existing receiver pins are fixture placeholders, not physical SDR sites.",
            "GroundView share token is k.",
            "Cesium is a projection only.",
            "Passes render at receiver coverage/site position, not invented vehicle coordinates.",
            "GroundView production is not deployed on skyprairie.io/earth.",
            "GroundView working state is local/dev.",
            "POST /api/groundview/node/events is unavailable on Vercel.",
            "Current local persistence uses .gev-cache/groundview/state.json.",
            "When VERCEL is set, current GroundView storage is memory-only.",
        ],

        "field_validation_outstanding": [
            "real rtl_433 capture rate",
            "live receiver behavior",
            "real RF range",
            "real Class 8 TPMS protocol coverage",
            "real downstream fingerprint stability",
            "camera/OCR field accuracy",
            "real matcher precision",
            "real matcher recall",
            "real false-positive rate",
            "real false-negative rate",
            "optimal clustering behavior",
            "optimal receiver spacing",
            "real antenna configuration",
        ],

        "rule": (
            "Do not represent fixture success as field validation. "
            "P0-P14 should not be rebuilt merely because P15 begins. "
            "Repair an earlier phase only when P15 exposes an actual regression, contradiction, "
            "or missing invariant required for safe field evidence."
        ),
    },

    # =========================================================================
    # FROZEN CONTRACTS
    # =========================================================================

    "frozen_contracts": {
        "truth_model": [
            "OBSERVED",
            "DERIVED",
            "INFERRED",
        ],

        "truth_definitions": {
            "OBSERVED": (
                "Evidence directly received, measured, or captured from a physical/configured source. "
                "Observed evidence is immutable once durably accepted."
            ),

            "DERIVED": (
                "Deterministic computation from observed evidence and explicit versioned configuration."
            ),

            "INFERRED": (
                "Probabilistic identity, association, continuity, or semantic conclusion."
            ),
        },

        "road_unit_v1": (
            "tractor + attached trailer traveling together"
        ),

        "matcher_version": "groundview_match_v1",

        "matcher_formula": (
            "100.0 * ("
            "0.50 * overlap_coefficient + "
            "0.30 * shared_count_strength + "
            "0.20 * jaccard"
            ")"
        ),

        "shared_count_strength": (
            "min(shared_count / 6.0, 1.0)"
        ),

        "absolute_overlap_caps": {
            0: 0.0,
            1: 19.0,
            2: 49.0,
            3: 69.0,
            4: 84.0,
            "5+": 100.0,
        },

        "confidence_labels": {
            "weak": "0 <= score < 25",
            "possible": "25 <= score < 50",
            "strong": "50 <= score < 75",
            "very_strong": "75 <= score <= 100",
        },

        "canonical_fixture": {
            "A": ["A", "B", "C", "D", "E", "F", "G"],
            "B": ["A", "B", "D", "E", "F"],
            "expected_precompetition_score": 89.29,
        },

        "forbidden_confidence_label": "confirmed",

        "non_negotiable": [
            "Do not fabricate vehicle GPS.",
            "Do not present receiver proximity as exact vehicle position.",
            "Do not make FMCSA data a dependency of the RF matcher.",
            "Do not create a second SkyView application.",
            "Do not create a second globe.",
            "Do not run a GroundView production Vercel deployment.",
            "Do not silently mutate groundview_match_v1 after field testing.",
            "Do not silently convert INFERRED state into OBSERVED state.",
            "Do not silently rewrite immutable observed evidence when algorithms change.",
            "Do not use semantic carrier/company identity as RF matcher input.",
        ],
    },

    # =========================================================================
    # SPECIFICATION PRECEDENCE
    # =========================================================================

    "specification_precedence": {
        "priority_order": [
            "Frozen contracts in this prompt.",
            "Authoritative GroundView specification already committed in the repository.",
            "Existing domain truth/provenance/version contracts.",
            "Repository-native SkyView architecture and conventions.",
            "This prompt's implementation guidance.",
            "Suggested filenames and organization.",
        ],

        "repository_adaptable": [
            "exact filenames",
            "exact module placement",
            "internal helper names",
            "test helper organization",
            "serialization helper structure",
            "repository-native API mounting details",
            "repository-native logging integration",
            "repository-native Cesium lifecycle implementation details",
        ],

        "cursor_must_not_autonomously_change": [
            "groundview_match_v1 formula",
            "groundview_match_v1 weights",
            "shared_count_strength formula",
            "absolute overlap caps",
            "confidence thresholds",
            "truth-model semantics",
            "road_unit_v1 definition",
            "no-fake-GPS rule",
            "no-confirmed-label rule",
            "no-production-Vercel rule",
            "no-second-app rule",
            "raw observed evidence immutability",
            "the requirement that old algorithm versions remain reproducible",
        ],

        "contradiction_rule": (
            "If the actual repository and two authoritative requirements genuinely cannot both "
            "be satisfied, do not silently choose one. Record the contradiction in GROUNDVIEW_STATUS.md "
            "with exact repository evidence and stop only the affected implementation path."
        ),
    },

    # =========================================================================
    # REVIEWED IMPLEMENTATION CONFLICTS THAT P15 MUST RESOLVE
    # =========================================================================

    "reviewed_source_findings": {
        "persistence": {
            "current_behavior": (
                "The reviewed GroundView store loads state.json, mutates in-memory state, and rewrites "
                "the whole file. It has no proven transaction queue, lock, atomic temp-file replacement, "
                "or corruption-safe recovery boundary."
            ),

            "known_failure": (
                "Concurrent writes can lose accepted state. Read/parse errors currently risk being interpreted "
                "as empty state rather than failing closed."
            ),

            "required_action": (
                "Treat the current file adapter as fixture/dev persistence only until P15 hardening passes."
            ),
        },

        "matcher_v1": {
            "spec_behavior": (
                "For candidate A<->B, another feasible candidate is a competitor when it shares pass A "
                "OR shares pass B."
            ),

            "reviewed_code_behavior": (
                "The reviewed implementation groups competition approximately by pass_a_id + receiver_b_id."
            ),

            "reviewed_test_behavior": (
                "The reviewed tests assert the narrower implementation rather than the written v1 specification."
            ),

            "required_action": (
                "Correct the implementation and tests to the already-authoritative groundview_match_v1 "
                "competition semantics before collecting field matcher evidence. "
                "Do not call this correction matcher v2."
            ),
        },

        "canonical_identity": {
            "reviewed_behavior": (
                "canonical_sensor_identity is currently written into a normalized record whose provenance "
                "is OBSERVED, while the architecture defines canonical identity as DERIVED."
            ),

            "required_action": (
                "Make versioned DERIVED canonical identity projections authoritative while retaining "
                "legacy fixture compatibility without destructive mutation of raw observations."
            ),
        },

        "synthetic_seed": {
            "reviewed_behavior": (
                "The GroundView client may trigger synthetic replay when the store appears empty. "
                "Synthetic seeding currently risks looking like recorded rtl_433 evidence."
            ),

            "required_action": (
                "Make fixture/test/field mode explicit and prohibit synthetic seeding or synthetic evidence "
                "inside field-mode stores."
            ),
        },

        "receiver_auth": {
            "reviewed_behavior": (
                "The existing node event route does not provide sufficient receiver authentication, replay "
                "protection, receiver-state enforcement, or public-route isolation for internet exposure."
            ),

            "required_action": (
                "Do not expose receiver ingress publicly until P15 authentication and route gates pass."
            ),
        },

        "diagnostics": {
            "reviewed_behavior": (
                "Unknown protocol evidence can currently be conflated with decoder failure."
            ),

            "required_action": (
                "Unknown/uncanonicalizable RF must remain valid evidence and must be reported separately "
                "from actual decoder/process failure."
            ),
        },
    },

    # =========================================================================
    # GLOBAL ARCHITECTURE
    # =========================================================================

    "architecture": {
        "rf_path": [
            "physical or replay source",
            "source-event envelope",
            "single normalization path",
            "immutable OBSERVED RF observation",
            "versioned DERIVED canonical identity projection",
            "versioned DERIVED pass clustering",
            "DERIVED RF fingerprint",
            "INFERRED candidate match",
            "INFERRED temporary road-unit track",
            "optional camera/semantic binding",
            "query/report projection",
            "SkyView/Cesium projection",
        ],

        "source_convergence": (
            "Recorded rtl_433, live rtl_433, synthetic fixtures, custom decoder output, federation input, "
            "and physical receiver-node input must converge through the same versioned GroundView source-event "
            "envelope and the same normalization path. "
            "Do not create a Bendix path, manufacturer-specific central pipeline, direct database bypass, "
            "or second RF schema."
        ),

        "frontend_rule": (
            "SkyView/Cesium is a read/projection surface. "
            "Frontend entities are never authoritative evidence or authoritative inference state."
        ),

        "camera_rule": (
            "Camera evidence remains optional and independent. "
            "RF collection and RF road-unit matching must continue functioning when all camera features are disabled."
        ),

        "mabeline_rule": (
            "GroundView may later expose evidence-layer pass/match/track objects to Mabeline. "
            "GroundView RF continuity must never automatically become carrier/company/legal identity."
        ),
    },

    # =========================================================================
    # GROUNDVIEW FIELD MODES
    # =========================================================================

    "groundview_modes": {
        "environment_variable": "GROUNDVIEW_MODE",

        "allowed_modes": [
            "fixture",
            "field",
            "test",
        ],

        "fixture": {
            "synthetic_seed_allowed": True,
            "synthetic_source_type": "synthetic_fixture",

            "rules": [
                "Fixture receiver locations are explicitly non-field configuration.",
                "Synthetic data must never masquerade as recorded or live rtl_433 evidence.",
            ],
        },

        "field": {
            "synthetic_seed_allowed": False,

            "rules": [
                "Reject source_type='synthetic_fixture'.",
                "Frontend empty-state behavior must not trigger synthetic replay.",
                "Real receiver configuration is required.",
                "Receiver-node writes require authenticated registered receiver identity.",
                "A fixture-marked store must not be opened as a field store.",
                "An empty field store remains empty until physical evidence is accepted.",
            ],
        },

        "test": {
            "synthetic_seed_allowed": True,

            "rules": [
                "Ephemeral fixture behavior is permitted.",
                "Tests must never write into a real field store.",
            ],
        },

        "mode_rule": (
            "Never infer fixture or field mode merely from whether the store is empty or whether VERCEL exists."
        ),
    },

    # =========================================================================
    # EVENT CONTRACT
    # =========================================================================

    "source_event_contract": {
        "version": "groundview_event_v1",

        "required_fields": [
            "schema_version",
            "source_type",
            "receiver_id",
            "source_event_id",
            "receiver_timestamp",
            "payload",
        ],

        "optional_fields": [
            "site_id",
            "sequence_number",
            "frequency_hz",
            "decoder_name",
            "decoder_version",
            "signal_metadata",
            "capture_ref",
            "clock_metadata",
        ],

        "source_types": [
            "rtl433_live",
            "rtl433_recorded",
            "synthetic_fixture",
            "custom_decoder",
            "receiver_node",
            "federated_groundview",
        ],

        "identity_rules": [
            "source_event_id must be stable across retries.",
            "Re-ingesting the same source event must resolve idempotently.",
            "Two distinct RF transmissions must not collapse merely because payload content is equal.",
            "Physical receiver nodes assign durable source_event_id before network upload.",
            "Receiver-local source_event_id must survive process and network restart.",
        ],

        "normalization_rule": (
            "Every RF source type must use the same normalize_event / repository-native equivalent. "
            "Do not duplicate canonicalization or observation construction in adapters."
        ),
    },

    # =========================================================================
    # OBSERVED / DERIVED DATA CONTRACT
    # =========================================================================

    "rf_observation_contract": {
        "provenance": "OBSERVED",
        "immutable": True,

        "required_identity": [
            "observation_id",
            "receiver_id",
            "source_event_id",
            "event_schema_version",
            "observed_at",
            "ingested_at",
        ],

        "raw_evidence_fields": [
            "site_id optional",
            "frequency_hz optional",
            "rtl433_protocol optional",
            "model optional",
            "sensor_id optional",
            "pressure optional",
            "temperature optional",
            "battery optional",
            "flags optional",
            "rssi optional",
            "snr optional",
            "noise optional",
            "modulation optional",
            "raw_payload optional",
            "raw_json",
            "decoder_name optional",
            "decoder_version optional",
            "raw_iq_capture_ref optional",
            "pulse_capture_ref optional",
            "raw_bitstream_ref optional",
        ],

        "forbidden_as_observed_truth": [
            "canonical_sensor_identity",
            "truck identity",
            "carrier identity",
            "inferred vehicle coordinates",
            "corrected timestamp replacing original receiver timestamp",
        ],
    },

    "canonical_identity_projection": {
        "version": "groundview_canonical_v1",
        "provenance": "DERIVED",

        "fields": [
            "identity_projection_id",
            "observation_id",
            "canonical_sensor_identity optional",
            "canonicalization_version",
            "canonicalization_config_snapshot_id",
            "normalization_status",
        ],

        "initial_strategy": "rtl433_protocol:model:sensor_id",

        "rules": [
            "Raw sensor_id alone is never the canonical identity.",
            "Canonical identity is never directly observed evidence.",
            "Protocol/model/raw sensor fields remain immutable on the OBSERVED observation.",
            "A new canonicalization version creates a new projection.",
            "Multiple canonicalization versions may coexist.",
            "Do not rewrite old observations when canonicalization logic changes.",
            "Unknown or incomplete canonical identity remains retained evidence.",
        ],

        "legacy_compatibility": (
            "If existing fixture observations contain canonical_sensor_identity, treat it only as a legacy "
            "cache. Recompute groundview_canonical_v1 from raw observation evidence and verify compatibility. "
            "Do not use the legacy observation field as provenance authority."
        ),

        "consumer_rule": (
            "Pass clustering and fingerprinting consume the explicitly selected canonical projection/version."
        ),
    },

    # =========================================================================
    # MATCHER V1 — FROZEN AFTER P15 RECONCILIATION
    # =========================================================================

    "matcher": {
        "version": "groundview_match_v1",
        "machine_learning": False,

        "definitions": {
            "A": "canonical sensor set for upstream pass",
            "B": "canonical sensor set for downstream pass",
            "shared_count": "len(A & B)",
            "a_count": "len(A)",
            "b_count": "len(B)",
            "union_count": "len(A | B)",

            "jaccard": (
                "shared_count / union_count if union_count > 0 else 0.0"
            ),

            "overlap_coefficient": (
                "shared_count / min(a_count, b_count) "
                "if min(a_count, b_count) > 0 else 0.0"
            ),

            "containment_a": (
                "shared_count / a_count if a_count > 0 else 0.0"
            ),

            "containment_b": (
                "shared_count / b_count if b_count > 0 else 0.0"
            ),

            "shared_count_strength": (
                "min(shared_count / 6.0, 1.0)"
            ),
        },

        "hard_gates": {
            "receiver_pair_configured": {
                "required": True,
                "failure": "candidate not generated",
            },

            "travel_time": {
                "rule": (
                    "minimum_travel_seconds <= elapsed_seconds <= maximum_travel_seconds"
                ),
                "failure": "score = 0",
            },

            "direction": {
                "required_when_configured": True,
                "failure": "score = 0",
            },

            "shared_sensor": {
                "minimum": 1,
                "failure": "score = 0",
            },
        },

        "base_score": {
            "formula": (
                "100.0 * ("
                "0.50 * overlap_coefficient + "
                "0.30 * shared_count_strength + "
                "0.20 * jaccard"
                ")"
            ),

            "weights": {
                "overlap_coefficient": 0.50,
                "shared_count_strength": 0.30,
                "jaccard": 0.20,
            },
        },

        "absolute_overlap_caps": {
            0: 0.0,
            1: 19.0,
            2: 49.0,
            3: 69.0,
            4: 84.0,
            "5_or_more": 100.0,
        },

        "competition_factors": [
            {
                "condition": "no competitor",
                "factor": 1.00,
            },
            {
                "condition": "margin >= 25",
                "factor": 1.00,
            },
            {
                "condition": "15 <= margin < 25",
                "factor": 0.95,
            },
            {
                "condition": "8 <= margin < 15",
                "factor": 0.85,
            },
            {
                "condition": "3 <= margin < 8",
                "factor": 0.70,
            },
            {
                "condition": "margin < 3",
                "factor": 0.50,
            },
        ],

        "competition_semantics": {
            "competitor_definition": (
                "For candidate match A<->B, a competitor is another feasible candidate produced "
                "in the same deterministic matching evaluation that shares pass A OR shares pass B."
            ),

            "feasible_competitor": (
                "The competitor must already satisfy configured receiver-pair, travel-time, direction, "
                "and minimum-shared-sensor hard gates. A hard-gate failure cannot penalize another candidate."
            ),

            "comparison_score": (
                "Competition compares capped_score before competition_factor."
            ),

            "best_competing_score": (
                "Maximum capped_score among feasible competitors; absent when no competitor exists."
            ),

            "score_margin": (
                "capped_score - best_competing_score when a competitor exists."
            ),

            "tie_rule": (
                "Equal capped scores produce margin 0 and therefore the margin<3 competition factor. "
                "Stable deterministic match/pass IDs control persistence/output ordering. "
                "Insertion order must not be authoritative."
            ),
        },

        "algorithm": [
            "Apply hard gates.",
            "Calculate set statistics.",
            "Calculate base score.",
            "Apply absolute shared-count cap.",
            "Calculate capped scores for all feasible candidates.",
            "Determine competitor universe using shares-pass-A OR shares-pass-B.",
            "Calculate best competing capped score.",
            "Calculate score margin.",
            "Apply competition factor.",
            "Clamp final score to 0..100.",
            "Assign confidence label.",
        ],

        "confidence_labels": {
            "weak": "0 <= score < 25",
            "possible": "25 <= score < 50",
            "strong": "50 <= score < 75",
            "very_strong": "75 <= score <= 100",
        },

        "forbidden_label": "confirmed",

        "canonical_example": {
            "A": ["A", "B", "C", "D", "E", "F", "G"],
            "B": ["A", "B", "D", "E", "F"],

            "shared_count": 5,
            "overlap_coefficient": 1.0,
            "jaccard": 0.7142857143,
            "shared_count_strength": 0.8333333333,
            "expected_precompetition_score_approx": 89.29,
        },

        "p15_reconciliation_rule": (
            "The reviewed implementation currently uses a narrower competition grouping than this "
            "authoritative v1 definition. Correct that implementation and its tests before field evidence. "
            "This is a pre-field groundview_match_v1 defect correction, not matcher v2."
        ),

        "freeze_rule": (
            "After P15 reconciliation passes, groundview_match_v1 is frozen. "
            "Any later change to formula, weights, caps, thresholds, competition semantics, or other "
            "score-producing behavior becomes a new matcher version such as groundview_match_v2."
        ),
    },

    # =========================================================================
    # STORAGE CONTRACT
    # =========================================================================

    "storage_contract": {
        "categories": {
            "immutable_observed": [
                "RF observations",
                "camera observations",
            ],

            "versioned_rebuildable_derived": [
                "canonical identity projections",
                "truck passes",
                "RF fingerprints",
                "visual detections",
            ],

            "versioned_rebuildable_inferred": [
                "candidate matches",
                "road-unit tracks",
                "visual identity candidates",
                "multimodal bindings",
            ],

            "configuration": [
                "receivers",
                "receiver links",
                "camera sites",
                "experiment configs",
            ],
        },

        "p16_storage_decision": "harden_current_file_store",

        "file_adapter_rules": [
            "All persistent mutations must be serialized through one process-local transaction queue or mutex.",
            "Do not permit overlapping load-mutate-rewrite transactions.",
            "Persistent replacement must write a same-directory temporary file.",
            "Durably flush the temporary file before replacement when supported by the runtime.",
            "Atomically rename the completed temporary file over the active state file.",
            "Only ENOENT may initialize an empty GroundView store.",
            "JSON parse failure must fail closed.",
            "Permission failure must fail closed.",
            "Truncated state must fail closed.",
            "Unexpected filesystem errors must fail closed.",
            "A read error must never become emptyState followed by overwrite.",
            "A failed durable write must never generate a receiver durable ACK.",
            "The file-backed service supports exactly one active writer process.",
            "Do not horizontally scale the file-backed GroundView service.",
            "Batch event persistence where practical to reduce whole-state rewrite amplification.",
            "Do not expose mutable internal persistence state directly to consumers.",
            "Persist an explicit storage schema version.",
            "Persist the GroundView mode marker.",
        ],

        "acceptable_for_p16": (
            "A hardened single-process file adapter is acceptable for one bounded physical-receiver "
            "experiment because the receiver maintains its own durable spool and central ingest is idempotent."
        ),

        "postgres_not_required_before_p16": True,

        "postgres_migration_triggers": [
            "receiver spool persistently grows because central commit latency cannot keep up",
            "multiple central GroundView writer processes are required",
            "sustained multi-receiver concurrency exceeds the single-writer adapter",
            "retained field history makes whole-state replacement operationally impractical",
            "indexed time/version queries become demonstrably necessary",
            "service redundancy requires concurrent transactional writers",
        ],

        "migration_rule": (
            "Keep the engine behind a narrow GroundView persistence interface so PostgreSQL can later replace "
            "the file adapter without changing RF normalization, truth semantics, matcher behavior, or SkyView."
        ),
    },

    # =========================================================================
    # CLOCK AND TIME PROVENANCE
    # =========================================================================

    "clock_and_time_provenance": {
        "rules": [
            "Preserve receiver_timestamp exactly as received.",
            "Preserve central ingested_at independently.",
            "Never silently replace receiver time with corrected time.",
            "Any clock correction is DERIVED.",
            "Clock correction carries method/version and original source timestamp.",
            "Replay manifests state the time basis used for clustering and matching.",
            "Receiver clock-quality metadata is retained with field runs.",
        ],
    },

    # =========================================================================
    # REPLAY / RUN MANIFEST
    # =========================================================================

    "field_replay_manifest": {
        "required_before_p16": True,

        "fields": [
            "run_id",
            "source_event_set_reference",
            "event_schema_version",
            "groundview_mode",
            "receiver_config_snapshot_id",
            "receiver_link_config_snapshot_id optional",
            "canonicalization_version",
            "canonicalization_config_snapshot_id",
            "clustering_version",
            "clustering_config_snapshot_id",
            "matcher_version",
            "matcher_config_identity",
            "track_builder_version optional",
            "clock_time_basis",
            "experiment_config_snapshot_id optional",
            "created_at",
        ],

        "rules": [
            "Every meaningful replay/derivation run has one exact manifest.",
            "Results reference the manifest that produced them.",
            "Do not approximate reproducibility by referencing the current mutable configuration.",
            "Do not list every historical configuration snapshot as if each participated in one run.",
            "A new algorithm/config run does not overwrite an older run.",
            "Historical v1 and future v2 outputs must coexist.",
        ],
    },

    # =========================================================================
    # RECEIVER AUTHENTICATION
    # =========================================================================

    "receiver_authentication": {
        "version": "groundview_receiver_auth_v1",
        "algorithm": "HMAC-SHA256",

        "headers": [
            "X-GroundView-Receiver",
            "X-GroundView-Timestamp",
            "X-GroundView-Nonce",
            "X-GroundView-Signature",
        ],

        "canonical_request": (
            "'GV1\\n' + "
            "METHOD + '\\n' + "
            "PATH + '\\n' + "
            "RECEIVER_ID + '\\n' + "
            "TIMESTAMP + '\\n' + "
            "NONCE + '\\n' + "
            "SHA256_HEX(EXACT_RAW_REQUEST_BODY)"
        ),

        "signature_format": "v1=<lowercase hex HMAC-SHA256>",

        "timestamp": {
            "format": "Unix seconds",
            "initial_max_skew_seconds": 300,
            "configurable": True,
        },

        "nonce": {
            "requirement": (
                "Cryptographically random and unique for the receiver inside the accepted replay window."
            ),

            "rule": (
                "Nonce claiming must be atomic with respect to concurrent requests."
            ),
        },

        "validation_order": [
            "Apply raw request-body size limit.",
            "Resolve receiver identity from X-GroundView-Receiver.",
            "Require registered receiver.",
            "Require receiver enabled.",
            "Reject quarantined receiver.",
            "Validate timestamp syntax and clock-skew window.",
            "Reject already-used nonce.",
            "Compute SHA256 over exact raw body.",
            "Verify HMAC using timing-safe comparison.",
            "Parse JSON only after applicable raw-body/auth checks.",
            "Require each event receiver_id to equal X-GroundView-Receiver.",
            "Validate event schema.",
            "Atomically claim nonce.",
            "Perform idempotent durable ingest.",
        ],

        "protected_routes": [
            "POST /api/groundview/node/events",
            "POST /api/groundview/node/heartbeat",
        ],

        "secret_rules": [
            "Receiver secrets are machine credentials, not user accounts.",
            "Do not build a user-account system for P15.",
            "Do not persist receiver secrets inside RF observations.",
            "Do not place receiver secrets in replay manifests.",
            "Do not place receiver secrets in GROUNDVIEW_STATUS.md.",
            "Do not print receiver secrets in normal logs.",
        ],

        "batch_semantics": {
            "request_auth": "one valid signature authenticates the bounded batch request",

            "per_event_result": [
                "accepted",
                "duplicate",
                "rejected",
            ],

            "durability_rule": (
                "A receiver event is acknowledged as durably accepted only after the central persistence "
                "transaction containing it succeeds."
            ),

            "failure_rule": (
                "Persistence failure must not return a successful durable ACK. "
                "The receiver retains the event in its spool and retries."
            ),
        },
    },

    # =========================================================================
    # PUBLIC ROUTE BOUNDARY
    # =========================================================================

    "field_http_exposure": {
        "principle": (
            "Do not make the existing entire GroundView development middleware surface internet-public."
        ),

        "public_receiver_ingress": [
            "authenticated POST node/events",
            "authenticated POST node/heartbeat",
        ],

        "not_public_by_default": [
            "replay mutation",
            "receiver configuration mutation",
            "receiver-link mutation",
            "camera mutation",
            "visual identity mutation",
            "binding mutation",
            "experiment mutation",
            "administrative storage operations",
        ],

        "rule": (
            "Local development may retain repository-native developer routes. "
            "A field-facing long-lived service must explicitly mount only the intended receiver-ingress surface "
            "or separately protect administrative routes."
        ),
    },

    # =========================================================================
    # RECEIVER-SIDE NODE ARCHITECTURE
    # =========================================================================

    "receiver_node": {
        "architecture": [
            "rtl_433",
            "GroundView receiver adapter",
            "groundview_event_v1",
            "append-only durable local spool",
            "signed bounded batch uploader",
            "authenticated GroundView node/events",
            "durable central acknowledgement",
        ],

        "spool_rules": [
            "Persist an event locally before attempting network upload.",
            "Assign stable source_event_id before upload.",
            "Retain sequence/spool position across restart.",
            "Do not delete/commit a spool item before central durable acknowledgement.",
            "Retry network and server failures.",
            "Duplicate retry must remain idempotent centrally.",
            "Uploader restart must not lose unacknowledged events.",
            "Do not write directly from receiver node to the central database/store.",
            "Do not create manufacturer-specific central ingest paths.",
        ],
    },

    # =========================================================================
    # HEALTH / DIAGNOSTIC SEMANTICS
    # =========================================================================

    "field_diagnostics": {
        "rules": [
            "Unknown protocol evidence is not automatically a decoder failure.",
            "Incomplete canonical identity is not automatically a decoder failure.",
            "Decoder failure requires an explicit decoder/process/error condition.",
            "Expose unknown/uncanonicalizable observation counts separately.",
            "Expose decoder process/error counts separately.",
            "Expected FIELD_VALIDATION_REQUIRED protocol gaps are not software-health failures.",
        ],
    },

    # =========================================================================
    # MABELINE EVIDENCE BOUNDARY
    # =========================================================================

    "mabeline_boundary": {
        "exportable_groundview_objects": {
            "groundview_pass": {
                "provenance": "DERIVED",
                "required_references": [
                    "pass_id",
                    "receiver/site",
                    "run_manifest",
                    "algorithm versions",
                    "source evidence references",
                ],
            },

            "groundview_match": {
                "provenance": "INFERRED",
                "required_references": [
                    "match_id",
                    "pass_a_id",
                    "pass_b_id",
                    "score components",
                    "matcher_version",
                    "run_manifest",
                ],
            },

            "groundview_track": {
                "provenance": "INFERRED",
                "required_references": [
                    "episode-bounded track_id",
                    "constituent passes",
                    "constituent matches",
                    "track_builder_version",
                ],
            },
        },

        "semantic_join": {
            "concept": (
                "road_unit_episode -> candidate_semantic_identity"
            ),

            "provenance": "INFERRED",

            "rules": [
                "Semantic identity is a separate evidence edge.",
                "A GroundView RF match does not automatically become carrier/company identity.",
                "FMCSA/carrier data may enrich later semantic evidence but does not enter groundview_match_v1.",
                "Mabeline semantic enrichment must never mutate GroundView OBSERVED RF evidence.",
            ],
        },
    },

    # =========================================================================
    # GIT / DEPLOYMENT SAFETY
    # =========================================================================

    "git_and_deployment": {
        "branch": "wip/groundview",

        "rules": [
            "Keep GroundView work on wip/groundview unless explicitly instructed otherwise.",
            "Do not push the branch unless explicitly instructed.",
            "Do not run vercel --prod.",
            "Do not create another Vercel project.",
            "Do not deploy GroundView production functionality to skyprairie.io/earth during P15-P18.",
            "Keep Vercel receiver mutation unavailable.",
            "Do not discard unrelated dirty work.",
            "Do not mix unrelated Mabeline financial/warehouse/Dispatch work into GroundView commits.",
        ],

        "long_lived_service_rule": (
            "A long-lived GroundView Node evidence service may be introduced when field operation requires it. "
            "That service remains a GroundView backend for SkyView and is not a second application or second globe."
        ),

        "file_store_hosting_rule": (
            "When using the hardened file adapter, run exactly one GroundView writer service instance "
            "against one persistent volume. Do not horizontally scale it."
        ),
    },

    # =========================================================================
    # CURSOR EXECUTION STATE
    # =========================================================================

    "execution_state": {
        "status_file": "GROUNDVIEW_STATUS.md",
        "committed": True,

        "required_status_sections": [
            "current phase",
            "current P15 implementation step",
            "completed P15 implementation steps",
            "phase gate status",
            "software-complete items",
            "FIELD_VALIDATION_REQUIRED items",
            "blocked items",
            "known failures",
            "authoritative algorithm versions",
            "repository integration decisions",
            "tests last run",
            "test commit",
            "architectural decisions",
            "invalidated downstream gates",
            "next safe resume action",
        ],

        "update_when": [
            "before beginning P15",
            "before beginning each P15 implementation step",
            "after each P15 implementation step gate passes",
            "after a phase gate passes",
            "when an upstream abstraction changes",
            "when a phase becomes blocked",
            "when a field-validation item is discovered",
            "before ending a substantial Cursor session",
        ],

        "completion_rule": (
            "Never mark a phase or P15 implementation step complete because files exist or the happy path runs. "
            "A step is complete only when its explicit gate passes and the evidence is recorded."
        ),
    },

    # =========================================================================
    # FAILURE / ROLLBACK BEHAVIOR
    # =========================================================================

    "failure_recovery": {
        "principle": (
            "Repair the earliest responsible abstraction. "
            "Do not accumulate downstream workarounds around a known-invalid upstream contract."
        ),

        "procedure": [
            "Detect the failed assumption.",
            "Stop work that depends on the failed assumption.",
            "Record the failure and affected gates in GROUNDVIEW_STATUS.md.",
            "Identify the earliest responsible abstraction.",
            "Repair that abstraction.",
            "Invalidate dependent gates.",
            "Rerun responsible and dependent tests.",
            "Continue automatically when authoritative contracts remain satisfied.",
        ],

        "cursor_should_continue_automatically_when": [
            "The issue is an ordinary repository-native implementation decision.",
            "A test failure has a clear GroundView-local repair.",
            "A suggested filename differs from repository convention.",
            "A field-dependent constant can remain configurable and FIELD_VALIDATION_REQUIRED.",
        ],

        "cursor_should_stop_affected_work_when": [
            "Continuing would persist evidence under a known-invalid contract.",
            "A destructive Git action is required.",
            "A required external credential is unavailable.",
            "Two authoritative requirements genuinely contradict each other.",
        ],
    },

    # =========================================================================
    # P15 EXPLICIT IMPLEMENTATION SEQUENCE
    # =========================================================================

    "p15_implementation_sequence": {
        "principle": (
            "Execute P15 in the order below. "
            "This sequence is dependency-aware and is part of the execution specification. "
            "Do not skip forward merely because a later task is easier to implement. "
            "A later step may begin only after the required earlier step gates pass. "
            "When a later step exposes a defect in an earlier abstraction, return to and repair "
            "the earliest responsible step, invalidate dependent gates, rerun them, and continue."
        ),

        "sequence": [
            {
                "step": "P15.0",
                "name": "Repository reconnaissance and baseline capture",

                "goal": (
                    "Establish the actual current GroundView repository integration points and prove "
                    "the pre-P15 fixture baseline before changing architecture."
                ),

                "actions": [
                    "Inspect git branch, HEAD, worktree, and dirty files non-destructively.",
                    "Confirm wip/groundview or record the actual safe GroundView branch state.",
                    "Do not reset, discard, stash-overwrite, or force-checkout unrelated local work.",
                    "Locate the actual GroundView engine, store, HTTP/provider, normalization, event adapters, matcher, matcher tests, replay, health, Cesium, and synthetic seed paths.",
                    "Locate the authoritative GroundView specification and GROUNDVIEW_STATUS.md.",
                    "Record repository-native paths and test commands in GROUNDVIEW_STATUS.md.",
                    "Run the existing GroundView unit/integration/replay tests before modifications.",
                    "Run the practical affected SkyView baseline tests.",
                    "Run the synthetic GroundView replay and capture its exact baseline.",
                ],

                "gate": [
                    "Repository integration map is recorded.",
                    "Existing tests have been run and results recorded.",
                    "Synthetic replay produces 36 packets.",
                    "Synthetic replay produces 9 passes.",
                    "Synthetic replay produces 20 matches.",
                    "Synthetic replay produces 5 tracks.",
                    "Canonical precompetition fixture produces approximately 89.29.",
                    "No unrelated local work was destroyed or silently modified.",
                ],

                "failure_action": (
                    "If the repository does not match the reviewed source snapshot, adapt filenames/module placement "
                    "to the actual repository. Do not abandon P15 unless an authoritative contradiction exists."
                ),
            },

            {
                "step": "P15.1",
                "name": "Freeze event/truth/version boundaries before persistence changes",

                "depends_on": [
                    "P15.0",
                ],

                "goal": (
                    "Make the source-event, OBSERVED evidence, DERIVED canonicalization, versioning, and mode "
                    "contracts explicit before modifying the live ingest or persistence paths."
                ),

                "actions": [
                    "Confirm or implement groundview_event_v1 as the common source-event envelope.",
                    "Ensure live rtl_433, recorded rtl_433, synthetic fixtures, custom decoders, federation input, and receiver-node input adapt into the same normalization path.",
                    "Persist event_schema_version on normalized observations.",
                    "Ensure source_event_id remains stable across retries.",
                    "Ensure observation_id remains deterministic/idempotent for the same source event.",
                    "Define fixture/field/test mode as explicit state rather than empty-store inference.",
                    "Persist storage schema version and GroundView mode marker.",
                    "Define the versioned DERIVED canonical identity projection.",
                    "Stop treating canonical_sensor_identity on an OBSERVED record as authoritative provenance.",
                    "Preserve legacy fixture canonical_sensor_identity only as compatibility cache.",
                    "Make cluster/fingerprint consumers resolve canonical identity through the selected canonicalization projection/version.",
                    "Add or update serialization/provenance tests before changing field ingest behavior.",
                ],

                "gate": [
                    "All RF source adapters converge through one normalizer.",
                    "OBSERVED observation persists event_schema_version.",
                    "Same source event retry resolves idempotently.",
                    "Two distinct source events with equal payload content remain distinct observations.",
                    "Field/fixture/test mode is explicit.",
                    "canonical_sensor_identity authority is DERIVED rather than OBSERVED.",
                    "groundview_canonical_v1 rebuilds from immutable raw observation evidence.",
                    "A second test canonicalization version can coexist with v1 without mutating observations or v1 projection state.",
                    "Existing fixture replay still reproduces its baseline.",
                ],

                "failure_action": (
                    "Repair event/provenance/version contracts here before proceeding. "
                    "Do not compensate for a broken normalization/provenance model inside storage, auth, replay, or UI."
                ),
            },

            {
                "step": "P15.2",
                "name": "Reconcile and freeze groundview_match_v1",

                "depends_on": [
                    "P15.1",
                ],

                "goal": (
                    "Correct the reviewed pre-field competition-semantics defect so the matcher is genuinely "
                    "frozen before physical RF evidence begins."
                ),

                "actions": [
                    "Retain the authoritative matcher formula unchanged.",
                    "Retain the authoritative 0.50 / 0.30 / 0.20 weights unchanged.",
                    "Retain shared_count_strength=min(shared_count/6.0,1.0) unchanged.",
                    "Retain absolute overlap caps unchanged.",
                    "Retain confidence boundaries unchanged.",
                    "Retain forbidden confirmed label.",
                    "Change competitor discovery so a feasible candidate competes when it shares pass A OR shares pass B.",
                    "Exclude hard-gate-failed candidates from penalizing valid candidates.",
                    "Continue comparing capped_score before competition_factor.",
                    "Make stable deterministic IDs authoritative for tied persistence/output ordering.",
                    "Remove insertion order as semantic tie authority.",
                    "Replace reviewed tests that explicitly assert the narrower competition grouping.",
                    "Add same-A/different-B and same-B/different-A competition fixtures.",
                    "Add invalid-time and invalid-direction non-competitor fixtures.",
                    "Add candidate-input permutation tests.",
                    "Record the correction as a pre-field groundview_match_v1 implementation defect correction.",
                ],

                "gate": [
                    "Canonical precompetition fixture remains approximately 89.29.",
                    "One shared sensor cannot exceed 19.",
                    "Two shared sensors cannot exceed 49.",
                    "Three shared sensors cannot become very_strong.",
                    "Same-pass-A feasible candidate competes.",
                    "Same-pass-B feasible candidate competes.",
                    "Hard-gate-failed candidate cannot penalize another candidate.",
                    "Exact capped-score ties apply the defined competition factor.",
                    "Candidate input ordering does not change numeric matcher results.",
                    "Tied output ordering is stable from deterministic IDs.",
                    "Synthetic fixture still produces 20 match records unless another authoritative invariant legitimately requires a fixture update.",
                ],

                "failure_action": (
                    "Do not create matcher v2 to avoid fixing the pre-field v1 defect. "
                    "Repair the v1 implementation to match the authoritative specification."
                ),
            },

            {
                "step": "P15.3",
                "name": "Harden the persistence boundary",

                "depends_on": [
                    "P15.1",
                    "P15.2",
                ],

                "goal": (
                    "Make one-process file persistence safe enough for the first physical receiver without "
                    "introducing PostgreSQL prematurely."
                ),

                "actions": [
                    "Identify every GroundView mutation that currently reaches persistence.",
                    "Route all persistent mutations through one serialized transaction queue or mutex.",
                    "Prevent overlapping load-mutate-rewrite transactions.",
                    "Validate loaded state schema/version before accepting it.",
                    "Treat only ENOENT as permission to create an empty store.",
                    "Fail closed on malformed JSON.",
                    "Fail closed on truncated state.",
                    "Fail closed on permission/read errors.",
                    "Fail closed on unexpected filesystem errors.",
                    "Write replacement state to a same-directory temporary file.",
                    "Durably flush the temporary file when supported.",
                    "Atomically rename the completed temporary file over the active state file.",
                    "Keep the previous valid state intact when replacement fails before rename.",
                    "Do not acknowledge an event as durably accepted until persistence succeeds.",
                    "Do not expose mutable internal store state directly.",
                    "Keep the adapter explicitly single-writer-process.",
                    "Add batching support at the persistence boundary where appropriate.",
                ],

                "gate": [
                    "100 concurrent unique store mutations retain all 100 records.",
                    "Concurrent heartbeat and event mutation retain both changes.",
                    "Malformed existing state fails closed.",
                    "Truncated existing state fails closed.",
                    "Permission/read failure fails closed.",
                    "Failed replacement does not erase the previous valid state.",
                    "Successful replacement remains parseable after restart.",
                    "Failed durable write produces no durable ACK.",
                    "Single-writer limitation is explicit in configuration/documentation.",
                    "Fixture replay remains deterministic after persistence changes.",
                ],

                "failure_action": (
                    "Repair the storage adapter. Do not work around lost-update or corruption behavior "
                    "by adding retries in higher-level GroundView domain modules."
                ),
            },

            {
                "step": "P15.4",
                "name": "Implement fixture/field/test isolation",

                "depends_on": [
                    "P15.1",
                    "P15.3",
                ],

                "goal": (
                    "Guarantee that physical field evidence cannot silently mix with synthetic fixture evidence."
                ),

                "actions": [
                    "Implement explicit GROUNDVIEW_MODE values fixture, field, and test.",
                    "Make mode available to the server/provider and frontend through a repository-native capability/config response.",
                    "Allow synthetic seeding only when the server explicitly declares fixture/test seed permission.",
                    "Remove frontend empty-store state as authorization to seed.",
                    "Make synthetic seeding use source_type='synthetic_fixture'.",
                    "Reject synthetic_fixture input in field mode.",
                    "Reject opening a fixture-marked persistent store as a field store without an explicit migration/reset operation outside this phase.",
                    "Ensure fixture receiver coordinates remain identifiable as fixture configuration.",
                    "Ensure an empty field store remains empty until physical evidence is accepted.",
                ],

                "gate": [
                    "Fixture mode can seed the canonical fixture.",
                    "Test mode can use isolated synthetic fixtures.",
                    "Field mode cannot invoke synthetic seed through frontend behavior.",
                    "Field mode rejects synthetic_fixture events server-side.",
                    "Synthetic fixture observations never serialize as rtl433_recorded or rtl433_live.",
                    "Fixture-marked persistent state cannot silently open as field state.",
                    "GroundView default-OFF behavior remains unchanged.",
                ],

                "failure_action": (
                    "Treat any path capable of inserting synthetic evidence into field state as a P15 blocker."
                ),
            },

            {
                "step": "P15.5",
                "name": "Implement receiver machine authentication and replay protection",

                "depends_on": [
                    "P15.3",
                    "P15.4",
                ],

                "goal": (
                    "Make receiver ingress safe for eventual network exposure without introducing a user-account system."
                ),

                "actions": [
                    "Implement groundview_receiver_auth_v1 using HMAC-SHA256.",
                    "Require X-GroundView-Receiver.",
                    "Require X-GroundView-Timestamp.",
                    "Require X-GroundView-Nonce.",
                    "Require X-GroundView-Signature.",
                    "Hash the exact raw request body in the canonical request.",
                    "Use timing-safe signature comparison.",
                    "Enforce configured timestamp skew.",
                    "Implement per-receiver nonce replay tracking.",
                    "Make nonce claiming atomic.",
                    "Validate that header receiver identity exists.",
                    "Validate that receiver is enabled.",
                    "Reject quarantined receiver.",
                    "Require every event receiver_id in a batch to match the authenticated receiver.",
                    "Apply authentication to heartbeat as well as event upload.",
                    "Keep receiver secrets outside observations, manifests, logs, and status files.",
                    "Add repository-native secret-loading/configuration support without creating end-user accounts.",
                ],

                "gate": [
                    "Valid signed event request succeeds.",
                    "Valid signed heartbeat succeeds.",
                    "Invalid signature is rejected.",
                    "Malformed signature is rejected.",
                    "Unknown receiver is rejected.",
                    "Disabled receiver is rejected.",
                    "Quarantined receiver is rejected.",
                    "Stale timestamp is rejected.",
                    "Future timestamp beyond configured skew is rejected.",
                    "Repeated nonce is rejected.",
                    "Same nonce on a different receiver follows per-receiver replay semantics correctly.",
                    "Header/body receiver mismatch is rejected.",
                    "Secrets do not appear in persisted evidence or normal logs.",
                ],

                "failure_action": (
                    "Do not expose node ingress publicly until every authentication gate passes."
                ),
            },

            {
                "step": "P15.6",
                "name": "Implement bounded batch ingest and durable acknowledgement semantics",

                "depends_on": [
                    "P15.3",
                    "P15.5",
                ],

                "goal": (
                    "Create the central contract required by a durable receiver-side spool."
                ),

                "actions": [
                    "Add raw request-body size limit before unbounded JSON handling.",
                    "Add maximum event count per batch.",
                    "Validate all event envelopes against groundview_event_v1.",
                    "Authenticate the batch request once using its exact raw body.",
                    "Apply per-event receiver identity validation.",
                    "Return per-event accepted/duplicate/rejected status where repository conventions allow.",
                    "Preserve source_event_id idempotency.",
                    "Persist accepted events in a serialized durable transaction.",
                    "Do not return durable acceptance before the transaction commits.",
                    "On persistence failure return a retryable failure rather than accepted status.",
                    "Keep duplicate retries safe and deterministic.",
                ],

                "gate": [
                    "Bounded valid batch succeeds.",
                    "Duplicate batch retry creates no duplicate observations.",
                    "Mixed accepted/duplicate events report deterministic outcomes.",
                    "Oversized request body is rejected.",
                    "Oversized batch is rejected.",
                    "Schema-invalid event is rejected according to the chosen atomic/per-event validation contract.",
                    "Persistence failure generates no successful durable ACK.",
                    "Retry after simulated persistence/network failure eventually produces one observation per source_event_id.",
                ],

                "failure_action": (
                    "Repair central ingest semantics before implementing or depending on receiver-side spool deletion/ACK behavior."
                ),
            },

            {
                "step": "P15.7",
                "name": "Implement exact replay/run manifests and rebuild linkage",

                "depends_on": [
                    "P15.1",
                    "P15.2",
                    "P15.3",
                ],

                "goal": (
                    "Make every meaningful GroundView derivation reproducible from explicit evidence, configuration, "
                    "algorithm versions, and time basis before physical evidence enters the system."
                ),

                "actions": [
                    "Implement one exact run manifest per meaningful replay/derivation run.",
                    "Reference the source event/evidence set used by the run.",
                    "Reference exact receiver configuration snapshot.",
                    "Reference exact receiver-link configuration snapshot when applicable.",
                    "Reference canonicalization version and configuration snapshot.",
                    "Reference clustering version and configuration snapshot.",
                    "Reference matcher version and matcher configuration identity.",
                    "Reference track-builder version when tracks are produced.",
                    "Reference experiment configuration when applicable.",
                    "Record raw versus corrected clock/time basis.",
                    "Make produced derived/inferred records traceable to their run manifest.",
                    "Do not overwrite older manifests/results when the same evidence is rebuilt with a new version.",
                ],

                "gate": [
                    "A replay result resolves one exact manifest.",
                    "Manifest resolves the exact receiver configuration used.",
                    "Manifest resolves the exact canonicalization version used.",
                    "Manifest resolves the exact clustering version/config used.",
                    "Manifest resolves groundview_match_v1 when matches are produced.",
                    "Deleting rebuildable derived/inferred state and rerunning with the same manifest inputs reproduces semantically equivalent output.",
                    "Running a second algorithm/config version does not mutate or overwrite the first run.",
                ],

                "failure_action": (
                    "Do not accept physical field evidence into a system whose derived results cannot identify "
                    "the exact algorithm/configuration context that created them."
                ),
            },

            {
                "step": "P15.8",
                "name": "Correct field diagnostics and provenance presentation",

                "depends_on": [
                    "P15.1",
                    "P15.7",
                ],

                "goal": (
                    "Ensure field health and SkyView presentation distinguish configuration, observed evidence, "
                    "derived state, inference, unknown protocols, and actual software failure."
                ),

                "actions": [
                    "Separate unknown protocol count from decoder process/error count.",
                    "Separate incomplete canonical identity from decoder failure.",
                    "Only set decoder_failure for an explicit decoder/process failure condition.",
                    "Keep unknown protocol observations queryable and replayable.",
                    "Change receiver pin/site provenance presentation to CONFIG or repository-native configured-site terminology.",
                    "Keep pass provenance DERIVED.",
                    "Keep match/track provenance INFERRED.",
                    "Verify no frontend selector fabricates vehicle coordinates.",
                    "Verify no health/report path promotes unknown RF into software failure.",
                ],

                "gate": [
                    "Unknown protocol fixture increments unknown evidence diagnostics.",
                    "Unknown protocol fixture alone does not set decoder_failure.",
                    "Explicit decoder failure does set decoder_failure.",
                    "Receiver pin is not presented as an OBSERVED vehicle coordinate.",
                    "Pass selection remains a receiver-site/coverage event.",
                    "Match and track remain visibly INFERRED.",
                    "No confirmed label appears.",
                    "No fake/interpolated vehicle GPS appears.",
                ],

                "failure_action": (
                    "Repair provenance/diagnostic classification at the producing layer rather than hiding the issue in UI text."
                ),
            },

            {
                "step": "P15.9",
                "name": "Isolate the field-facing HTTP surface",

                "depends_on": [
                    "P15.5",
                    "P15.6",
                ],

                "goal": (
                    "Prevent eventual internet exposure of the entire GroundView developer mutation surface."
                ),

                "actions": [
                    "Identify every currently mounted GroundView HTTP route.",
                    "Classify routes as public receiver ingress, local/admin mutation, or read/query.",
                    "Ensure a future field-facing service can mount authenticated node/events and node/heartbeat without automatically exposing replay/config/camera/binding/experiment mutation.",
                    "Use repository-native middleware/routing separation rather than creating a second application.",
                    "Keep Vercel node mutation unavailable.",
                    "Do not create a public anonymous receiver write path.",
                ],

                "gate": [
                    "Field-facing route configuration exposes only the intended receiver ingress or separately protected routes.",
                    "Replay mutation is not anonymously public.",
                    "Receiver configuration mutation is not anonymously public.",
                    "Camera/binding/experiment mutation is not anonymously public.",
                    "Node event and heartbeat routes require receiver authentication.",
                    "Vercel mutation behavior remains unavailable/stubbed.",
                ],

                "failure_action": (
                    "Do not deploy or expose the long-lived receiver service until route isolation passes."
                ),
            },

            {
                "step": "P15.10",
                "name": "Full P15 regression and field-readiness gate",

                "depends_on": [
                    "P15.0",
                    "P15.1",
                    "P15.2",
                    "P15.3",
                    "P15.4",
                    "P15.5",
                    "P15.6",
                    "P15.7",
                    "P15.8",
                    "P15.9",
                ],

                "goal": (
                    "Prove that P15 hardening did not break the completed P0-P14 software path and that "
                    "one physical receiver may now safely be introduced."
                ),

                "actions": [
                    "Run the complete GroundView unit/integration/regression suite.",
                    "Run the canonical synthetic replay from clean rebuildable state.",
                    "Run matcher-v1 regression fixtures.",
                    "Run persistence concurrency/corruption/recovery tests.",
                    "Run receiver-auth tests.",
                    "Run batch ingest/idempotency/durable-ACK tests.",
                    "Run mode-isolation tests.",
                    "Run canonical-projection coexistence tests.",
                    "Run replay-manifest determinism tests.",
                    "Run health/provenance tests.",
                    "Run affected SkyView/GroundView-off regression tests.",
                    "Confirm no GroundView production deployment occurred.",
                    "Update GROUNDVIEW_STATUS.md with exact evidence.",
                ],

                "gate": [
                    "All P15 step gates pass.",
                    "Synthetic baseline remains 36 packets.",
                    "Synthetic baseline remains 9 passes.",
                    "Synthetic baseline remains 20 matches.",
                    "Synthetic baseline remains 5 tracks.",
                    "Canonical precompetition score remains approximately 89.29.",
                    "groundview_match_v1 matches its authoritative specification.",
                    "OBSERVED canonical provenance violation is removed as authority.",
                    "Concurrent writes no longer lose accepted state.",
                    "Corruption/read errors fail closed.",
                    "Synthetic evidence cannot enter field mode.",
                    "Receiver HMAC and replay protection pass.",
                    "Batch retries are idempotent.",
                    "Durable ACK follows durable commit.",
                    "Exact run manifests are produced.",
                    "Unknown RF and decoder failure are distinct.",
                    "GroundView OFF preserves existing SkyView behavior.",
                    "Vercel receiver mutation remains unavailable.",
                ],

                "failure_action": (
                    "P15 remains IN_PROGRESS. Identify the earliest failed P15 step, repair it, invalidate "
                    "and rerun every dependent step gate. Do not declare field readiness partially complete."
                ),

                "completion_effect": (
                    "After this gate passes, groundview_match_v1 is frozen for field work and P16 may begin "
                    "only if physical receiver hardware/site prerequisites exist."
                ),
            },
        ],

        "ordering_constraints": [
            "Do not harden receiver authentication before the receiver/event identity contract is confirmed.",
            "Do not implement durable ACK semantics before persistence durability semantics are correct.",
            "Do not allow physical field data before synthetic/field isolation passes.",
            "Do not freeze matcher v1 before the reviewed competition-semantics discrepancy is resolved.",
            "Do not make canonical identity projections depend on mutable OBSERVED fields.",
            "Do not build a receiver-side spool against an ambiguous central ACK contract.",
            "Do not expose a long-lived field service before route isolation and HMAC gates pass.",
            "Do not start P16 while any P15.0-P15.10 gate remains failed or unverified.",
        ],

        "parallelism": {
            "allowed": [
                (
                    "After P15.1 passes, matcher reconciliation and initial storage implementation may be worked "
                    "in parallel only if they touch independent modules and their integration tests remain gated."
                ),
                (
                    "Diagnostic/UI provenance cleanup may be prepared while persistence/auth work proceeds, "
                    "but P15.8 cannot pass until the canonical identity and run-manifest contracts are stable."
                ),
            ],

            "not_allowed": [
                "Treating parallel implementation as permission to bypass dependency gates.",
                "Starting field-node deployment while P15 auth/storage/mode isolation remains incomplete.",
            ],
        },
    },

    # =========================================================================
    # PHASE 15 — CLOUD / FIELD READINESS
    # =========================================================================

    "phase_15_cloud_field_readiness": {
        "goal": (
            "Harden the completed fixture/replay architecture so the first physical receiver cannot "
            "silently lose, corrupt, contaminate, spoof, mis-version, or misclassify GroundView evidence."
        ),

        "execution_sequence": (
            "Execute p15_implementation_sequence P15.0 through P15.10. "
            "Those steps and gates are mandatory execution ordering for this phase."
        ),

        "prerequisites": [
            "Inspect actual repository state before changing files.",
            "Confirm current GroundView test commands.",
            "Confirm current fixture/replay baseline.",
            "Confirm GroundView is not being production deployed.",
        ],

        "repository_reconnaissance": [
            "Locate actual GroundView engine/store/http/provider modules.",
            "Locate current matcher and matcher tests.",
            "Locate normalize_event and source-event adapters.",
            "Locate replay and synthetic seeding paths.",
            "Locate node/events and heartbeat routes.",
            "Locate health/diagnostic implementation.",
            "Locate Cesium GroundView receiver/pass/match rendering.",
            "Locate current GroundView status/spec files.",
            "Record repository-native paths in GROUNDVIEW_STATUS.md.",
        ],

        "build": [
            "Correct groundview_match_v1 competition implementation to the authoritative shares-pass-A OR shares-pass-B definition.",
            "Replace matcher tests that currently lock in the narrower competition grouping.",
            "Make final tied candidate ordering depend on stable deterministic IDs rather than insertion order.",
            "Preserve all frozen groundview_match_v1 formula/weight/cap/confidence behavior.",
            "Serialize file-store mutations through one transaction queue/mutex.",
            "Implement fail-closed validated store loading.",
            "Implement same-directory temporary state writes and atomic replacement.",
            "Prevent parse/read errors from becoming empty-store overwrite.",
            "Add storage schema version.",
            "Add GroundView store mode marker.",
            "Implement bounded node event batches.",
            "Preserve existing source-event idempotency.",
            "Return durable ACK only after persistence succeeds.",
            "Implement groundview_receiver_auth_v1.",
            "Authenticate node heartbeat using the same receiver identity boundary.",
            "Enforce registered receiver identity.",
            "Enforce enabled/disabled receiver state.",
            "Enforce receiver quarantine state.",
            "Add raw request size limit.",
            "Add batch-size/event-count limit.",
            "Add nonce replay protection.",
            "Add explicit fixture/field/test mode separation.",
            "Change synthetic seeding to source_type='synthetic_fixture'.",
            "Disable all synthetic auto-seeding in field mode.",
            "Make the frontend seed only when the server explicitly advertises fixture/test seeding permission.",
            "Implement exact replay/run manifest linkage.",
            "Persist event_schema_version on RF observations.",
            "Implement versioned DERIVED canonical identity projections.",
            "Make clustering/fingerprinting consume selected canonical identity projection/version.",
            "Retain legacy fixture canonical_sensor_identity only as compatibility cache.",
            "Separate unknown protocol/incomplete canonicalization from decoder-process failure.",
            "Correct receiver-site UI provenance from OBSERVED to configured receiver site.",
            "Keep pass provenance DERIVED.",
            "Keep match/track provenance INFERRED.",
            "Keep Vercel node mutation unavailable.",
            "Provide field-facing route isolation so a public service does not expose all development mutation routes.",
        ],

        "do_not_build": [
            "PostgreSQL merely because field work is beginning.",
            "Kubernetes.",
            "Microservice decomposition.",
            "A second SkyView application.",
            "A second globe.",
            "User-account authentication for receiver nodes.",
            "Production Vercel GroundView ingest.",
            "groundview_match_v2.",
            "FMCSA matcher integration.",
            "Manufacturer-specific central ingest pipelines.",
        ],

        "tests": [
            "All existing GroundView fixture/replay tests.",
            "Canonical matcher precompetition score remains approximately 89.29.",
            "shares-pass-A competitor test.",
            "shares-pass-B competitor test.",
            "invalid travel-time candidate cannot penalize a valid candidate.",
            "invalid direction candidate cannot penalize a valid candidate.",
            "candidate input reordering does not alter numeric matcher outputs.",
            "candidate tied output order is deterministic from stable IDs.",
            "100 concurrent unique store mutations retain all 100 records.",
            "concurrent heartbeat + event mutation does not lose either update.",
            "malformed existing state fails closed.",
            "permission/read failure fails closed.",
            "failed write leaves previous valid state readable.",
            "failed durable write produces no durable receiver ACK.",
            "duplicate batch retry remains idempotent.",
            "valid receiver HMAC accepted.",
            "invalid HMAC rejected.",
            "stale timestamp rejected.",
            "replayed nonce rejected.",
            "receiver header/body mismatch rejected.",
            "unknown receiver rejected.",
            "disabled receiver rejected.",
            "quarantined receiver rejected.",
            "oversized body rejected.",
            "oversized batch rejected.",
            "heartbeat requires receiver authentication.",
            "field mode cannot auto-seed.",
            "field mode rejects synthetic_fixture events.",
            "fixture seed carries synthetic_fixture provenance.",
            "fixture-marked store cannot silently become field store.",
            "canonical v1 projection rebuilds from raw OBSERVED evidence.",
            "a second test canonicalization version coexists without mutating v1 or the observation.",
            "run manifest references exact config/version inputs.",
            "unknown protocol increments unknown evidence diagnostics without setting decoder_failure.",
            "explicit decoder failure still sets decoder failure health.",
            "GroundView disabled leaves existing SkyView behavior unchanged.",
            "Vercel node mutation still returns hosted-unavailable behavior.",
        ],

        "exit_gate": [
            "P15.0 through P15.10 gates pass.",
            "Synthetic baseline remains 36 packets.",
            "Synthetic baseline remains 9 passes.",
            "Synthetic baseline remains 20 matches.",
            "Synthetic baseline remains 5 tracks.",
            "Canonical precompetition score remains 89.29.",
            "Authoritative matcher-v1 competition semantics pass.",
            "Matcher results are deterministic independent of candidate generation order.",
            "Concurrent file-store mutation test passes.",
            "Corrupt-state fail-closed test passes.",
            "Atomic-write recovery test passes.",
            "Receiver batch idempotency passes.",
            "Receiver HMAC suite passes.",
            "Nonce replay protection passes.",
            "Receiver state/quarantine checks pass.",
            "Body and batch limits pass.",
            "Field mode cannot receive synthetic fixture evidence.",
            "OBSERVED records no longer treat canonical identity as observed truth.",
            "Canonical versions can coexist.",
            "Replay manifest resolves exact evidence/config/version inputs.",
            "Unknown protocol and decoder failure diagnostics are distinct.",
            "No receiver mutation is enabled on Vercel.",
            "Existing affected SkyView tests remain green.",
        ],

        "done_when": (
            "GroundView is safe to receive physical evidence from one authenticated receiver without "
            "changing its frozen truth model, silently losing data, mixing fixture evidence with field evidence, "
            "or requiring production deployment."
        ),
    },

    # =========================================================================
    # PHASE 16 — SINGLE REAL RECEIVER
    # =========================================================================

    "phase_16_single_real_receiver": {
        "goal": (
            "Determine what useful RF one real freight observation site hears. "
            "Do not test downstream road-unit recognition yet."
        ),

        "prerequisites": [
            "Phase 15 exit gate passes.",
            "A physical SDR/receiver node is available.",
            "A real observation site is selected.",
            "Receiver/site coordinates are surveyed or otherwise defensibly measured.",
            "Real receiver metadata is recorded.",
        ],

        "architecture": [
            "real SDR",
            "rtl_433 JSON",
            "GroundView receiver adapter",
            "groundview_event_v1",
            "append-only durable local spool",
            "signed bounded batch uploader",
            "P15-hardened central GroundView ingest",
            "immutable OBSERVED RF observations",
            "groundview_canonical_v1 projections",
            "existing clustering/fingerprint/replay/reporting",
        ],

        "receiver_configuration": [
            "unique receiver_id",
            "real site_id",
            "surveyed latitude",
            "surveyed longitude",
            "altitude when available",
            "road name/direction when known",
            "enabled frequencies",
            "antenna metadata",
            "SDR hardware metadata",
            "receiver software version",
            "rtl_433 version",
            "clock metadata",
        ],

        "receiver_rules": [
            "Assign stable source_event_id before network upload.",
            "Persist event to local spool before upload.",
            "Do not remove spool evidence before durable central ACK.",
            "Preserve receiver/source timestamp.",
            "Preserve frequency.",
            "Preserve decoder/protocol/model/raw sensor fields.",
            "Preserve signal metadata when available.",
            "Preserve unknown/uncanonicalizable RF.",
            "Do not use synthetic Kansas City fixture coordinates.",
            "Do not write directly to central storage/database.",
            "Do not create protocol-specific central APIs.",
            "Do not claim that a single receiver recognized a road unit downstream.",
        ],

        "failure_drills": [
            "restart receiver adapter while events are queued",
            "restart uploader while events are queued",
            "temporary network loss",
            "central service unavailable",
            "duplicate batch retry",
            "central persistence failure",
            "clock-skew rejection",
        ],

        "measure": [
            "total rtl_433 records",
            "accepted GroundView events",
            "duplicate events",
            "rejected events by reason",
            "receiver spool depth",
            "maximum spool age",
            "upload retry counts",
            "protocol distribution",
            "model distribution",
            "frequency distribution",
            "unknown/uncanonicalizable observation count",
            "RSSI distribution when available",
            "SNR distribution when available",
            "clock-quality measurements",
            "canonical sensor identities under groundview_canonical_v1",
            "pass counts under current clustering configuration",
            "sensor counts per derived pass",
            "RF dwell duration when measurable",
        ],

        "software_operational_gate": [
            "One defined real capture session completes.",
            "Spool survives process restart.",
            "Network interruption causes queued evidence rather than loss.",
            "Backlog drains after reconnect.",
            "Duplicate retries do not duplicate observations.",
            "Spool acknowledgements reconcile with durably accepted central events.",
            "Field store contains zero synthetic_fixture observations.",
            "Raw receiver timestamps survive normalization unchanged.",
            "Frequency and decoder provenance survive normalization unchanged.",
            "Unknown evidence remains queryable.",
            "Derived state can be deleted and deterministically rebuilt from OBSERVED evidence.",
            "The run manifest identifies exact versions/config snapshots.",
        ],

        "field_validation_required": [
            "Class 8 TPMS penetration",
            "real sensors heard per road unit",
            "real transmission cadence",
            "real RF range",
            "real protocol coverage",
            "real antenna effectiveness",
            "whether current clustering default is optimal",
        ],

        "done_when": (
            "GroundView can truthfully report what one physical freight observation site heard, "
            "can survive ordinary network/process interruption without evidence loss, and can replay the "
            "physical OBSERVED evidence deterministically without making downstream identity claims."
        ),
    },

    # =========================================================================
    # PHASE 17 — TWO-SITE DOWNSTREAM FIELD EXPERIMENT
    # =========================================================================

    "phase_17_two_site_downstream_experiment": {
        "goal": (
            "Run the first real receiver-A to receiver-B experiment measuring downstream RF fingerprint "
            "continuity using frozen groundview_match_v1."
        ),

        "prerequisites": [
            "Phase 15 passes.",
            "Phase 16 passes.",
            "Receiver A is stable.",
            "Receiver B is stable.",
            "Both sites have real receiver identities.",
            "Both sites have surveyed coordinates.",
            "Both sites have recorded hardware/software/antenna metadata.",
            "Both sites have usable clock-quality metadata.",
            "The receiver-to-receiver corridor is physically understood.",
            "Direction constraints are defensible.",
            "Minimum and maximum travel windows are derived from the real corridor.",
        ],

        "receiver_link_rules": [
            "Do not reuse synthetic Kansas City coordinates.",
            "Do not reuse fixture travel windows merely because they already exist.",
            "Record the basis for minimum_travel_seconds.",
            "Record the basis for maximum_travel_seconds.",
            "Record road direction.",
            "Snapshot the receiver-link configuration in the run manifest.",
        ],

        "pipeline": [
            "real receiver A events",
            "groundview_event_v1",
            "OBSERVED A evidence",
            "groundview_canonical_v1",
            "groundview_cluster_v1/current frozen clustering version",
            "A fingerprints",
            "real receiver B events",
            "groundview_event_v1",
            "OBSERVED B evidence",
            "groundview_canonical_v1",
            "groundview_cluster_v1/current frozen clustering version",
            "B fingerprints",
            "groundview_match_v1",
            "candidate downstream matches",
            "optional temporary road-unit tracks where topology permits",
            "field report",
        ],

        "rules": [
            "Use the same normalization pipeline at both receivers.",
            "Do not modify groundview_match_v1 after viewing the field data.",
            "Do not tune v1 to make one run look better.",
            "Do not use very_strong as ground truth.",
            "Do not call TPMS-only matches confirmed.",
            "Do not fabricate movement between receiver sites.",
            "Do not use camera semantic identity as an RF matching feature.",
            "Retain raw evidence references required for later ground-truth annotation.",
        ],

        "measure": [
            "observation count per receiver",
            "accepted/duplicate/rejected ingest count per receiver",
            "receiver spool reconciliation",
            "clock-quality distribution",
            "protocol/model distribution per site",
            "frequency distribution per site",
            "unknown/uncanonicalizable evidence per site",
            "pass count per site",
            "sensor identities per pass",
            "shared-sensor count distribution",
            "overlap coefficient distribution",
            "Jaccard distribution",
            "base score distribution",
            "absolute-cap distribution",
            "competition count distribution",
            "score-margin distribution",
            "competition-factor distribution",
            "final groundview_match_v1 score distribution",
            "candidate ambiguity rate",
            "number of upstream passes with no feasible downstream candidate",
            "downstream fingerprint stability",
            "ground-truth annotation references when available",
        ],

        "required_outputs": [
            "immutable raw field evidence",
            "exact run manifests",
            "receiver/site configuration snapshots",
            "receiver-link configuration snapshot",
            "per-run JSON report",
            "per-run CSV report",
            "candidate-match evidence table",
            "ambiguity report",
            "unknown-protocol report",
            "manual ground-truth annotation references",
        ],

        "field_validation_status": (
            "P17 measures real downstream candidate behavior. "
            "It does not by itself establish matcher precision/recall unless enough independent ground-truth labels exist."
        ),

        "done_when": (
            "The real two-site evidence can be deterministically replayed through frozen v1, "
            "candidate matches and ambiguity are inspectable, and the report distinguishes what was observed, "
            "what was deterministically derived, and what remains inferred."
        ),
    },

    # =========================================================================
    # PHASE 18 — FIELD-CALIBRATED MATCHER V2 RESEARCH
    # =========================================================================

    "phase_18_field_calibrated_matcher_v2_research": {
        "goal": (
            "Evaluate possible matcher improvements using labelled physical field evidence while preserving "
            "groundview_match_v1 and all v1 historical outputs."
        ),

        "prerequisites": [
            "Phase 17 field captures exist.",
            "Exact P17 run manifests exist.",
            "Ground-truth annotations include known-same road-unit examples.",
            "Ground-truth annotations include known-different road-unit examples.",
            "The number/quality of labelled examples is sufficient to make evaluation meaningful.",
        ],

        "build": [
            "Versioned experimental matcher runner.",
            "Side-by-side v1 versus candidate-v2 comparison.",
            "Precision calculation.",
            "Recall calculation.",
            "False-positive analysis.",
            "False-negative analysis.",
            "Threshold sweep tooling.",
            "Score-component distribution reporting.",
            "Competition-behavior comparison.",
            "Versioned output persistence.",
        ],

        "rules": [
            "Never mutate groundview_match_v1.",
            "Never overwrite v1 match rows with experimental results.",
            "Never reinterpret historical v1 results as v2.",
            "Unlabelled candidate matches are not ground truth.",
            "A changed scoring formula is a new matcher version.",
            "A changed weight is a new matcher version.",
            "A changed shared-count cap is a new matcher version.",
            "A changed confidence threshold is a new matcher version.",
            "A changed competition rule is a new matcher version.",
            "A changed hard gate that affects score eligibility is a new matcher version.",
            "Matcher-v2 research does not authorize production deployment.",
            "Do not add FMCSA/carrier/company identity as an RF matcher feature.",
            "Do not add opaque ML merely because labelled data exists.",
        ],

        "possible_outcomes": [
            "groundview_match_v1 remains preferred",
            "a transparent groundview_match_v2 candidate is justified",
            "insufficient evidence exists to change the matcher",
        ],

        "done_when": (
            "A candidate matcher-v2 behavior, if justified, can be objectively compared with frozen v1 "
            "against the exact same labelled evidence and exact run manifests without altering v1 history."
        ),
    },

    # =========================================================================
    # PHASE DEPENDENCIES
    # =========================================================================

    "post_p14_dependencies": {
        "phase_15_cloud_field_readiness": [],

        "phase_16_single_real_receiver": [
            "phase_15_cloud_field_readiness",
            "physical_receiver_available",
        ],

        "phase_17_two_site_downstream_experiment": [
            "phase_16_single_real_receiver",
            "second_physical_receiver_available",
        ],

        "phase_18_field_calibrated_matcher_v2_research": [
            "phase_17_two_site_downstream_experiment",
            "sufficient_ground_truth_annotations",
        ],

        "critical_path": "P15 -> P16 -> P17 -> P18",

        "execution_rule": (
            "P15 is immediately executable software work. "
            "P16 and P17 are partly software/operations but cannot be declared field-complete without physical evidence. "
            "P18 cannot be meaningfully completed without labelled P17 evidence."
        ),
    },

    # =========================================================================
    # TEST STRATEGY
    # =========================================================================

    "testing": {
        "p15_high_value": [
            "matcher authoritative competition universe",
            "matcher candidate-order independence",
            "canonical 89.29 regression",
            "file-store concurrent mutation",
            "atomic-write recovery",
            "corrupt-state fail-closed",
            "batch idempotency",
            "durable ACK semantics",
            "receiver HMAC validation",
            "stale timestamp rejection",
            "nonce replay rejection",
            "receiver state/quarantine enforcement",
            "request size limit",
            "batch size limit",
            "fixture/field mode isolation",
            "canonical identity projection coexistence",
            "run-manifest completeness",
            "unknown protocol versus decoder failure",
            "GroundView disabled SkyView regression",
            "Vercel receiver mutation remains unavailable",
        ],

        "p16_operational": [
            "receiver restart with queued spool",
            "uploader restart with queued spool",
            "network outage and recovery",
            "central service outage and recovery",
            "duplicate upload retry",
            "field store contains no synthetic evidence",
            "physical observation replay determinism",
        ],

        "p17_field": [
            "two receiver ingest reconciliation",
            "clock-quality report",
            "real receiver-link gate behavior",
            "downstream shared-sensor distribution",
            "candidate ambiguity",
            "run-manifest reproducibility",
        ],

        "p18_calibration": [
            "v1 output unchanged",
            "v1 and v2 coexist",
            "labelled precision/recall",
            "threshold sweep reproducibility",
            "candidate-v2 does not mutate historical v1",
        ],
    },

    # =========================================================================
    # FIELD VALIDATION BOUNDARY
    # =========================================================================

    "field_validation_boundary": {
        "implement_now": [
            "configuration",
            "versioning",
            "source-event identity",
            "durable receiver spool",
            "authentication",
            "idempotency",
            "replay",
            "run manifests",
            "metrics",
            "reports",
            "unknown evidence inventory",
            "calibration infrastructure",
        ],

        "do_not_fabricate": [
            "Class 8 TPMS penetration",
            "real RF range",
            "real protocol distribution",
            "real sensor count per rig",
            "real transmission cadence",
            "real downstream fingerprint stability",
            "real matcher precision/recall",
            "real optimal receiver spacing",
            "real optimal clustering window",
            "real antenna performance",
        ],

        "rule": (
            "Fixture/replay success proves software behavior only. "
            "Only physical evidence may close empirical field-validation items."
        ),
    },

    # =========================================================================
    # CLOUD HOSTING DECISION
    # =========================================================================

    "hosting_policy": {
        "preferred_for_p16": (
            "Use a local/field long-lived Node GroundView service with the hardened single-writer file adapter "
            "when public internet ingest is unnecessary."
        ),

        "acceptable_remote_p16_option": (
            "One long-lived GroundView Node service using one persistent volume and one writer process, "
            "protected by P15 receiver authentication and route isolation."
        ),

        "future_postgres_option": (
            "One long-lived GroundView Node service with PostgreSQL is appropriate once actual field operation "
            "demonstrates multi-writer, sustained multi-receiver, retention, query, or redundancy requirements."
        ),

        "not_allowed": [
            "Kubernetes",
            "new Vercel project for GroundView",
            "production Vercel receiver ingest",
            "second SkyView application",
            "second globe",
            "premature distributed microservices",
        ],
    },

    # =========================================================================
    # COMPLETION REPORT
    # =========================================================================

    "completion_report": {
        "style": "short engineering execution report",

        "always_include": [
            "phase worked",
            "P15 implementation steps completed",
            "current P15 step if incomplete",
            "files changed",
            "repository-native architecture decisions",
            "tests added",
            "commands run",
            "test results",
            "fixture baseline results",
            "canonical 89.29 actual result",
            "matcher-v1 reconciliation result",
            "storage durability result",
            "auth result",
            "synthetic/field isolation result",
            "provenance correction result",
            "run-manifest result",
            "known failures",
            "FIELD_VALIDATION_REQUIRED items",
            "next safe action",
        ],

        "p15_specific": [
            "whether P15.0 through P15.10 passed",
            "whether all P15 exit gates passed",
            "whether GroundView is safe for one physical receiver",
            "whether any public receiver ingress was actually configured",
            "whether PostgreSQL was avoided or justified by actual repository constraints",
        ],

        "p16_specific": [
            "capture session metadata",
            "real observation counts",
            "spool reconciliation",
            "unknown protocol observations",
            "synthetic evidence count",
            "replay reproducibility",
        ],

        "p17_specific": [
            "receiver A/B metadata",
            "real receiver-link configuration",
            "candidate match distributions",
            "ambiguity statistics",
            "which conclusions remain unvalidated",
        ],

        "p18_specific": [
            "ground-truth sample counts",
            "v1 precision/recall",
            "candidate-v2 precision/recall",
            "false-positive/false-negative comparison",
            "whether any v2 change is actually justified",
        ],

        "do_not_include": [
            "research-paper prose",
            "invented field observations",
            "claims that hardware work occurred when no hardware was available",
            "production deployment claims unless explicitly authorized later",
        ],
    },

    # =========================================================================
    # CURSOR STARTING INSTRUCTIONS
    # =========================================================================

    "cursor_start": [
        "Read this entire specification before editing.",
        "Read the committed authoritative GroundView specification.",
        "Read GROUNDVIEW_STATUS.md if present.",
        "Inspect the actual current repository tree and GroundView implementation.",
        "Do not assume reviewed tar paths exactly match the current working tree.",
        "Confirm current branch and repository status non-destructively.",
        "Do not discard unrelated local work.",
        "Begin with P15.0. Do not jump directly to storage, auth, or receiver-node implementation.",
        "Confirm the current GroundView fixture/replay baseline before P15 modifications.",
        "Run the existing GroundView matcher/replay/SkyView regression tests.",
        "Record current results in GROUNDVIEW_STATUS.md.",
        "Execute P15.0 through P15.10 in dependency order.",
    ],

    # =========================================================================
    # IMMEDIATE EXECUTION DIRECTIVE
    # =========================================================================

    "execute": (
        "Implement Phase 15 Cloud / Field Readiness now in the existing SkyView repository. "
        "Execute the explicit p15_implementation_sequence from P15.0 through P15.10. "
        "Do not skip a prerequisite step or declare a later step complete while an earlier dependency gate is failed. "

        "GroundView remains a native layer under The Mabeline Project and must preserve the frozen "
        "OBSERVED / DERIVED / INFERRED truth model, road_unit_v1 definition, no-fake-GPS rule, "
        "no-confirmed-label rule, no-FMCSA-matcher-dependency rule, and no-second-app rule. "

        "Treat groundview_match_v1 as authoritative according to the formula, caps, confidence thresholds, "
        "canonical 89.29 fixture, and competitor semantics specified here. The reviewed current competition "
        "grouping is a pre-field implementation defect: correct it and its tests to shares-pass-A OR shares-pass-B, "
        "then freeze v1. Do not invent matcher v2 during P15. "

        "Stabilize the source-event, provenance, version, and mode contracts before relying on them from storage "
        "or live receiver code. Make versioned DERIVED canonical identity projections authoritative and preserve "
        "raw immutable OBSERVED protocol/model/sensor evidence. "

        "Harden the existing storage boundary rather than introducing PostgreSQL merely by preference. "
        "Serialize mutations, fail closed on corruption/read failures, make replacement atomic/durable, "
        "retain a single writer process, and acknowledge receiver events only after durable commit. "

        "After storage semantics are correct, implement explicit fixture/field/test modes. Field mode must never "
        "auto-seed synthetic evidence. Synthetic data must use source_type='synthetic_fixture'. "

        "Then implement receiver HMAC authentication, nonce replay protection, receiver-state checks, body/batch limits, "
        "and durable bounded batch semantics. Do not design the receiver spool around an ambiguous ACK contract. "

        "Implement exact replay/run manifests linking evidence to receiver/link/canonicalization/clustering/matcher "
        "versions and configuration snapshots before accepting physical field evidence. "
        "Separate unknown protocol evidence from actual decoder failure. "

        "Isolate the future field-facing HTTP surface so authenticated node/events and node/heartbeat can be exposed "
        "without automatically exposing GroundView administrative mutation routes. "

        "Do not deploy GroundView to production. Do not run vercel --prod. Do not create another Vercel project. "
        "Do not fabricate physical field results. Do not mark P16, P17, or P18 complete without their required "
        "physical or labelled evidence. "

        "Proceed autonomously through ordinary repository-native implementation decisions. "
        "When a foundational assumption fails, repair the earliest responsible abstraction, invalidate dependent "
        "P15 gates, and rerun them instead of adding downstream workarounds. "

        "Complete P15 only when P15.0 through P15.10 and every Phase 15 exit gate pass. "
        "If physical receiver hardware is available after P15, P16 may proceed according to this specification. "
        "If physical hardware is not available, leave P16 explicitly FIELD_VALIDATION_REQUIRED and stop after "
        "reporting a complete, tested P15 software state rather than fabricating P16 success."
    ),
}

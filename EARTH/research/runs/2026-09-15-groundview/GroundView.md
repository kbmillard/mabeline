> **HISTORICAL / COMPLETED (P0–P14).** This document is the completed GroundView software-foundation specification (phases 0–14 on fixtures/replay). It is **not** current execution instructions.
>
> Current authoritative execution spec: `SkyView/GROUNDVIEW_SPEC.md` (P15–P18 durable field readiness). Ledger: `SkyView/GROUNDVIEW_STATUS.md`.
>
> Do not overwrite this file. Do not execute P0–P14 again merely because P15 begins.

---

GROUNDVIEW_PROJECT = { "project": { "name": "GroundView", "parent": "The Mabeline Project", "application": "SkyView", "surface": "/EARTH", "repository": "SkyView", "working_branch": "wip/groundview", "matcher_version": "groundview_match_v1", "clustering_version": "groundview_cluster_v1", "canonicalization_version": "groundview_canonical_v1",
    "authority": (
        "This is the authoritative GroundView implementation specification. "
        "It incorporates the original GroundView design, the accepted first-dev plan, "
        "the explicit groundview_match_v1 contract, and the structural-integrity review."
    ),

    "execution_mode": (
        "Build the complete GroundView software foundation in dependency-safe phases now. "
        "Do not wait for physical RF field validation before implementing software layers "
        "that can be built and tested with replay, synthetic fixtures, mock providers, "
        "recorded evidence, interfaces, or versioned placeholders. "
        "When physical evidence is required to answer an empirical question, implement "
        "the complete software path for measuring that question and mark only the empirical "
        "claim FIELD_VALIDATION_REQUIRED."
    ),

    "core_question": (
        "Can persistent RF sensor emissions associated with one passing commercial "
        "tractor-trailer form a composite physical fingerprint that allows GroundView "
        "to recognize the same road unit at downstream observation sites?"
    ),

    "road_unit_definition": (
        "For GroundView v1, a tractor plus its attached trailer traveling together "
        "is one road unit. Road-unit tracking does not require separating tractor and trailer."
    ),
},

# =========================================================================
# AUTHORITATIVE PROJECT RULES
# =========================================================================

"project_rules": {
    "git_and_prod": [
        "GroundView work stays on wip/groundview until explicitly instructed otherwise.",
        "Do not push wip/groundview unless explicitly instructed.",
        "Do not run vercel --prod.",
        "Do not create another Vercel project.",
        "Do not mix Mabeline financial/ dirt or warehouse bytes into GroundView commits.",
        "Do not mix unrelated Dispatch, offices, divisions, or Place-of-Performance work into GroundView.",
        "Production earth continues to ship only from the approved clean production baseline.",
    ],

    "architecture": [
        "GroundView is part of SkyView, not a second application.",
        "GroundView lives under The Mabeline Project.",
        "Reuse existing provider, API, Cesium, layer-state, cache, credit, selection, and UI patterns.",
        "Prefer repository-native modules and existing abstractions.",
        "Do not add a major service or database merely by preference.",
        "Use existing .gev-cache/local persistence patterns first when they satisfy the GroundView storage contract.",
        "Long-lived receiver/federation persistence must not depend on ephemeral Vercel serverless storage.",
    ],

    "truth_model": [
        "OBSERVED means directly received or measured physical evidence.",
        "DERIVED means deterministic processing of observed evidence.",
        "INFERRED means probabilistic identity, continuity, semantic, or association reasoning.",
        "Never silently convert DERIVED or INFERRED state into OBSERVED state.",
        "Never render inferred truck movement as measured GPS.",
        "Never invent exact vehicle coordinates from receiver proximity.",
        "Never use confirmed as a TPMS-only confidence label.",
    ],

    "data_integrity": [
        "Raw observations are immutable.",
        "Unknown evidence remains valid evidence even when it cannot yet participate in matching.",
        "Derived state must be reproducible.",
        "Inferred state must retain the evidence and algorithm/config versions that produced it.",
        "Every algorithm that affects persisted output must carry a version.",
        "Every derived or inferred result must be attributable to exact config snapshots.",
        "Historical algorithm versions must remain reproducible when retained data references them.",
        "Raw numeric TPMS IDs never match across incompatible canonical namespaces.",
    ],

    "implementation": [
        "Build all software-buildable phases without waiting for field hardware.",
        "Respect dependency gates rather than blindly following phase numbers.",
        "Do not patch around a failed earlier abstraction in a later phase.",
        "Repair the earliest responsible abstraction and rerun dependent gates.",
        "Do not rewrite unrelated SkyView architecture.",
        "Do not redesign SkyView visually.",
        "Keep field-dependent values configurable and versioned.",
        "Prefer transparent deterministic algorithms before ML.",
        "Do not use ML where an authoritative deterministic algorithm already exists.",
    ],
},

# =========================================================================
# SPECIFICATION PRECEDENCE
# =========================================================================

"specification_precedence": {
    "authoritative": [
        "Project name GroundView.",
        "Parent The Mabeline Project.",
        "Application SkyView.",
        "Surface /EARTH.",
        "Working branch wip/groundview.",
        "OBSERVED / DERIVED / INFERRED truth model.",
        "Raw observed evidence immutability.",
        "groundview_match_v1 formula.",
        "groundview_match_v1 weights.",
        "groundview_match_v1 shared-count-strength formula.",
        "groundview_match_v1 absolute overlap caps.",
        "groundview_match_v1 competition factors.",
        "groundview_match_v1 confidence thresholds.",
        "groundview_match_v1 competitor semantics.",
        "The forbidden confirmed label.",
        "The canonical 89.29 matcher example.",
        "Road-unit v1 definition.",
        "No fake GPS.",
        "No FMCSA dependency for core GroundView tracking.",
        "No second application.",
        "No production Vercel deployment.",
    ],

    "repository_adaptable": [
        "Exact filenames.",
        "Exact internal module layout.",
        "Provider entry-point names.",
        "Repository-native API route shape.",
        "Local cache serialization details.",
        "Internal helper decomposition.",
        "Error-class organization.",
        "Test helper organization.",
        "Cesium implementation details that preserve GroundView semantics.",
        "UI spacing, icon reuse, and repository-native presentation details.",
    ],

    "field_adaptable_only_by_version_or_config": [
        "Clustering window.",
        "Receiver spacing.",
        "RF range assumptions.",
        "Protocol coverage.",
        "Antenna configuration.",
        "Clock-quality thresholds.",
        "Field-calibrated score behavior in a future matcher version.",
        "Field-calibrated clustering behavior in a future cluster version.",
    ],

    "rule": (
        "Repository-adaptable decisions may be made autonomously when existing SkyView "
        "conventions provide clear evidence. Authoritative behavior may not be changed. "
        "Empirical behavior remains configurable/versioned and must never be silently "
        "promoted from an assumption into observed fact."
    ),
},

# =========================================================================
# PERSISTENT PROJECT EXECUTION STATE
# =========================================================================

"execution_state": {
    "status_file": "GROUNDVIEW_STATUS.md",
    "committed": True,

    "purpose": (
        "GROUNDVIEW_STATUS.md is the persistent multi-session execution ledger. "
        "Cursor must be able to resume GroundView safely after context compaction, "
        "agent handoff, interruption, or a later session without relying on chat history."
    ),

    "phase_states": [
        "NOT_STARTED",
        "IN_PROGRESS",
        "SOFTWARE_COMPLETE",
        "FIELD_VALIDATION_REQUIRED",
        "BLOCKED",
        "COMPLETE",
        "INVALIDATED_BY_UPSTREAM_CHANGE",
    ],

    "required_structure": {
        "specification": [
            "authoritative_prompt_path",
            "working_branch",
            "last_reviewed_commit",
        ],

        "execution": [
            "active_phases",
            "software_complete",
            "field_validation_required",
            "blocked",
            "invalidated_by_upstream_change",
        ],

        "authoritative_versions": [
            "event_schema",
            "canonicalization",
            "clustering",
            "matcher",
            "track_builder",
            "camera_detector optional",
            "visual_recognizer optional",
            "binding optional",
        ],

        "repository_integration": [
            "provider_pattern",
            "api_pattern",
            "storage_pattern",
            "cesium_lifecycle_pattern",
            "layer_state_pattern",
            "selection_pattern",
            "credit_pattern",
            "test_commands",
        ],

        "latest_config_snapshots": [
            "receiver_config",
            "receiver_link_config",
            "clustering_config",
            "canonicalization_config",
        ],

        "phase_gates": [
            "phase",
            "status",
            "commit",
            "commands",
            "evidence",
        ],

        "tests_last_run": [
            "commit",
            "commands",
            "results",
        ],

        "other": [
            "known_failures",
            "architectural_decisions",
            "field_validation_required",
            "next_safe_resume_action",
            "rerun_before_continuing",
        ],
    },

    "update_when": [
        "before starting a new phase",
        "after a phase exit gate passes",
        "when a phase becomes blocked",
        "when an upstream repair invalidates a dependent gate",
        "when a repository-adaptive architectural decision is made",
        "whenever an empirical item moves into or out of FIELD_VALIDATION_REQUIRED",
        "before ending a substantial implementation session",
    ],

    "rules": [
        "GROUNDVIEW_STATUS.md is committed on wip/groundview.",
        "A phase may be marked SOFTWARE_COMPLETE only when its software gate has evidence.",
        "A phase may be marked COMPLETE only when all required software and empirical gates applicable to that state are satisfied.",
        "Do not record credentials or secrets.",
        "Do not place large logs in the status file.",
        "Do not silently redefine authoritative project behavior in the status file.",
        "Record authoritative versions as references, not editable substitutes for this specification.",
    ],
},

# =========================================================================
# GLOBAL INVARIANTS
# =========================================================================

"global_invariants": {
    "one_evidence_path": (
        "Synthetic fixture input, recorded replay, rtl_433 input, custom decoder input, "
        "and physical receiver-node input all converge through one versioned GroundView "
        "source-event envelope and one RF normalization path."
    ),

    "observed_evidence_immutability": (
        "No decoder upgrade, canonicalization change, clustering run, matcher, track builder, "
        "camera result, experiment, report, calibration, or UI action may mutate the original "
        "observed evidence."
    ),

    "canonical_identity_is_derived": (
        "Canonical sensor identity is a versioned DERIVED projection of raw protocol/model/"
        "sensor evidence. It is never directly observed truth."
    ),

    "stable_event_identity": (
        "Re-ingesting the same source event yields the same observation ID. "
        "Two distinct real transmissions must not collapse solely because their payload bytes match."
    ),

    "deterministic_derived_identity": (
        "Equivalent source evidence plus identical algorithm/config versions yields identical "
        "pass, fingerprint, candidate-match, and track identities."
    ),

    "deterministic_ordering": (
        "Whenever primary timestamps are equal, use a stable secondary deterministic key."
    ),

    "version_coexistence": (
        "A newer algorithm version may coexist with an older algorithm version. "
        "Computing v2 must never overwrite historical v1 outputs."
    ),

    "configuration_snapshots": (
        "Every derivation/replay run references immutable snapshots of all mutable configuration "
        "that materially affects its output."
    ),

    "clock_provenance": (
        "Receiver timestamps are preserved exactly as received. "
        "Clock correction is separate DERIVED data and never silently replaces observed time."
    ),

    "unknown_evidence_preservation": (
        "Evidence does not need to be canonicalizable, clusterable, or matchable to remain valid evidence."
    ),

    "duplicate_distinction": (
        "Duplicate ingest is eliminated by source-event identity/idempotency. "
        "Legitimate repeated RF transmissions remain separate OBSERVED packet events but contribute "
        "one canonical sensor identity to set-based fingerprint matching."
    ),

    "frontend_projection": (
        "SkyView/Cesium is a projection of persisted GroundView state and never the source of truth."
    ),

    "reports_are_read_only": (
        "Reports, calibration, experiment comparison, and visual inspection never mutate evidence "
        "or historical algorithm-version output."
    ),

    "no_silent_fallback": (
        "If a persisted run references an unavailable algorithm/config version, replay fails explicitly "
        "instead of silently substituting the current implementation."
    ),

    "dependency_invalidation": (
        "Repairing an upstream abstraction invalidates dependent phase gates until required tests rerun."
    ),

    "phase_state_explicitness": (
        "SOFTWARE_COMPLETE, FIELD_VALIDATION_REQUIRED, BLOCKED, and COMPLETE are distinct states."
    ),
},

# =========================================================================
# TARGET REPOSITORY LAYOUT
# =========================================================================

"target_layout": {
    "server/providers/groundview/": [
        "provider entry",
        "http",
        "source-event adapter",
        "normalize",
        "storage",
        "receiver config",
        "receiver-link config",
        "cluster",
        "fingerprints",
        "matches",
        "tracks",
        "replay",
        "experiments",
        "reports",
        "diagnostics",
        "health",
        "rf/",
        "receiver-node/",
        "federation/",
        "camera/",
        "identity/",
        "binding/",
    ],

    "src/data/groundview/": [
        "layer entry",
        "entities",
        "selection",
        "styles",
        "provenance",
        "match.mjs",
        "match.test.mjs",
        "repository-native GroundView frontend helpers",
    ],

    "fixtures/groundview/": [
        "synthetic two-receiver NDJSON",
        "synthetic competing-candidates fixture",
        "synthetic protocol-collision fixture",
        "synthetic unknown-protocol fixture",
        "synthetic receiver-node envelope fixture",
        "synthetic camera binding fixture",
        "receiver configuration fixture",
    ],

    "EARTH/research/runs/2026-09-15-groundview/": [
        "GroundView.rtf",
        "GroundView.md",
        "field-experiment.md",
        "protocol-notes.md",
        "matcher-calibration.md",
    ],

    "rule": (
        "This tree is guidance, not permission to ignore better existing repository conventions. "
        "Repository-native placement wins when semantics remain unchanged."
    ),
},

# =========================================================================
# FOUNDATION CONTRACT — MUST EXIST BEFORE PHASE 1 DEPENDENTS
# =========================================================================

"foundation_contract": {
    "must_be_established_before_phase_1_dependents": True,
    "event_schema_version": "groundview_event_v1",

    "source_event_rule": (
        "Fixture replay, recorded rtl_433 input, custom decoder input, and future physical "
        "receiver-node input must adapt into one GroundView source-event envelope and then "
        "call the same RF normalize_event path. Do not create source-specific domain pipelines."
    ),

    "event_envelope_minimum": [
        "schema_version",
        "source_type",
        "receiver_id",
        "source_event_id",
        "receiver_timestamp",
        "sequence_number optional",
        "frequency_hz optional",
        "decoder_name optional",
        "decoder_version optional",
        "payload",
        "signal_metadata optional",
        "capture_ref optional",
        "clock_metadata optional",
    ],

    "supported_source_types_initial": [
        "synthetic_fixture",
        "rtl433_recorded",
        "rtl433_live_adapter",
        "custom_decoder",
        "receiver_node",
    ],

    "stable_identity_rules": [
        "Re-ingesting the same source event must resolve to the same observation_id.",
        "Two distinct physical packet events remain distinct observations even when decoded payload content is equal.",
        "Derived IDs must be deterministic from source IDs plus relevant algorithm/config versions.",
        "Equal timestamps require deterministic secondary ordering.",
    ],

    "single_normalizer": (
        "No replay, receiver, decoder, federation, report, or API module may implement "
        "an alternate RF normalization path."
    ),

    "foundation_gate": [
        "actual repository integration points recorded",
        "source-event schema frozen as groundview_event_v1",
        "stable source-event identity rule implemented",
        "one normalize_event entry point exists",
        "storage contract exists",
        "deterministic ID strategy exists",
        "config snapshot strategy exists",
        "clock provenance rules exist",
        "groundview_cluster_v1 semantics exist",
        "groundview_match_v1 competition semantics exist",
    ],
},

# =========================================================================
# DETERMINISTIC IDENTIFIER CONTRACT
# =========================================================================

"identifier_contract": {
    "principle": (
        "IDs for rebuildable GroundView state must be deterministic where their underlying "
        "evidence and version/config inputs are deterministic."
    ),

    "observation_id": (
        "Derive from receiver/source identity plus stable source_event_id and event-schema namespace. "
        "Do not derive solely from decoded payload bytes."
    ),

    "identity_projection_id": (
        "Derive from observation_id plus canonicalization_version plus canonicalization_config_snapshot_id."
    ),

    "pass_id": (
        "Derive from receiver_id, ordered member observation IDs, clustering_version, "
        "and clustering_config_snapshot_id."
    ),

    "fingerprint_id": (
        "Derive from pass_id, canonicalization_version, and deterministic ordered canonical identity set."
    ),

    "match_id": (
        "Derive from ordered endpoint pass IDs, matcher_version, and matcher config/version identity."
    ),

    "track_id": (
        "Derive from deterministic ordered pass/match membership plus track_builder_version."
    ),

    "ordering_rule": (
        "Sort using explicit stable keys before constructing deterministic IDs. "
        "Never depend on filesystem order, hash-map iteration order, ingest arrival order, "
        "or database-return order without an explicit sort."
    ),

    "serialization_rule": (
        "Canonical replay/report output must use deterministic ordering so identical runs "
        "produce semantically and, where practical, byte-equivalent artifacts."
    ),
},

# =========================================================================
# STORAGE CONTRACT
# =========================================================================

"storage_contract": {
    "boundaries": {
        "observed": (
            "Append-only immutable evidence. Duplicate source-event ingest resolves idempotently "
            "without rewriting prior observed evidence."
        ),

        "derived": (
            "Rebuildable deterministic state stored under explicit algorithm/config versions."
        ),

        "inferred": (
            "Rebuildable probabilistic state stored under explicit algorithm/config versions."
        ),

        "config": (
            "Mutable operational configuration whose exact immutable snapshots are retained "
            "for every derivation/replay run that depends on it."
        ),
    },

    "required_snapshots": [
        "receiver configuration",
        "receiver-link configuration",
        "canonicalization configuration",
        "clustering configuration",
        "matcher version/config",
        "track-builder version/config",
        "clock-correction version/config when used",
        "experiment configuration when applicable",
    ],

    "version_coexistence_rule": (
        "Computing a new algorithm version must not overwrite results produced by an older "
        "version. groundview_match_v1 and future match versions must coexist."
    ),

    "implementation_rule": (
        "Use repository-native .gev-cache/local persistence initially where appropriate, "
        "but GroundView domain modules must use a storage boundary rather than direct "
        "filesystem assumptions."
    ),

    "minimum_storage_operations": [
        "append/get observed source events",
        "append/get RF observations",
        "write/read config snapshots",
        "write/read versioned derived records",
        "write/read versioned inferred records",
        "delete/rebuild derived state without deleting observations",
        "query by receiver/time/version",
        "query historical version output",
    ],
},

# =========================================================================
# CLOCK / TIME PROVENANCE
# =========================================================================

"clock_and_time_provenance": {
    "rules": [
        "Preserve receiver/source timestamp exactly as received.",
        "Preserve central ingested_at separately.",
        "Do not silently replace receiver time with corrected time.",
        "Any clock correction is DERIVED and carries method/version plus original timestamp.",
        "Replay manifests state whether clustering/matching uses raw receiver time or a specific corrected-time version.",
        "Receiver clock-quality metadata is retained with experiment/config snapshots.",
    ],

    "future_clock_correction_projection": {
        "provenance": "DERIVED",
        "fields": [
            "observation_id",
            "original_receiver_timestamp",
            "corrected_timestamp",
            "correction_method",
            "correction_version",
            "quality",
        ],
    },
},

# =========================================================================
# DOMAIN MODEL
# =========================================================================

"domain_model": {
    "receiver": {
        "provenance": "CONFIG",
        "fields": [
            "receiver_id",
            "name",
            "latitude",
            "longitude",
            "altitude_m optional",
            "road_name optional",
            "road_direction optional",
            "site_id optional",
            "enabled_frequencies_hz",
            "antenna_metadata optional",
            "hardware_metadata optional",
            "software_metadata optional",
            "decoder_versions optional",
            "clock_metadata optional",
            "status",
            "created_at",
            "updated_at",
        ],
    },

    "receiver_link": {
        "provenance": "CONFIG",
        "fields": [
            "from_receiver_id",
            "to_receiver_id",
            "distance_meters optional",
            "minimum_travel_seconds",
            "maximum_travel_seconds",
            "direction optional",
            "road_name optional",
            "enabled",
        ],
    },

    "rf_observation": {
        "provenance": "OBSERVED",
        "immutable": True,

        "fields": [
            "observation_id",
            "source_event_id",
            "source_type",
            "event_schema_version",
            "receiver_id",
            "site_id optional",
            "receiver_timestamp",
            "observed_at",
            "ingested_at",
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
            "clock_metadata optional",
        ],

        "forbidden_as_observed_fields": [
            "canonical_sensor_identity",
            "truck_pass_identity",
            "fingerprint_identity",
            "same_truck_identity",
            "semantic carrier identity inferred from other evidence",
        ],
    },

    "sensor_identity_projection": {
        "provenance": "DERIVED",

        "purpose": (
            "Versioned canonical interpretation of protocol/model/raw sensor identity "
            "from an immutable RF observation."
        ),

        "fields": [
            "identity_projection_id",
            "observation_id",
            "canonical_sensor_identity optional",
            "canonicalization_version",
            "canonicalization_config_snapshot_id",
            "normalization_status",
        ],

        "rules": [
            "Raw protocol/model/sensor_id evidence remains on the RF observation.",
            "Canonical sensor identity is never directly observed evidence.",
            "A new canonicalization version creates a new projection.",
            "A new canonicalization version never mutates the raw observation.",
            "Multiple canonicalization versions may coexist.",
        ],
    },

    "truck_pass": {
        "provenance": "DERIVED",

        "fields": [
            "pass_id",
            "receiver_id",
            "start_time",
            "end_time",
            "duration_seconds",
            "member_observation_ids",
            "sensor_identity_projection_ids",
            "sensor_identities",
            "sensor_count",
            "observation_count",
            "protocol_breakdown",
            "model_breakdown",
            "rssi_summary",
            "snr_summary",
            "canonicalization_version",
            "clustering_version",
            "clustering_config_snapshot_id",
            "receiver_config_snapshot_id",
            "build_version",
        ],
    },

    "rf_fingerprint": {
        "provenance": "DERIVED",

        "fields": [
            "fingerprint_id",
            "pass_id",
            "receiver_id",
            "sensor_identity_projection_ids",
            "sensor_identities",
            "sensor_count",
            "first_seen",
            "last_seen",
            "canonicalization_version",
            "clustering_version",
            "clustering_config_snapshot_id",
            "fingerprint_version",
        ],

        "rule": (
            "Fingerprint membership means canonical sensors observed together in one derived pass. "
            "It does not assert permanent ownership by a vehicle."
        ),
    },

    "candidate_match": {
        "provenance": "INFERRED",

        "fields": [
            "match_id",
            "pass_a_id",
            "pass_b_id",
            "receiver_a_id",
            "receiver_b_id",
            "shared_sensor_identities",
            "shared_sensor_count",
            "set_a_count",
            "set_b_count",
            "union_count",
            "jaccard_similarity",
            "overlap_coefficient",
            "containment_a",
            "containment_b",
            "shared_count_strength",
            "elapsed_seconds",
            "minimum_travel_seconds",
            "maximum_travel_seconds",
            "time_feasible",
            "direction_feasible",
            "base_score",
            "absolute_overlap_cap",
            "capped_score",
            "competing_candidate_count",
            "best_competing_score optional",
            "score_margin optional",
            "competition_factor",
            "final_score",
            "confidence_label",
            "matcher_version",
            "receiver_config_snapshot_id",
            "receiver_link_config_snapshot_id",
            "canonicalization_version",
            "clustering_version",
        ],
    },

    "road_unit_track": {
        "provenance": "INFERRED",

        "purpose": (
            "Temporally bounded chain of compatible GroundView pass matches. "
            "It is not a permanent truck identity."
        ),

        "fields": [
            "track_id",
            "ordered_pass_ids",
            "ordered_match_ids",
            "ordered_receiver_ids",
            "start_time",
            "end_time",
            "mean_edge_score",
            "weakest_link_score",
            "track_builder_version",
            "track_builder_config_snapshot_id",
            "status",
        ],
    },

    "camera_observation": {
        "provenance": "OBSERVED",

        "fields": [
            "camera_observation_id",
            "camera_id",
            "observed_at",
            "latitude",
            "longitude",
            "image_ref optional",
            "frame_ref optional",
            "source",
            "raw_metadata",
        ],
    },

    "visual_detection": {
        "provenance": "DERIVED",

        "fields": [
            "detection_id",
            "camera_observation_id",
            "object_class",
            "bounding_box",
            "confidence",
            "tracking_id optional",
            "detector_version",
        ],
    },

    "visual_identity_candidate": {
        "provenance": "INFERRED",

        "fields": [
            "identity_candidate_id",
            "detection_id",
            "identity_type",
            "normalized_value",
            "raw_text optional",
            "confidence",
            "recognizer_version",
        ],
    },

    "multimodal_binding": {
        "provenance": "INFERRED",

        "fields": [
            "binding_id",
            "rf_pass_id",
            "camera_observation_id",
            "visual_detection_id optional",
            "identity_candidate_ids",
            "time_delta_ms",
            "site_consistency",
            "binding_score",
            "binding_version",
        ],
    },
},

# =========================================================================
# CANONICAL SENSOR IDENTITY
# =========================================================================

"canonical_sensor_identity": {
    "version": "groundview_canonical_v1",

    "strategy": "rtl433_protocol:model:sensor_id",

    "example": "241:TST-507:12AF93C1",

    "missing_field_policy": {
        "sensor_id_missing": (
            "No canonical sensor identity projection is produced. "
            "Observation remains valid OBSERVED evidence."
        ),

        "protocol_missing": (
            "Do not collapse into a generic namespace that could falsely intersect with "
            "known protocol identities. Use an explicitly versioned unknown namespace only "
            "if groundview_canonical_v1 defines one deterministically."
        ),

        "model_missing": (
            "Handle according to the explicit groundview_canonical_v1 namespace rule. "
            "Do not silently substitute another model."
        ),
    },

    "requirements": [
        "Preserve original protocol, model, and raw sensor ID independently.",
        "Canonicalization is DERIVED.",
        "Canonicalization is replaceable by a new version.",
        "Canonicalization v2 can coexist with v1.",
        "Identical raw IDs from different canonical protocol/model namespaces do not match.",
        "Fingerprint records retain the canonicalization version used.",
    ],
},

# =========================================================================
# PASS CLUSTERING — AUTHORITATIVE PROVISIONAL V1
# =========================================================================

"clustering": {
    "version": "groundview_cluster_v1",
    "strategy": "receiver-local gap-based temporal session clustering",
    "initial_window_seconds": 30,

    "field_validation_status": (
        "30 seconds is a provisional configurable default. "
        "Its real-world optimality remains FIELD_VALIDATION_REQUIRED."
    ),

    "algorithm": [
        "Partition eligible RF observations by receiver_id.",
        "Order each receiver partition by observed_at, then observation_id as deterministic tie-breaker.",
        "Start the first pass with the first ordered observation.",
        "For each next observation, compare its observed_at to the immediately previous observation already assigned to the current pass.",
        "If the gap is <= clustering_window_seconds, add it to the current pass.",
        "If the gap is > clustering_window_seconds, close the current pass and start a new pass.",
        "Arrival order must not affect the result.",
        "Duplicate ingest must already be eliminated through source-event idempotency.",
        "Legitimate repeated RF transmissions remain separate observations.",
        "Repeated transmissions from one canonical sensor contribute one sensor identity to the fingerprint set.",
        "Unknown or noncanonicalizable observations remain stored evidence even if they cannot contribute canonical identity to a fingerprint.",
    ],

    "required_provenance": [
        "clustering_version",
        "clustering_config_snapshot_id",
        "canonicalization_version",
        "receiver_config_snapshot_id",
    ],

    "version_rule": (
        "If field evidence later justifies different clustering semantics, create a new "
        "clustering version. Do not silently mutate groundview_cluster_v1."
    ),
},

# =========================================================================
# MATCHER — AUTHORITATIVE V1
# =========================================================================

"matcher": {
    "version": "groundview_match_v1",
    "strategy": "transparent deterministic fuzzy-set matching",
    "machine_learning": False,

    "definitions": {
        "A": "canonical sensor identity set for upstream pass",
        "B": "canonical sensor identity set for downstream pass",

        "shared_count": "len(A & B)",
        "a_count": "len(A)",
        "b_count": "len(B)",
        "union_count": "len(A | B)",

        "jaccard": (
            "shared_count / union_count "
            "if union_count > 0 else 0.0"
        ),

        "overlap_coefficient": (
            "shared_count / min(a_count, b_count) "
            "if min(a_count, b_count) > 0 else 0.0"
        ),

        "containment_a": (
            "shared_count / a_count "
            "if a_count > 0 else 0.0"
        ),

        "containment_b": (
            "shared_count / b_count "
            "if b_count > 0 else 0.0"
        ),

        "shared_count_strength": (
            "min(shared_count / 6.0, 1.0)"
        ),
    },

    "candidate_generation": [
        "Only compare passes on configured receiver relationships.",
        "Apply configured receiver ordering/direction constraints.",
        "Apply configured minimum and maximum travel-time constraints.",
        "Require at least one shared canonical sensor identity.",
        "Candidates failing a hard gate do not enter the feasible-candidate universe.",
    ],

    "hard_gates": {
        "receiver_pair_configured": {
            "required": True,
            "failure": "candidate not generated",
        },

        "travel_time": {
            "rule": (
                "minimum_travel_seconds <= elapsed_seconds "
                "<= maximum_travel_seconds"
            ),
            "failure": "candidate invalid; score = 0",
        },

        "direction": {
            "required_when_configured": True,
            "failure": "candidate invalid; score = 0",
        },

        "shared_sensor": {
            "minimum": 1,
            "failure": "candidate invalid; score = 0",
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

    "competition_semantics": {
        "competitor_definition": (
            "For candidate A<->B, a competitor is another feasible candidate produced in "
            "the same deterministic matching evaluation that shares pass A or shares pass B. "
            "The current candidate itself is excluded."
        ),

        "feasible_competitor": (
            "A competitor must already have passed receiver-pair, travel-time, direction, "
            "and minimum-shared-sensor hard gates. Hard-gate failures cannot penalize another candidate."
        ),

        "comparison_score": (
            "Competition compares capped_score before application of competition_factor."
        ),

        "best_competing_score": (
            "Maximum capped_score among feasible competitors. "
            "There is no best_competing_score when no feasible competitor exists."
        ),

        "score_margin": (
            "capped_score - best_competing_score when a competitor exists."
        ),

        "tie_breaking": (
            "Candidate persistence/order uses deterministic IDs. "
            "Tie ordering never changes numeric competition results."
        ),
    },

    "competition_factors": [
        {
            "condition": "no feasible competitor",
            "factor": 1.00,
        },
        {
            "condition": "score_margin >= 25.0",
            "factor": 1.00,
        },
        {
            "condition": "15.0 <= score_margin < 25.0",
            "factor": 0.95,
        },
        {
            "condition": "8.0 <= score_margin < 15.0",
            "factor": 0.85,
        },
        {
            "condition": "3.0 <= score_margin < 8.0",
            "factor": 0.70,
        },
        {
            "condition": "score_margin < 3.0",
            "factor": 0.50,
        },
    ],

    "algorithm": [
        "Apply hard gates.",
        "Calculate set statistics.",
        "Calculate base_score.",
        "Apply absolute shared-count cap to produce capped_score.",
        "Calculate capped_score for all feasible candidates in the deterministic evaluation universe.",
        "Find feasible competitors sharing pass A or pass B.",
        "Calculate best_competing_score from competitor capped_scores.",
        "Calculate score_margin.",
        "Apply competition_factor.",
        "Clamp final_score to 0..100.",
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
        "a_count": 7,
        "b_count": 5,
        "union_count": 7,
        "overlap_coefficient": 1.0,
        "jaccard": 0.7142857143,
        "containment_a": 0.7142857143,
        "containment_b": 1.0,
        "shared_count_strength": 0.8333333333,

        "expected_base_score_approx": 89.29,
        "expected_confidence_without_competition": "very_strong",
    },

    "hard_rules": [
        "Zero shared sensors scores 0.",
        "One shared sensor can never score above 19.",
        "Two shared sensors can never score above 49.",
        "Three shared sensors can never be very_strong.",
        "Duplicate packets never increase shared_count.",
        "Packet frequency is reception evidence, not independent identity evidence.",
        "Different canonical namespaces do not intersect merely because raw IDs match.",
        "Travel-time feasibility is a gate, not a positive bonus.",
        "Direction feasibility is a gate when configured.",
        "Invalid candidates cannot act as competitors.",
        "Candidate input order cannot change numeric results.",
    ],

    "required_debug_output": [
        "match_id",
        "pass_a_id",
        "pass_b_id",
        "receiver_a_id",
        "receiver_b_id",
        "shared_sensor_identities",
        "shared_count",
        "a_count",
        "b_count",
        "union_count",
        "jaccard",
        "overlap_coefficient",
        "containment_a",
        "containment_b",
        "shared_count_strength",
        "elapsed_seconds",
        "minimum_travel_seconds",
        "maximum_travel_seconds",
        "time_feasible",
        "direction_feasible",
        "base_score",
        "absolute_overlap_cap",
        "capped_score",
        "competing_candidate_count",
        "best_competing_score",
        "score_margin",
        "competition_factor",
        "final_score",
        "confidence_label",
        "matcher_version",
    ],
},

# =========================================================================
# REPLAY MANIFEST
# =========================================================================

"replay_manifest": {
    "purpose": (
        "Every derivation run must be reproducible from an explicit manifest."
    ),

    "required_fields": [
        "run_id",
        "source_event_set identity/reference",
        "event_schema_version",
        "receiver_config_snapshot_id",
        "receiver_link_config_snapshot_id",
        "canonicalization_version",
        "canonicalization_config_snapshot_id",
        "clustering_version",
        "clustering_config_snapshot_id",
        "matcher_version",
        "matcher_config identity",
        "track_builder_version optional",
        "track_builder_config_snapshot_id optional",
        "clock_time_basis",
        "experiment_config_snapshot_id optional",
        "created_at",
    ],

    "rule": (
        "Historical replay must resolve these exact versions. "
        "Using newer versions creates a comparison run, not a replacement for the original run."
    ),
},

# =========================================================================
# STRUCTURED DIAGNOSTICS
# =========================================================================

"diagnostics_contract": {
    "starts_in_phase": 1,

    "principle": (
        "Structured failure categories begin with the core engine. "
        "Phase 12 later consolidates them into the full operations/health surface."
    ),

    "initial_categories": [
        "GROUNDVIEW_INGEST_PARSE_ERROR",
        "GROUNDVIEW_EVENT_IDENTITY_ERROR",
        "GROUNDVIEW_UNKNOWN_PROTOCOL",
        "GROUNDVIEW_NORMALIZATION_ERROR",
        "GROUNDVIEW_STORAGE_ERROR",
        "GROUNDVIEW_CANONICALIZATION_ERROR",
        "GROUNDVIEW_CLUSTER_ERROR",
        "GROUNDVIEW_MATCH_ERROR",
        "GROUNDVIEW_CONFIG_VERSION_ERROR",
        "GROUNDVIEW_CLOCK_QUALITY_WARNING",
        "GROUNDVIEW_REPLAY_VERSION_MISSING",
        "GROUNDVIEW_PROVENANCE_VIOLATION",
    ],

    "rules": [
        "Diagnostics do not mutate evidence.",
        "Errors identify the earliest failing layer where practical.",
        "Unknown protocol is not automatically an error.",
        "Expected FIELD_VALIDATION_REQUIRED conditions are not represented as software failures.",
    ],
},

# =========================================================================
# FAILURE / ROLLBACK BEHAVIOR
# =========================================================================

"failure_recovery": {
    "principle": (
        "Repair the earliest responsible abstraction. "
        "Do not accumulate downstream workarounds around a known-invalid upstream contract."
    ),

    "on_failed_assumption": [
        "Stop work that directly depends on the failed assumption.",
        "Record the failure and affected phases in GROUNDVIEW_STATUS.md.",
        "Identify the earliest abstraction responsible.",
        "Repair that abstraction.",
        "Invalidate previously passed dependent phase gates.",
        "Rerun the responsible gate.",
        "Rerun all affected dependent gates.",
        "Continue automatically when authoritative project rules remain satisfied.",
    ],

    "continue_automatically_when": [
        "The issue is an ordinary repository-native implementation choice.",
        "A test failure has an unambiguous GroundView-local repair.",
        "A suggested filename/path differs from repository convention.",
        "A field-dependent constant can remain configured and FIELD_VALIDATION_REQUIRED.",
    ],

    "pause_current_phase_when": [
        "Continuing would persist derived/inferred state against a known-invalid upstream abstraction.",
        "A required credential is unavailable.",
        "A destructive Git or deployment action would be required.",
    ],

    "architectural_contradiction_when": (
        "Two authoritative requirements cannot both be satisfied after inspecting the "
        "actual repository. Record the exact requirements, repository evidence, and smallest "
        "possible resolution. Do not silently choose one."
    ),
},

# =========================================================================
# PHASE COMPLETION POLICY
# =========================================================================

"phase_completion_policy": {
    "rule": (
        "A phase is never complete merely because files exist or a happy path runs."
    ),

    "software_complete_requires": [
        "all software work not requiring physical empirical evidence",
        "phase exit gate passing",
        "affected existing SkyView regressions passing",
        "GROUNDVIEW_STATUS.md updated",
        "known incomplete empirical work explicitly listed",
    ],

    "field_validation_required_means": (
        "Software infrastructure is complete and testable with fixtures/replay, but one or "
        "more physical-world empirical claims remain unverified. "
        "This is not a software failure and must not be represented as empirical success."
    ),

    "blocked_means": (
        "A required software dependency, credential, destructive-action approval, or genuine "
        "architectural contradiction prevents safe continuation."
    ),

    "complete_means": (
        "All software gates are satisfied and all empirical validation specifically required "
        "for that phase's COMPLETE state has been performed."
    ),
},

# =========================================================================
# PHASE DEPENDENCIES
# =========================================================================

"phase_dependencies": {
    "phase_0_repository_hygiene": [],

    "foundation_contract": [
        "phase_0_repository_hygiene",
    ],

    "phase_1_core_observation_engine": [
        "phase_0_repository_hygiene",
        "foundation_contract",
    ],

    "phase_2_groundview_globe_layer": [
        "phase_1_core_observation_engine",
    ],

    "phase_3_track_chaining": [
        "phase_1_core_observation_engine",
    ],

    "phase_4_receiver_node_protocol": [
        "phase_1_core_observation_engine",
    ],

    "phase_5_rf_capture_and_decoder_lab": [
        "phase_1_core_observation_engine",
    ],

    "phase_6_field_experiment_system": [
        "phase_1_core_observation_engine",
    ],

    "phase_7_camera_observation_layer": [
        "phase_1_core_observation_engine",
    ],

    "phase_8_visual_semantic_identity": [
        "phase_7_camera_observation_layer",
    ],

    "phase_9_multimodal_binding": [
        "phase_1_core_observation_engine",
        "phase_8_visual_semantic_identity",
    ],

    "phase_10_receiver_federation_foundation": [
        "phase_4_receiver_node_protocol",
    ],

    "phase_11_historical_query_and_playback": [
        "phase_3_track_chaining",
    ],

    "phase_12_operations_and_health": [
        "phase_4_receiver_node_protocol",
        "phase_10_receiver_federation_foundation",
    ],

    "phase_13_matcher_calibration_framework": [
        "phase_1_core_observation_engine",
    ],

    "phase_14_groundview_product_surface": [
        "phase_2_groundview_globe_layer",
        "phase_3_track_chaining",
        "phase_11_historical_query_and_playback",
    ],
},

"critical_paths": {
    "core_groundview": [
        "phase_0_repository_hygiene",
        "foundation_contract",
        "phase_1_core_observation_engine",
        "phase_3_track_chaining",
        "phase_11_historical_query_and_playback",
        "phase_14_groundview_product_surface",
    ],

    "receiver_network": [
        "phase_1_core_observation_engine",
        "phase_4_receiver_node_protocol",
        "phase_10_receiver_federation_foundation",
        "phase_12_operations_and_health",
    ],

    "visual_identity": [
        "phase_1_core_observation_engine",
        "phase_7_camera_observation_layer",
        "phase_8_visual_semantic_identity",
        "phase_9_multimodal_binding",
    ],
},

"phase_execution_rule": (
    "Phase numbers are the preferred human traversal order, not permission to ignore "
    "actual dependencies. A phase may begin when every dependency and required upstream "
    "gate has passed. Independent phases may proceed in parallel. "
    "Do not let a later phase patch around a failed earlier abstraction. "
    "Proceed through all software-buildable work without waiting for physical RF field data. "
    "For empirically unknowable portions, implement interfaces, configuration, snapshots, "
    "fixtures, measurement, reporting, tests, and replay support, then mark only the "
    "empirical claim FIELD_VALIDATION_REQUIRED."
),

# =========================================================================
# PHASES
# =========================================================================

"phases": {

    # ---------------------------------------------------------------------
    # PHASE 0 — REPOSITORY SAFETY AND INTEGRATION RECONNAISSANCE
    # ---------------------------------------------------------------------

    "phase_0_repository_hygiene": {
        "goal": (
            "Create a safe isolated GroundView development environment and establish "
            "the actual repository-native integration map before modifying GroundView code."
        ),

        "actions": [
            "Inspect repository, branch, worktree, remotes, HEAD, recent branch ancestry, and dirty files without modifying them.",
            "Identify the actual approved SkyView production baseline from repository evidence.",
            "Verify whether the expected chrome baseline 6e67a6b is still the correct GroundView base before acting on it.",
            "Identify existing provider, API middleware, .gev-cache, Cesium entity lifecycle, layer-state, selection, data-credit, and test conventions.",
            "Record repository integration facts in GROUNDVIEW_STATUS.md.",
            "If unrelated dirty work exists, preserve it non-destructively before creating wip/groundview.",
            "Create/use local-only wip/mabeline-layers only when it correctly represents existing dirty Mabeline work.",
            "Do not discard, reset, overwrite, force-checkout, or otherwise destroy unrelated local work.",
            "Create wip/groundview from the verified clean approved SkyView baseline.",
            "Verify unrelated dirty files, warehouse bytes, and financial/ changes are absent from GroundView work.",
            "Copy the authoritative GroundView spec into EARTH research notes as readable markdown while retaining the RTF.",
            "Run existing practical SkyView baseline test/lint/build commands and record results.",
        ],

        "repository_integration_map_required": [
            "provider entry points",
            "API middleware pattern",
            "local cache/storage pattern",
            "Cesium entity creation/update/removal lifecycle",
            "layer-state pattern",
            "selection/pick pattern",
            "data-credit pattern",
            "existing test commands",
            "hosted-unavailable pattern",
        ],

        "exit_gate": [
            "correct repository identified",
            "working branch isolated",
            "approved baseline verified",
            "no destructive reset occurred",
            "existing unrelated work preserved",
            "baseline tests/build status recorded",
            "repository integration map recorded in GROUNDVIEW_STATUS.md",
        ],

        "failure_rule": (
            "If named baseline or dirty-state assumptions are false, do not improvise "
            "destructive Git repair. Record the mismatch and stop only the unsafe operation."
        ),
    },

    # ---------------------------------------------------------------------
    # FOUNDATION GATE — BEFORE PHASE 1 DEPENDENTS
    # ---------------------------------------------------------------------

    "foundation_contract_gate": {
        "goal": (
            "Freeze the minimal cross-cutting contracts whose later retrofit would have "
            "the largest blast radius."
        ),

        "required_before_phase_1_dependents": [
            "groundview_event_v1 source-event envelope",
            "stable source-event identity",
            "single RF normalizer",
            "GroundView storage boundary",
            "deterministic ID construction",
            "deterministic ordering",
            "config snapshot rules",
            "clock/time provenance",
            "groundview_canonical_v1",
            "groundview_cluster_v1",
            "groundview_match_v1 exact competition semantics",
        ],

        "verification": [
            "rtl_433 fixture adapter feeds normalize_event",
            "synthetic receiver-node envelope feeds the same normalize_event",
            "both adapters produce equivalent normalized RF evidence for equivalent payloads",
            "canonicalization can be rebuilt under two versions without mutating observed evidence",
            "replay twice into clean derived state yields identical deterministic IDs/order",
        ],

        "done_when": (
            "Phase 1 can implement features without making new foundational identity, "
            "normalization, storage, or versioning decisions ad hoc."
        ),
    },

    # ---------------------------------------------------------------------
    # PHASE 1 — CORE OBSERVATION ENGINE
    # ---------------------------------------------------------------------

    "phase_1_core_observation_engine": {
        "goal": (
            "Implement the complete deterministic replayable RF observation → canonical "
            "identity projection → pass → fingerprint → cross-receiver matching pipeline."
        ),

        "build": [
            "Receiver configuration model and snapshotting.",
            "Receiver-link configuration model and snapshotting.",
            "groundview_event_v1 adapters.",
            "rtl_433 NDJSON adapter.",
            "Synthetic receiver-node event adapter.",
            "Single RF normalize_event implementation.",
            "Immutable RF observation storage.",
            "Versioned groundview_canonical_v1 identity projection.",
            "groundview_cluster_v1.",
            "Composite RF fingerprints.",
            "groundview_match_v1.",
            "Competition-aware deterministic candidate ranking.",
            "Replay manifest.",
            "Replay tooling.",
            "JSON/CSV/debug reporting.",
            "Initial structured diagnostics.",
        ],

        "api": [
            "GET/POST GroundView receivers using repository-native API convention",
            "GET GroundView observations",
            "GET GroundView passes",
            "GET GroundView fingerprints",
            "GET GroundView matches",
            "POST GroundView replay",
        ],

        "ingest_tests": [
            "malformed NDJSON does not partially create an observation",
            "missing optional RF fields remain valid",
            "missing required event identity/timestamp fails explicitly",
            "timestamp timezone and precision parsing",
            "frequency survives envelope → normalization → persistence → replay unchanged",
            "exact source-event retry remains one observation",
            "equal payload with distinct source-event identity remains two observations",
            "same sequence number under different receiver IDs does not collide",
            "unknown protocol retained",
        ],

        "canonical_identity_tests": [
            "same raw ID + same namespace = same canonical identity",
            "same raw ID + different protocol namespace != same identity",
            "missing model follows explicit groundview_canonical_v1 rule",
            "canonical v1 and v2 fixture projections can coexist from unchanged observation",
            "recomputing canonical identity never mutates raw observation",
        ],

        "clustering_tests": [
            "one truck pass",
            "two close truck passes",
            "sparse long pass behavior according to v1 semantics",
            "exact 30-second boundary",
            "30s minus epsilon",
            "30s plus epsilon",
            "duplicate ingest versus legitimate repeated sensor transmissions",
            "equal timestamps use deterministic secondary ordering",
            "random arrival order yields identical clusters",
            "unknown noncanonicalizable evidence remains stored",
        ],

        "matcher_tests": [
            "canonical 89.29 case",
            "zero overlap",
            "exactly 1 shared sensor",
            "exactly 2 shared sensors",
            "exactly 3 shared sensors",
            "exactly 4 shared sensors",
            "exactly 5 shared sensors",
            "cap boundaries 19/49/69/84/100",
            "confidence threshold boundaries",
            "pure subset containment with lower Jaccard",
            "travel-time hard-gate failure",
            "direction hard-gate failure",
            "near-tied competitor",
            "clearly inferior competitor",
            "competitor sharing only pass A",
            "competitor sharing only pass B",
            "unrelated candidate is not competitor",
            "exact competition tie",
            "candidate insertion order does not alter score",
            "invalid-time candidate cannot penalize another candidate",
            "invalid-direction candidate cannot penalize another candidate",
        ],

        "rebuild_tests": [
            "delete every derived/inferred artifact and regenerate equivalent state",
            "replay same evidence twice into clean derived state gives same IDs/order",
            "shuffled source-file order gives same derived state",
            "old config snapshot reproduces old result after current config changes",
            "missing historical algorithm version fails loudly",
        ],

        "provenance_tests": [
            "OBSERVED RF record cannot serialize canonical identity as observed truth",
            "INFERRED match cannot serialize as OBSERVED or DERIVED",
            "clock-corrected time remains distinguishable from receiver time",
        ],

        "exit_gate": [
            "foundation contract remains satisfied",
            "immutable evidence tests pass",
            "deterministic IDs pass",
            "malformed ingest tests pass",
            "unknown protocol retained",
            "namespace-collision tests pass",
            "groundview_cluster_v1 suite passes",
            "canonical 89.29 matcher result passes",
            "all matcher cap/confidence/competition boundaries pass",
            "replay-from-empty is deterministic",
            "existing affected SkyView tests remain green",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 2 — NATIVE SKYVIEW GLOBE LAYER
    # ---------------------------------------------------------------------

    "phase_2_groundview_globe_layer": {
        "goal": (
            "Make GroundView a native Mabeline/SkyView globe layer while preserving "
            "truthfulness and existing Cesium lifecycle behavior."
        ),

        "build": [
            "GROUNDVIEW control under The Mabeline Project.",
            "Receivers sub-layer.",
            "Truck Passes sub-layer.",
            "Matches sub-layer.",
            "Layer-state registration.",
            "GroundView data credit.",
            "Cesium receiver entities.",
            "Receiver selection information.",
            "Pass selection at receiver position.",
            "Inferred match relation/polyline.",
            "Visible provenance.",
        ],

        "display_rules": {
            "receiver": "actual configured WGS84 receiver location",

            "pass": (
                "receiver/site location representing RF coverage observation, "
                "not an exact truck coordinate"
            ),

            "match": (
                "inferred relationship between observations, not a measured driven path"
            ),

            "never": [
                "invented truck GPS",
                "lane-level coordinate not observed",
                "interpolated route rendered as observation",
                "confirmed label",
            ],
        },

        "selection_fields": [
            "receiver",
            "pass time",
            "sensor count",
            "shared sensor count",
            "set sizes",
            "overlap coefficient",
            "Jaccard",
            "elapsed time",
            "base score",
            "competition factor",
            "final score",
            "confidence",
            "provenance",
            "matcher version",
        ],

        "lifecycle_tests": [
            "GroundView disabled before initialization leaves baseline unchanged",
            "enable/disable repeatedly",
            "replay while GroundView layer disabled",
            "repeated replay does not leak entities",
            "entity count returns to expected state after disable/cleanup",
            "pass pick resolves only to receiver/site position",
            "match API/frontend exposes no fabricated intermediate coordinates",
            "selection reads provenance from persisted GroundView state",
        ],

        "exit_gate": [
            "GroundView disabled equals baseline behavior",
            "repeated toggle/replay produces no Cesium entity leak",
            "only actual receiver coordinates are represented as physical observations",
            "provenance visible in selection",
            "no inferred GPS",
            "existing SkyView regression suite remains green",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 3 — TEMPORARY ROAD-UNIT TRACK CHAINING
    # ---------------------------------------------------------------------

    "phase_3_track_chaining": {
        "goal": (
            "Chain compatible pairwise matches into temporary episode-bounded road-unit tracks."
        ),

        "version": "groundview_track_v1",

        "rules": [
            "Do not create permanent truck IDs.",
            "Track identity is bounded to one observation episode.",
            "Track contains deterministic ordered pass IDs and match IDs.",
            "Every edge retains its individual matcher evidence.",
            "Track summary cannot hide a weak constituent edge.",
            "Track exposes weakest-link score.",
            "Reject impossible chronology.",
            "Reject receiver-order violations.",
            "Preserve forks when evidence is ambiguous rather than forcing one path.",
        ],

        "initial_scoring": {
            "weakest_link_score": "min(edge final_score)",
            "mean_edge_score": "mean(edge final_score)",
            "rule": (
                "Do not create another opaque identity score in v1."
            ),
        },

        "deterministic_track_identity": (
            "Track ID derives from bounded episode membership, deterministic ordered pass/match IDs, "
            "and track_builder_version."
        ),

        "tests": [
            "A → B → C valid chain",
            "A → C impossible chronology",
            "ambiguous B alternatives create fork",
            "weak middle edge retained visibly",
            "missing middle receiver",
            "out-of-order source arrival rebuilds same track",
            "deterministic track rebuild",
            "no permanent vehicle identifier emitted",
        ],

        "exit_gate": [
            "valid multi-receiver chain works",
            "forks preserved",
            "chronology violations rejected",
            "track IDs deterministic",
            "no permanent vehicle identity serialized or exposed",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 4 — RECEIVER NODE PROTOCOL
    # ---------------------------------------------------------------------

    "phase_4_receiver_node_protocol": {
        "goal": (
            "Complete the live receiver-node protocol around the already-established "
            "groundview_event_v1 contract."
        ),

        "important_boundary": (
            "Phase 4 does not invent the source-event envelope. "
            "The minimal event contract and one-normalizer rule already exist before Phase 1."
        ),

        "receiver_event_envelope": "groundview_event_v1",

        "build": [
            "Authenticated receiver ingest interface.",
            "Batch event upload.",
            "Idempotency handling.",
            "Sequence handling.",
            "Clock-drift/quality metadata.",
            "Receiver heartbeat model.",
            "Receiver software version reporting.",
            "Receiver capability reporting.",
            "Per-band status.",
            "Local spool/retry interface specification.",
            "Replay of real receiver-node envelopes.",
            "Receiver quarantine behavior.",
        ],

        "security_boundary": [
            "No public anonymous receiver write endpoint.",
            "Local development mode may use an explicit development-only bypass.",
            "Development bypass must not silently become hosted anonymous-write behavior.",
        ],

        "network_tests": [
            "live-node envelope and replay envelope converge on same normalizer",
            "duplicate batch upload remains idempotent",
            "repeated event sequence does not duplicate observation",
            "partial batch failure and retry",
            "out-of-order batches",
            "clock metadata retained",
            "receiver quarantine behavior",
            "anonymous hosted write rejected",
        ],

        "exit_gate": [
            "same normalizer used for replay and live nodes",
            "duplicate/retry ingest idempotent",
            "clock metadata retained",
            "development bypass isolated",
            "anonymous nonlocal write rejected",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 5 — RF CAPTURE / DECODER LAB
    # ---------------------------------------------------------------------

    "phase_5_rf_capture_and_decoder_lab": {
        "goal": (
            "Build tooling for unsupported commercial-truck TPMS protocols without "
            "creating another GroundView RF domain model."
        ),

        "targets": [
            "Bendix commercial TPMS family",
            "LDL commercial TPMS family",
            "current Volvo/Mack wheel sensors",
            "Schrader commercial variants",
            "TST/EezTire-compatible aftermarket",
            "truck-oriented 915 MHz systems",
            "unknown observed protocols",
        ],

        "build": [
            "Raw IQ capture references.",
            "Pulse capture references.",
            "Raw bitstream references.",
            "Decoder provenance/version metadata.",
            "Protocol sample catalog.",
            "Capture annotation format.",
            "Protocol fixture directory.",
            "Decoder regression-test interface.",
            "Unknown-signal inventory report.",
        ],

        "decoder_contract": {
            "required_output_when_known": [
                "protocol namespace",
                "sensor ID",
                "timestamp",
                "frequency",
            ],

            "optional_output": [
                "pressure",
                "temperature",
                "battery",
                "flags",
            ],

            "hard_rule": (
                "Every custom decoder output must enter through a groundview_event_v1 adapter "
                "and the same normalize_event path as rtl_433. "
                "A custom decoder must not create a second RF observation schema."
            ),
        },

        "exit_gate": [
            "known decoder fixture enters normalizer through common event path",
            "unknown captures remain preserved evidence",
            "decoder version/provenance retained",
            "capture provenance retained",
            "no custom decoder domain fork",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 6 — FIELD EXPERIMENT SYSTEM
    # ---------------------------------------------------------------------

    "phase_6_field_experiment_system": {
        "goal": (
            "Turn GroundView into an experiment platform capable of measuring whether "
            "real highway RF fingerprinting works without requiring field evidence to "
            "complete the software foundation."
        ),

        "experiment_model": {
            "fields": [
                "experiment_run_id",
                "source_event_set/reference",
                "site_snapshot_ids",
                "receiver_config_snapshot_ids",
                "receiver_link_config_snapshot_id",
                "clock_metadata_snapshot",
                "canonicalization_version/config",
                "clustering_version/config",
                "matcher_version/config",
                "ground_truth_annotation_ref optional",
                "started_at",
                "ended_at",
                "notes",
            ],
        },

        "metrics": [
            "total RF packets",
            "unique raw sensor IDs",
            "unique canonical sensor identities",
            "estimated truck passes",
            "sensor identities per pass",
            "packets per pass",
            "RF dwell duration",
            "protocol distribution",
            "frequency distribution",
            "RSSI distribution",
            "SNR distribution",
            "missing-sensor rate when ground truth exists",
            "downstream shared-sensor count",
            "overlap coefficient distribution",
            "Jaccard distribution",
            "candidate ambiguity rate",
            "score-margin distribution",
            "receiver-to-receiver recognition rate when ground truth exists",
            "false candidate rate when ground truth exists",
            "receiver placement effect when comparable runs exist",
        ],

        "build": [
            "Experiment-run storage.",
            "Immutable experiment config snapshot.",
            "Immutable site/receiver snapshot references.",
            "Metrics computation.",
            "Per-run JSON report.",
            "Per-run CSV export.",
            "Comparison between experiment runs.",
            "Matcher-threshold analysis report without mutating v1.",
            "Protocol coverage report.",
            "Ground-truth annotation reference hook.",
        ],

        "software_done_when": (
            "A deterministic two-site fixture experiment can be captured/replayed through the "
            "same experiment model, retains immutable run/config/site snapshots, generates "
            "reproducible JSON/CSV metrics and comparison reports, and can later accept physical "
            "receiver evidence without schema redesign."
        ),

        "field_validation_required": [
            "Class 8 TPMS penetration",
            "real sensors heard per rig",
            "real transmission cadence",
            "real RF range",
            "real protocol distribution",
            "real downstream fingerprint stability",
            "optimal clustering window",
            "optimal receiver spacing",
            "real false-positive rate",
            "real false-negative rate",
            "real score/threshold calibration",
            "real antenna configuration",
        ],

        "field_done_when": (
            "A physical two-site run is captured and analyzed using the already-complete "
            "experiment pipeline. Until then the phase is SOFTWARE_COMPLETE with explicit "
            "FIELD_VALIDATION_REQUIRED items."
        ),

        "hard_rule": (
            "Do not silently change groundview_match_v1 or groundview_cluster_v1 from experiment results. "
            "Changed semantics require a new explicit version."
        ),

        "exit_gate_software": [
            "fixture experiment produces immutable snapshots",
            "metrics reproducible",
            "JSON/CSV reproducible",
            "ground-truth hook exists",
            "empirical claims remain clearly FIELD_VALIDATION_REQUIRED",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 7 — CAMERA OBSERVATION
    # ---------------------------------------------------------------------

    "phase_7_camera_observation_layer": {
        "goal": (
            "Add optional visual observations at GroundView sites without making camera "
            "evidence mandatory for RF tracking."
        ),

        "sources": [
            "GroundView-owned camera",
            "suitable existing SkyView CCTV source",
            "recorded experiment video",
            "recorded still-frame sequence",
        ],

        "build": [
            "Camera-site configuration.",
            "Camera observation model.",
            "Frame/image evidence references.",
            "Truck/tractor-trailer object detection interface.",
            "Object tracking within one camera view.",
            "Timestamp synchronization metadata.",
            "Selection/debug overlay.",
            "Replay fixture support.",
        ],

        "rules": [
            "Camera observations remain independent evidence.",
            "Camera feature can be absent/disabled without affecting RF pipeline.",
            "Do not infer plate/USDOT/carrier identity merely from vehicle detection.",
            "Preserve original image/frame evidence reference when permitted.",
            "Do not require public CCTV for core GroundView operation.",
        ],

        "exit_gate": [
            "camera fixture replays independently",
            "RF pipeline passes with camera absent",
            "timestamps retained",
            "evidence references retained",
            "no camera dependency enters RF matcher",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 8 — VISUAL SEMANTIC IDENTITY
    # ---------------------------------------------------------------------

    "phase_8_visual_semantic_identity": {
        "goal": (
            "Extract optional commercial-vehicle semantic identity candidates from "
            "suitable camera observations."
        ),

        "identity_targets": [
            "USDOT number",
            "carrier name",
            "trade name",
            "tractor/unit number",
            "trailer number",
            "ISO container number",
            "chassis number",
            "logo/livery candidate",
        ],

        "pipeline": [
            "vehicle detection",
            "candidate text regions",
            "OCR",
            "normalization",
            "identifier-format validation",
            "confidence",
            "identity candidate",
        ],

        "rules": [
            "OCR semantic result is INFERRED unless independently verified by another evidence source.",
            "Keep raw OCR text.",
            "Keep normalized candidate value.",
            "Keep OCR/model version.",
            "Keep confidence.",
            "Do not treat visual identity confidence as RF match confidence.",
            "Do not require license-plate recognition.",
            "Do not make semantic identity necessary for road-unit continuity.",
            "RF evidence is never mutated by visual recognition.",
        ],

        "exit_gate": [
            "raw OCR text retained",
            "normalized value retained",
            "recognizer version retained",
            "confidence retained",
            "candidate remains INFERRED",
            "RF state unchanged",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 9 — MULTIMODAL BINDING
    # ---------------------------------------------------------------------

    "phase_9_multimodal_binding": {
        "goal": (
            "Associate camera semantic evidence with an RF truck pass when both occur "
            "at the same physical site and time."
        ),

        "binding_inputs": [
            "RF truck pass",
            "camera observation",
            "visual truck detection",
            "site identity",
            "RF pass time",
            "camera detection time",
            "visual identity candidates",
        ],

        "initial_strategy": {
            "machine_learning": False,

            "factors": [
                "same configured observation site",
                "temporal overlap",
                "camera object timing",
                "RF pass timing",
                "number of competing camera trucks",
                "number of competing RF passes",
            ],

            "rule": (
                "Do not bind semantic identity to an RF pass when multiple simultaneous "
                "trucks make the association materially ambiguous."
            ),
        },

        "exit_gate": [
            "unambiguous synthetic co-observation binds deterministically",
            "ambiguous simultaneous trucks remain ambiguous/unbound",
            "binding deletion leaves RF evidence unchanged",
            "binding is INFERRED",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 10 — RECEIVER FEDERATION FOUNDATION
    # ---------------------------------------------------------------------

    "phase_10_receiver_federation_foundation": {
        "goal": (
            "Build the software foundation for many distributed GroundView receiver nodes "
            "feeding one observation network."
        ),

        "reuse_rule": (
            "Federation composes the Phase 4 receiver-node event, authentication, idempotency, "
            "and central-ingest contracts. It must not create a federation-specific observation "
            "schema, normalizer, or alternate ingestion pipeline."
        ),

        "build": [
            "Receiver registration model.",
            "Receiver capability manifest.",
            "Receiver software version.",
            "Receiver heartbeat/status.",
            "Event batch upload.",
            "Idempotent event ingestion.",
            "Backfill upload.",
            "Clock-quality reporting.",
            "Receiver provenance.",
            "Receiver disable/quarantine state.",
            "Per-receiver ingest metrics.",
        ],

        "not_yet": [
            "public anonymous signup",
            "public crowdsourced production deployment",
            "nationwide production operations",
        ],

        "network_principle": (
            "Every physical observation remains traceable to the receiver that produced it."
        ),

        "exit_gate": [
            "multiple test receiver identities upload through one ingest path",
            "backfill uses same ingest path",
            "retries idempotent",
            "quarantine behavior works",
            "persistence does not rely on ephemeral Vercel writes",
            "no federation-specific normalizer exists",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 11 — HISTORICAL QUERY / PLAYBACK
    # ---------------------------------------------------------------------

    "phase_11_historical_query_and_playback": {
        "goal": (
            "Make GroundView observations and temporary road-unit tracks explorable over time "
            "inside SkyView."
        ),

        "build": [
            "Time-bounded observation queries.",
            "Receiver history queries.",
            "Pass history.",
            "Match history.",
            "Track history.",
            "Replay-window API.",
            "Cesium historical rendering using existing SkyView patterns.",
        ],

        "historical_version_rule": (
            "Historical replay resolves and displays the original algorithm/config versions "
            "that produced persisted results. Recomputing with newer versions creates a separate "
            "comparison run and never replaces or masquerades as the historical result."
        ),

        "rules": [
            "Historical replay preserves original provenance.",
            "Do not create unobserved movement between observations.",
            "If modeled interpolation is ever offered, mark it explicitly modeled and keep it off by default.",
        ],

        "exit_gate": [
            "delete rebuildable state and reproduce equivalent passes/matches/tracks using original versions",
            "original config snapshots reproduce old historical results",
            "newer-version comparison remains separate",
            "visualization fabricates no movement",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 12 — OPERATIONS / HEALTH
    # ---------------------------------------------------------------------

    "phase_12_operations_and_health": {
        "goal": (
            "Consolidate GroundView diagnostics into an operational health surface."
        ),

        "note": (
            "Structured diagnostic categories begin in Phase 1. "
            "This phase consolidates rather than introducing observability."
        ),

        "receiver_health": [
            "last heartbeat",
            "last observation",
            "events per minute",
            "band activity",
            "decoder errors",
            "unknown protocol count",
            "clock status",
            "disk spool status",
            "software version",
        ],

        "central_health": [
            "ingest backlog",
            "observation count",
            "cluster count",
            "match count",
            "match ambiguity",
            "replay errors",
            "storage growth",
        ],

        "build": [
            "GroundView health endpoint.",
            "Structured logs.",
            "Receiver status surface.",
            "Experiment/debug summary.",
            "Repository-native local diagnostics UI when appropriate.",
        ],

        "fault_fixture_gate": [
            "receiver loss surfaces distinctly",
            "clock error surfaces distinctly",
            "decoder failure surfaces distinctly",
            "ingest error surfaces distinctly",
            "clustering failure surfaces distinctly",
            "matcher ambiguity surfaces distinctly",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 13 — MATCHER CALIBRATION FRAMEWORK
    # ---------------------------------------------------------------------

    "phase_13_matcher_calibration_framework": {
        "goal": (
            "Evaluate field-labelled evidence and future matcher versions without "
            "altering authoritative groundview_match_v1."
        ),

        "note": (
            "Phase 6 already reserves ground_truth_annotation_ref in experiment runs. "
            "Phase 13 owns annotation tooling and quantitative evaluation."
        ),

        "build": [
            "Ground-truth annotation tooling/schema implementation.",
            "Known same-road-unit examples.",
            "Known different-road-unit examples.",
            "Precision calculation.",
            "Recall calculation.",
            "Threshold sweep tooling.",
            "Score-component distribution reports.",
            "groundview_match_v1 versus future matcher comparison.",
            "groundview_cluster_v1 versus future clustering comparison where relevant.",
        ],

        "rule": (
            "Do not mutate v1 behavior after calibration. "
            "Changed matching semantics become groundview_match_v2. "
            "Changed clustering semantics become groundview_cluster_v2."
        ),

        "exit_gate": [
            "labelled fixtures produce reproducible precision/recall",
            "threshold sweeps reproducible",
            "v2 candidate can run beside v1",
            "v1 canonical 89.29 regression remains unchanged",
            "stored v1 output remains unchanged",
        ],
    },

    # ---------------------------------------------------------------------
    # PHASE 14 — STABLE GROUNDVIEW PRODUCT SURFACE
    # ---------------------------------------------------------------------

    "phase_14_groundview_product_surface": {
        "goal": (
            "Finish the stable SkyView presentation of GroundView without turning "
            "SkyView into a dedicated truck-tracking dashboard."
        ),

        "surface": [
            "GROUNDVIEW master toggle",
            "receiver visibility",
            "truck-pass visibility",
            "match visibility",
            "temporary track visibility",
            "observation detail",
            "provenance",
            "source/credit",
            "time window",
            "confidence filtering when appropriate",
        ],

        "avoid": [
            "new standalone GroundView application",
            "large new dashboard framework",
            "fake moving truck icons between observations",
            "overstated identity certainty",
            "frontend-owned inference state",
        ],

        "exit_gate": [
            "GroundView off-state equals SkyView baseline",
            "existing SkyView suite green",
            "GroundView suite green",
            "all GroundView provenance rules hold",
            "no fabricated positions",
            "historical and current GroundView state are version-aware",
        ],
    },
},

# =========================================================================
# PHASE EXIT GATE INDEX
# =========================================================================

"phase_exit_gates": {
    "P0": (
        "Correct repository identified; branch isolation verified; no destructive reset; "
        "baseline SkyView tests/status recorded; integration map recorded."
    ),

    "FOUNDATION": (
        "Single source-event envelope; single normalizer; deterministic IDs/order; "
        "storage boundary; config snapshots; time provenance; canonical/cluster/matcher contracts frozen."
    ),

    "P1": (
        "Immutable evidence, deterministic IDs, malformed ingest, unknown protocol retention, "
        "namespace collision, cluster suite, canonical 89.29, every matcher boundary, "
        "competition universe, replay-from-empty determinism, existing SkyView regressions."
    ),

    "P2": (
        "GroundView disabled equals baseline; repeated toggle/replay has no entity leak; "
        "only receiver positions used; provenance visible; no inferred GPS."
    ),

    "P3": (
        "A→B→C, fork, weak edge, impossible chronology, missing middle receiver, "
        "deterministic track rebuild, no permanent vehicle ID."
    ),

    "P4": (
        "Replay and live-node envelopes converge on same normalizer; duplicate/retry ingest "
        "idempotent; clock metadata retained; anonymous nonlocal write rejected."
    ),

    "P5": (
        "Known-decoder fixture enters common normalizer; unknown captures preserved; "
        "decoder/capture provenance retained; no second domain model."
    ),

    "P6": (
        "Fixture experiment creates immutable run/config/site snapshots and reproducible "
        "JSON/CSV metrics; empirical RF claims remain FIELD_VALIDATION_REQUIRED."
    ),

    "P7": (
        "Camera fixture replays independently; RF works without camera; timestamps/evidence retained."
    ),

    "P8": (
        "OCR candidates retain raw text, normalized value, recognizer version, confidence; "
        "candidate remains INFERRED; RF unchanged."
    ),

    "P9": (
        "Unambiguous synthetic binding deterministic; ambiguous simultaneous trucks remain "
        "unbound/ambiguous; binding deletion leaves RF evidence unchanged."
    ),

    "P10": (
        "Multiple test receivers upload/backfill through same ingest path; retries idempotent; "
        "quarantine works; no ephemeral Vercel persistence dependency."
    ),

    "P11": (
        "Derived state can be deleted and rebuilt using exact historical versions/configs; "
        "visualization fabricates no movement."
    ),

    "P12": (
        "Receiver loss, clock error, decoder failure, ingest failure, cluster failure, and "
        "matcher ambiguity surface distinctly."
    ),

    "P13": (
        "Labelled fixtures produce reproducible precision/recall and threshold sweeps; "
        "future version runs beside v1; v1 remains unchanged."
    ),

    "P14": (
        "GroundView off-state equals baseline; provenance rules hold; all affected "
        "SkyView and GroundView tests pass."
    ),
},

# =========================================================================
# API TARGET
# =========================================================================

"api_target": {
    "core": [
        "GET/POST GroundView receivers",
        "GET GroundView observations",
        "GET GroundView passes",
        "GET GroundView fingerprints",
        "GET GroundView matches",
        "GET GroundView tracks",
        "POST GroundView replay",
    ],

    "receiver_node": [
        "POST GroundView node events",
        "POST GroundView node heartbeat",
        "GET GroundView node config if repository architecture warrants it",
    ],

    "camera": [
        "GET GroundView cameras",
        "GET GroundView camera observations",
        "GET GroundView visual identities",
        "GET GroundView bindings",
    ],

    "experiments": [
        "GET GroundView experiments",
        "POST GroundView experiment replay",
        "GET GroundView experiment report",
    ],

    "health": [
        "GET GroundView health",
    ],

    "instruction": (
        "Use repository-native local-provider/Vite middleware conventions. "
        "Conceptual route names do not override a clearly established SkyView API pattern."
    ),
},

# =========================================================================
# SKYVIEW INTEGRATION
# =========================================================================

"skyview_integration": {
    "parent_section": "THE MABELINE PROJECT",
    "layer_name": "GROUNDVIEW",

    "controls": [
        "GROUNDVIEW ON/OFF",
        "RECEIVERS",
        "TRUCK PASSES",
        "MATCHES",
        "TRACKS when Phase 3 is available",
    ],

    "receiver_rendering": {
        "geometry": "configured WGS84 receiver position",
        "selectable": True,
    },

    "truck_pass_rendering": {
        "position": "receiver position or existing honest observation-area representation",

        "rule": (
            "A pass means a road unit was inferred from RF evidence in receiver coverage. "
            "It does not mean the road unit occupied the exact receiver coordinates."
        ),
    },

    "match_rendering": {
        "representation": (
            "Existing SkyView-compatible relation/polyline between observation sites."
        ),

        "rule": (
            "The line visualizes an inferred relationship. "
            "It is not a measured or interpolated driven path."
        ),
    },

    "track_rendering": {
        "representation": (
            "Ordered relation segments between observed receiver sites."
        ),

        "rule": (
            "Do not animate or interpolate a vehicle between sites as if continuously observed."
        ),
    },

    "selection_required_fields": [
        "provenance",
        "receiver/site",
        "time",
        "sensor count",
        "shared count when match",
        "overlap coefficient when match",
        "Jaccard when match",
        "elapsed time when match",
        "base score when match",
        "competition factor when match",
        "final score when match",
        "confidence when match",
        "algorithm versions",
    ],

    "credit": (
        "GroundView TPMS RF / rtl_433 where applicable, with GroundView "
        "OBSERVED / DERIVED / INFERRED provenance."
    ),

    "design_rule": (
        "Use existing SkyView visual language. "
        "Do not create a new design system."
    ),
},

# =========================================================================
# REPLAY
# =========================================================================

"replay": {
    "principle": (
        "Every important GroundView derivation/inference must be reproducible without hardware."
    ),

    "pipeline": [
        "adapt source event",
        "normalize",
        "canonicalize",
        "cluster",
        "fingerprint",
        "match",
        "track",
        "bind optional camera evidence",
        "report",
    ],

    "required_properties": [
        "deterministic",
        "version-aware",
        "config-snapshot-aware",
        "multi-receiver",
        "out-of-order-source tolerant",
        "unknown-protocol tolerant",
        "partial-capture tolerant",
    ],

    "outputs": [
        "console debug summary",
        "JSON",
        "CSV",
    ],

    "determinism_rule": (
        "Identical evidence plus identical manifest/config/version inputs must produce "
        "deterministically equivalent IDs, ordering, and outputs."
    ),
},

# =========================================================================
# SYNTHETIC FIXTURES
# =========================================================================

"synthetic_fixtures": {
    "two_receiver_core": {
        "receiver_A": {
            "truck_1": ["A", "B", "C", "D", "E", "F", "G"],
            "truck_2": ["J", "K", "L", "M"],
        },

        "receiver_B": {
            "truck_1": ["A", "B", "D", "E", "F"],
            "truck_2": ["J", "L", "M"],
        },
    },

    "must_also_cover": [
        "unrelated traffic",
        "single-ID coincidence",
        "two-ID match",
        "near-tied competitor",
        "competitor sharing only A",
        "competitor sharing only B",
        "unrelated candidate",
        "travel-window miss",
        "direction miss",
        "duplicate ingest",
        "legitimate repeated sensor transmission",
        "out-of-order arrival",
        "equal timestamps",
        "unknown protocol",
        "same raw ID in different namespaces",
        "missing optional fields",
        "same payload distinct source-event IDs",
        "receiver-node envelope equivalent to recorded rtl_433 input",
    ],
},

# =========================================================================
# FIELD VALIDATION BOUNDARY
# =========================================================================

"field_validation_boundary": {
    "implement_now": [
        "configuration",
        "versioning",
        "capture interfaces",
        "receiver-node event protocol",
        "measurement",
        "experiment manifests",
        "metrics",
        "reporting",
        "ground-truth hooks",
        "calibration tooling",
        "comparison tooling",
        "replay",
        "tests",
    ],

    "do_not_fabricate": [
        "Class 8 TPMS penetration",
        "sensor IDs heard per real rig",
        "real transmission cadence",
        "real RF range",
        "real protocol distribution",
        "real optimal clustering window",
        "real optimal receiver spacing",
        "real false-positive rate",
        "real false-negative rate",
        "real matcher calibration",
        "real antenna configuration",
    ],

    "rule": (
        "Software may be SOFTWARE_COMPLETE while these empirical questions remain "
        "FIELD_VALIDATION_REQUIRED."
    ),
},

# =========================================================================
# HOSTED / DEPLOYMENT POLICY
# =========================================================================

"deployment": {
    "local_first": True,

    "vercel": {
        "new_project": False,
        "production_deploy": False,

        "future_policy": (
            "If GroundView frontend code is later approved for hosted earth before durable "
            "receiver infrastructure exists, mutating GroundView routes must be unavailable/"
            "stubbed using the existing hosted-unavailable pattern."
        ),
    },

    "long_lived_services": (
        "Do not prematurely choose production receiver hosting. "
        "Keep interfaces suitable for future durable ingest outside Vercel."
    ),
},

# =========================================================================
# CURSOR AUTONOMY
# =========================================================================

"cursor_autonomy": {
    "may_decide": [
        "Exact filenames when repository conventions clearly dictate better names.",
        "Import boundaries.",
        "Helper decomposition.",
        "Serialization helper structure.",
        "Error-class organization.",
        "Test helper organization.",
        "Repository-native API path details.",
        "Cesium primitive/entity implementation consistent with existing lifecycle.",
        "Local serialization format hidden behind GroundView storage contract.",
        "Fixture loader implementation.",
        "Temporary mocks.",
        "Camera provider adapters.",
        "UI spacing/icon reuse.",
        "Parallel implementation of independent post-P1 phases whose prerequisites are satisfied.",
        "GroundView-owned refactoring required to repair the earliest responsible abstraction.",
    ],

    "must_not_alter": [
        "groundview_match_v1 semantics",
        "matcher weights",
        "shared_count_strength formula",
        "absolute overlap caps",
        "competition factors",
        "competition universe",
        "confidence thresholds",
        "forbidden confirmed label",
        "OBSERVED / DERIVED / INFERRED truth model",
        "road-unit v1 definition",
        "no-fake-GPS rule",
        "no-FMCSA-core-dependency rule",
        "GroundView-inside-SkyView requirement",
        "no-production-Vercel-deploy rule",
        "raw observation immutability",
        "previously persisted algorithm-version semantics",
        "historical v1 outputs",
        "evidence provenance",
        "receiver coordinates/timestamps/signal values by fabrication",
        "empirical RF claims without field evidence",
        "major database migration merely by preference",
        "single RF ingest/normalization path",
        "camera optionality for RF tracking",
        "temporary-track-not-permanent-vehicle semantics",
        "destructive Git action because repository assumptions differ",
    ],
},

# =========================================================================
# NON-GOALS / FORBIDDEN SHORTCUTS
# =========================================================================

"non_goals": [
    "No second SkyView application.",
    "No automatic production deployment.",
    "No fake truck GPS.",
    "No confirmed TPMS identity label.",
    "No FMCSA dependency for core GroundView tracking.",
    "No requirement to resolve legal carrier identity.",
    "No requirement to split tractor/trailer for road-unit tracking.",
    "No mandatory license-plate recognition.",
    "No opaque ML matcher.",
    "No path interpolation presented as observed evidence.",
    "No premature nationwide public receiver signup.",
    "No uncontrolled warehouse writes.",
    "No federation-specific normalizer.",
    "No custom-decoder-specific GroundView domain model.",
    "No camera requirement for RF matching.",
    "No frontend-owned GroundView truth.",
],

# =========================================================================
# PREFERRED BUILD TRAVERSAL
# =========================================================================

"preferred_build_order": [
    "Phase 0 — repository safety and reconnaissance",
    "Foundation Contract Gate",
    "Phase 1 — core RF observation engine",
    "Phase 2 — native GroundView globe layer",
    "Phase 3 — temporary multi-receiver track chaining",
    "Phase 4 — receiver node protocol",
    "Phase 5 — RF capture/decoder lab",
    "Phase 6 — field experiment system",
    "Phase 7 — camera observation layer",
    "Phase 8 — visual semantic identity",
    "Phase 9 — multimodal RF/camera binding",
    "Phase 10 — receiver federation foundation",
    "Phase 11 — historical query/playback",
    "Phase 12 — operations/health",
    "Phase 13 — matcher calibration framework",
    "Phase 14 — stable GroundView product surface",
],

# =========================================================================
# COMPLETION REPORT
# =========================================================================

"completion_report": {
    "style": "short engineering report",

    "include": [
        "phases attempted",
        "phases whose gates passed",
        "phases SOFTWARE_COMPLETE",
        "FIELD_VALIDATION_REQUIRED items",
        "blocked items",
        "files changed",
        "new domain models",
        "new API routes",
        "storage implementation",
        "event-schema implementation path",
        "canonicalization implementation path",
        "clustering implementation path",
        "matcher implementation path",
        "replay commands",
        "test commands",
        "test results",
        "canonical 89.29 actual result",
        "how to enable GROUNDVIEW locally",
        "GROUNDVIEW_STATUS.md current resume point",
    ],

    "do_not_include": [
        "research-paper prose",
        "background explanation of TPMS",
        "background explanation of SkyView",
        "restatement of the full project brief",
    ],
},

# =========================================================================
# EXECUTION DIRECTIVE
# =========================================================================

"execute": (
    "Implement GroundView across these dependency-gated phases in the existing SkyView repository. "
    "Begin with non-destructive Phase 0 repository reconnaissance and create/update "
    "GROUNDVIEW_STATUS.md before substantial implementation. "
    "Establish the Foundation Contract before Phase 1 dependent code. "
    "The specified truth model, raw-evidence immutability, source-event convergence, "
    "groundview_canonical_v1 boundary, groundview_cluster_v1 semantics, groundview_match_v1 "
    "formula/caps/competition/confidence behavior, Git/Vercel constraints, deterministic "
    "rebuild rules, historical-version rules, and no-fake-GPS requirements are authoritative. "
    "Build all software foundations that can be built now. "
    "Use deterministic fixtures and replay wherever physical observations are unavailable. "
    "Do not stop for ordinary repository-native design decisions. "
    "If an upstream assumption fails, repair the earliest responsible abstraction, invalidate "
    "dependent gates, rerun them, and continue. "
    "Only pause for a destructive action, unavailable required credential, or genuine "
    "architectural contradiction between authoritative requirements and repository reality."
),
}

External research used only as advisory hardening: passenger-vehicle TPMS research demonstrates that persistent identifiers can be observed passively and may be spoofable, but U.S. FMVSS 138 does **not** establish TPMS prevalence for Class 8/heavy trucks; the heavy-commercial observability thesis therefore must be measured directly rather than inherited from passenger-car literature. NTP exposes useful clock-quality concepts such as offset, jitter, dispersion, and synchronization distance; NIST guidance supports hash-based digital-evidence integrity; FHWA data confirms that truck-route feasibility involves designated networks plus access/restriction complexity; and NIST IoT guidance supports lifecycle-oriented device onboarding and credential management. The supplied Deep Research report is advisory, and its hypothetical implementation snapshot is **not repository truth**. This prompt implements the supplied Final Synthesis Directive and preserves its authority hierarchy and original-product-ambition requirement.

```text
GROUNDVIEW — DEFINITIVE CURSOR EXECUTION MEGA PROMPT
FINAL SYNTHESIS / EXECUTION CONTRACT
P0–P18 FROZEN FOUNDATION + P19–P30 SCIENTIFIC/OPERATIONAL PROGRAM
+ GV-C1–GV-C14 END-STATE CAPABILITY PROGRAM

===============================================================================
0. YOUR ROLE
===============================================================================

You are the implementation agent responsible for carrying GroundView forward from
its existing repository state.

You are NOT being asked to write another architecture review.

You are NOT being asked merely to produce a plan.

You must:

1. inspect repository truth,
2. establish the actual baseline,
3. map existing GroundView abstractions,
4. implement every safe software-buildable improvement whose correctness does
   not depend on unavailable physical evidence,
5. add focused tests,
6. run tests continuously,
7. repair root causes instead of patching around broken abstractions,
8. update the authoritative GroundView documents,
9. preserve all frozen historical contracts,
10. stop only the specific workstreams blocked by physical evidence,
    authorization, or a genuine unresolved repository contradiction,
11. continue all other safe work.

Do not ask broad questions already answered by this contract.

If an implementation detail is uncertain but reversible and does not change
frozen semantics, make the smallest repository-consistent choice and proceed.

If a decision would mutate a frozen contract, fabricate empirical evidence,
change the scientific meaning of an existing result, require production
authorization, or depend materially on unknown physical behavior, do not guess.
Block only that workstream, document the boundary, and continue safe work.

There is no further architecture-planning round after this unless you discover
a genuine contradiction in the checked-out repository.

===============================================================================
1. GROUNDVIEW NORTH STAR
===============================================================================

GroundView is intended to become the physical ground-observation domain inside
SkyView.

The final ambition is not:

    two SDRs
    + TPMS overlap
    + one matcher score

The final ambition is:

    PHYSICAL COMMERCIAL ROAD UNIT
            │
            ├── RF / TPMS
            ├── other lawful passive RF
            ├── camera / visual evidence
            ├── vehicle markings
            ├── trailer/container markings
            ├── visual dimensions
            └── future roadside observation modalities
            │
            ▼
    GROUNDVIEW OBSERVATION NETWORK
            │
            ▼
       receiver A
            │
            ▼
       receiver B
            │
            ▼
       receiver C
            │
            ▼
    temporary evidence-backed road-unit episode
            │
            ▼
       road-network constraints
            │
            ▼
    evidence-constrained physical journey
            │
            ▼
    facility / yard / terminal interaction
            │
            ▼
      destination evidence / inference
            │
            ▼
      MABELINE PHYSICAL-EVIDENCE GRAPH
            │
            ▼
           SKYVIEW
            │
            ▼
     LIVE GROUND TRANSPORTATION LAYER

At the larger product level:

    AIR      ADS-B / OpenSky / equivalent observations
    SEA      AIS
    SPACE    orbital telemetry
    GROUND   GroundView

                         ONE SKYVIEW EARTH

Do not implement unrelated AIR / SEA / SPACE work merely because this vision
exists.

Do preserve architectural compatibility with the concept of one Earth showing
multiple observed physical domains.

The central product principle is:

    DO NOT FABRICATE MOVEMENT.

and simultaneously:

    DO BUILD MOVEMENT INTELLIGENCE.

These are compatible because GroundView already has the provenance model needed
to distinguish reality from inference.

GroundView may know:

    OBSERVED
        Receiver A @ t1
        Receiver B @ t2
        Receiver C @ t3

while separately computing:

    INFERRED
        physically feasible movement envelope A → B
        physically feasible movement envelope B → C
        candidate route branches
        candidate next receivers
        arrival windows
        active journey state

The INFERRED model may become sophisticated.

It must never become fake OBSERVED GPS.

The ultimate product is:

    an evidence-constrained model of a real physical road unit
    moving through a real transportation network

not:

    a dot pretending to be a truck.

===============================================================================
2. AUTHORITY HIERARCHY
===============================================================================

Use this exact authority order.

LEVEL 1 — CHECKED-OUT REPOSITORY TRUTH

The actual repository always wins on factual questions involving:

- current branch,
- current files,
- current code,
- actual tests,
- actual implementation,
- current documentation,
- working-tree state,
- currently installed dependencies,
- repository naming conventions.

Inspect before modifying.

LEVEL 2 — CURRENT GROUNDVIEW AUTHORITIES

Inside the repository:

1. SkyView/GROUNDVIEW_STATUS.md
   authoritative for current phase and gate state.

2. SkyView/GROUNDVIEW_SPEC.md
   authoritative for active technical/execution contracts.

3. current GroundView BLUEPRINT.md
   authoritative for architecture/history/narrative.

If STATUS and BLUEPRINT disagree about a gate, STATUS wins.

If repository code contradicts a written frozen contract, do not silently choose
one. Establish the contradiction, identify which authority is current, repair
the earliest responsible abstraction where permitted, and document the result.

LEVEL 3 — APPROVED SCIENTIFIC / OPERATIONAL FUTURE

P19–P30 in this prompt define the scientific/operational progression beyond the
completed P18 software boundary.

LEVEL 4 — ARCHITECTURE HARDENING

The scientific-validity, evidence-integrity, clock-quality, receiver-
comparability, security, reliability, observability, data-contract, capacity,
and rollback constraints in this prompt strengthen P19–P30.

LEVEL 5 — ORIGINAL PRODUCT AMBITION

The GV-C capability program in this prompt protects what GroundView is ultimately
trying to become.

It may expand the roadmap.

It may NOT override:

- empirical truth,
- provenance,
- frozen historical contracts,
- security,
- independent evaluation,
- physical field gates,
- evidence integrity.

LEVEL 6 — EXTERNAL / DEEP RESEARCH

Use external research as advisory engineering/scientific input.

Reject or modify advice that conflicts with:

- repository truth,
- frozen GroundView contracts,
- measured evidence,
- the explicit no-fabrication rules in this prompt.

Specifically DO NOT blindly adopt:

- arbitrary clock-skew thresholds,
- arbitrary matcher thresholds,
- guessed throughput SLOs,
- guessed receiver counts,
- premature PostgreSQL/Kafka/Redis/Kubernetes,
- imaginary Python code paths,
- hypothetical test output,
- in-place mutation of frozen versions,
- passenger-car TPMS prevalence as evidence for Class 8 truck prevalence.

Record material Deep Research recommendations you reject or modify in the final
report.

===============================================================================
3. REPOSITORY SAFETY
===============================================================================

Before touching code:

- inspect branch,
- inspect git status,
- inspect current diff,
- preserve unrelated user work,
- do not reset unrelated files,
- do not delete unrelated work,
- do not use destructive git commands,
- do not stash/reset merely to make the tree look clean,
- do not push,
- do not commit unless explicitly instructed,
- do not run `vercel --prod`,
- do not enable GroundView in production,
- do not create a second application,
- do not create a second globe.

Working branch is expected to be local `wip/groundview`, but verify repository
truth.

===============================================================================
4. EXPECTED STARTING BASELINE — VERIFY, DO NOT ASSUME
===============================================================================

Expected snapshot:

    P0–P15 = PASS
    P16–P18 = SOFTWARE_COMPLETE
    empirical field state = FIELD_VALIDATION_REQUIRED

    groundview_match_v1 = preferred
    groundview_match_research_v0 = research only
    v2_justified = false

Expected frozen replay semantics:

    36 packets
    9 passes
    20 matches
    5 tracks
    89.29 canonical pre-competition score

Expected historical test snapshot:

    node --test src/data/groundview/*.test.mjs
    55/55 at the Blueprint snapshot

Test count may now be higher.

Run BEFORE meaningful changes:

    cd SkyView
    node --test src/data/groundview/*.test.mjs
    node scripts/groundview-replay.mjs

Record the exact actual output.

Never fabricate success.

If the semantic replay differs from:

    36 / 9 / 20 / 5 / 89.29

diagnose why before building new capabilities.

If the difference is caused by intentional repository evolution that is already
authoritative, document it.

Otherwise repair the responsible regression before proceeding.

===============================================================================
5. FROZEN P0–P18 FOUNDATION
===============================================================================

Do not reopen these contracts in place.

TRUTH MODEL

    OBSERVED
        Directly measured/received physical evidence.

    DERIVED
        Deterministic computation from OBSERVED evidence under explicit,
        versioned configuration.

    INFERRED
        Probabilistic identity, continuity, route, movement, semantic
        association, destination hypothesis, or other inference.

    CONFIG
        Configured receiver/site/topology/routing/operational information.

Never silently promote one level to another.

ROAD UNIT

    road_unit_v1 =
        tractor + attached trailer traveling together

Do not silently redefine this in field statistics, denominator counts, matching,
journeys, or visualization.

FROZEN HISTORICAL VERSION FAMILIES

Preserve at minimum:

    groundview_event_v1
    groundview_store_v1
    groundview_canonical_v1
    groundview_cluster_v1
    groundview_match_v1
    groundview_track_v1
    groundview_receiver_auth_v1
    groundview_receiver_spool_v1
    groundview_bind_v1

Also preserve repository-established versioning for camera/federation/replay/etc.

FROZEN OPERATIONAL RULES

- one normalizer path,
- stable source_event_id assigned at the durable receiver-spool boundary,
- append-only physical observation semantics,
- fresh auth nonce per HTTP attempt,
- same source_event_id on HTTP retry,
- central ACK only after durable commit,
- field mode rejects synthetic_fixture,
- no fake OBSERVED vehicle GPS,
- no RF confidence label called `confirmed`,
- no permanent truck identity from RF continuity alone,
- no carrier/FMCSA/semantic/camera shortcut inside matcher-v1,
- camera remains optional to the RF path,
- research candidates do not rewrite historical v1 inference,
- GroundView default OFF,
- production GroundView not authorized merely because code exists.

===============================================================================
6. MATCHER-V1 IS FROZEN
===============================================================================

`groundview_match_v1` remains immutable.

Hard gates:

    travel window
    direction
    shared >= 1

Base:

    100 * (
        0.50 * overlap_coefficient
      + 0.30 * shared_count_strength
      + 0.20 * jaccard
    )

Where:

    shared_count_strength =
        min(shared_count / 6, 1)

Absolute caps:

    0 shared  → 0
    1 shared  → 19
    2 shared  → 49
    3 shared  → 69
    4 shared  → 84
    >=5       → 100

Competition:

    only feasible candidates,
    competitor if candidate shares pass A OR pass B.

Then clamp 0–100.

Canonical fixture:

    A = {A,B,C,D,E,F,G}
    B = {A,B,D,E,F}

    pre-competition score = 89.29

Do not “improve” v1 in place.

Any justified change creates a new immutable matcher identifier.

All versions remain replayable/queryable.

===============================================================================
7. IMPORTANT EXTERNAL-RESEARCH CORRECTION: CLASS 8 TPMS IS AN EMPIRICAL QUESTION
===============================================================================

Do NOT infer Class 8/commercial-tractor-trailer TPMS prevalence from passenger
vehicle mandates or passenger-car TPMS literature.

Treat the following as a core P19 falsification question:

    What fraction of independently observed commercial road_unit_v1 traffic
    at a real site emits usable passive RF evidence that GroundView can
    canonicalize and cluster?

Passenger-vehicle work supports the plausibility of passive TPMS observation and
also demonstrates spoofing/privacy concerns.

It does NOT prove:

- Class 8 penetration,
- Class 8 protocol mix,
- Class 8 transmission cadence,
- tractor/trailer sensor count,
- commercial-road-unit fingerprint stability,
- useful downstream range,
- national feasibility.

P19 exists specifically to measure those unknowns.

This is now a BLOCKING scientific unknown, not an assumption.

===============================================================================
8. RF AUTHENTICITY INVARIANT
===============================================================================

Transport authentication and physical RF authenticity are different things.

The current receiver HMAC can establish:

    "a receiver possessing this credential submitted this request"

It does NOT establish:

    "the over-the-air TPMS payload came from an authentic physical tire sensor"

OBSERVED RF therefore means:

    "GroundView receiver observed this radio message"

not:

    "GroundView cryptographically proved this vehicle sensor emitted it"

Preserve this distinction permanently.

Potential RF spoofing/replay/injection is part of the GroundView threat model.

Do not rewrite OBSERVED radio evidence merely because its physical-source
authenticity is uncertain.

If future evidence-integrity scoring is needed, make it a new
DERIVED/INFERRED assessment with versioned provenance.

===============================================================================
9. TWO PROGRAM AXES — DO NOT CREATE PHASE-NUMBER AMBIGUITY
===============================================================================

There are TWO different future structures.

A. SCIENTIFIC / OPERATIONAL PHASES

    P19–P30

These preserve the approved phase numbering and control when physical,
scientific, operational, scale, and product claims are earned.

B. END-STATE CAPABILITY PROGRAM

    GV-C1–GV-C14

These preserve the larger original GroundView ambition.

GV-C work may often be scaffolded before its empirical unlock.

A GV-C capability becoming SOFTWARE_FOUNDATION_READY does NOT mean the physical
claim behind it has been validated.

Use these capability states:

    NOT_STARTED
    SOFTWARE_FOUNDATION
    SOFTWARE_FOUNDATION_READY
    EMPIRICAL_VALIDATION_REQUIRED
    EMPIRICALLY_VALIDATED
    OPERATIONAL
    BLOCKED
    RETIRED

Never call a capability empirically validated merely because fixture tests pass.

===============================================================================
10. SCIENTIFIC / OPERATIONAL CRITICAL PATH P19–P30
===============================================================================

The non-negotiable scientific spine is:

    P19
    one-site physical RF reality

        ↓

    P20
    real two-site A→B experiment
    + contemporaneous independent truth capture

        ↓

    P21
    blinded independent matcher evaluation

        ↓

    P22
    real multi-site corridor continuity

        ↓

    P23
    truthful branch-safe transit projection

P24 is CONDITIONAL measured-need infrastructure.

It is not a mandatory chronological database-upgrade phase merely because the
number comes after P23.

P25–P30 scale and productize only what the physical program has earned.

===============================================================================
11. POST-P18 CROSS-CUTTING CONTRACTS
===============================================================================

Search for repository equivalents before creating anything.

Where absent, introduce repository-consistent additive/versioned structures for
the following responsibilities.

Recommended identifiers are:

    groundview_requirements_v1
    groundview_run_manifest_v2
    groundview_clock_quality_v1
    groundview_receiver_profile_v1
    groundview_ground_truth_v1
    groundview_evaluation_plan_v1
    groundview_matcher_promotion_v1
    groundview_track_evaluation_v1
    groundview_transit_state_v1

These are responsibilities, not permission to duplicate existing abstractions.

If equivalent repository objects already exist, extend or version them.

Do not mutate frozen P0–P18 versions merely to fit these additions.

===============================================================================
12. REQUIREMENT TRACEABILITY
===============================================================================

Implement a traceable execution graph.

Every major requirement must resolve:

    requirement
        → phase/capability
        → implementation
        → test
        → evidence artifact
        → status gate
        → downstream dependencies
        → downstream invalidation if broken

A practical machine-readable representation should include fields equivalent to:

    requirement_id
    statement
    authority_source
    owning_phase
    owning_capability
    implementation_refs[]
    test_refs[]
    evidence_refs[]
    gate
    hard_dependencies[]
    soft_dependencies[]
    invalidates_downstream[]
    status

Do not create bureaucracy for its own sake.

The purpose is that no future engineer must infer why GroundView is allowed to
make a claim.

===============================================================================
13. EVIDENCE CHAIN / RUN MANIFEST V2
===============================================================================

For P19+ empirical work, every important conclusion must be reconstructable.

Implement an additive manifest version rather than rewriting historical
manifests.

Where practical, content-address:

- raw capture artifacts,
- recorded rtl_433 stream,
- normalized evidence export,
- receiver CONFIG,
- receiver profile/install epoch,
- receiver-link CONFIG,
- road/route constraint snapshot,
- software revision,
- dirty-tree/patch identity if relevant,
- schema versions,
- algorithm versions,
- clock-quality record,
- independent truth material,
- annotation set,
- evaluation plan,
- generated reports.

Use deterministic canonical serialization where practical.

Use a modern cryptographic content hash such as SHA-256 unless repository
standards already specify an equivalent.

Never put receiver secrets into manifests.

Hash mismatch or missing evidence does not delete the run.

It changes its scientific status to something equivalent to:

    EVIDENCE_CHAIN_INCOMPLETE

Manifest verification must detect:

- changed file,
- missing file,
- changed config,
- changed annotation,
- mismatched version reference.

Historical evidence remains preserved.

===============================================================================
14. CLOCK QUALITY MODEL
===============================================================================

Time is scientific evidence.

Do not treat a timestamp as intrinsically accurate.

Implement an explicit P19+ clock-quality representation without changing
matcher-v1 semantics.

Capture where available:

    clock source
    synchronization method
    last synchronization time
    estimated offset
    estimated uncertainty
    jitter
    dispersion / synchronization distance if available
    drift indicator
    clock step/jump events
    monotonic/system-time relationship where useful
    quality state

Do NOT hard-code an arbitrary global "1 second" scientific threshold.

Before a P20/P21 field evaluation, freeze a corridor-specific timing-validity
criterion based on:

- link travel-window width,
- receiver clock characteristics,
- expected transit times,
- desired scientific discrimination.

If clock quality makes temporal feasibility scientifically unreliable:

- preserve the evidence,
- mark the run timing-ineligible,
- do not silently widen matcher windows until something matches.

Clock-quality failure is not a reason to mutate v1.

===============================================================================
15. RECEIVER PROFILE / INSTALLATION EPOCH
===============================================================================

Receiver differences can masquerade as road-unit sensor instability.

For every physical installation, capture where material:

    logical receiver_id
    receiver_installation_id / equivalent revision identity
    SDR model
    SDR hardware identity where available
    tuner/chipset where relevant
    firmware
    gain mode
    gain settings
    antenna type
    antenna orientation
    antenna height
    feedline characteristics where material
    mounting environment
    frequency configuration
    rtl_433 version/config
    GroundView node version
    clock configuration
    site geometry
    installation timestamp
    operator notes where appropriate

A hardware/antenna/config replacement must create a new profile revision or
installation epoch.

Do not silently pool before/after data as though the physical receiver remained
identical.

Build profile diff and comparability reporting.

Do not insert receiver-sensitivity normalization into frozen matcher-v1.

===============================================================================
16. RECEIVER COMPARABILITY
===============================================================================

Before interpreting A/B differences as road-unit RF behavior, establish that
receiver/site differences are understood sufficiently for the experiment.

Support procedures such as:

- known RF source where practical,
- controlled instrumented vehicle where practical,
- co-located receiver comparison where practical,
- protocol-mix comparison,
- event-rate comparison,
- sensitivity diagnostics,
- RSSI/SNR behavior where reliable,
- configuration-drift checks.

Do not manufacture one universal calibration threshold.

Freeze the comparability method before the experiment.

A pair with material unexplained sensitivity differences may still generate
useful evidence, but it must not support a strong matcher-validity conclusion
until the confound is addressed.

===============================================================================
17. P19 — ONE-SITE PHYSICAL RF REALITY
===============================================================================

P19 is the next empirical phase.

Goal:

    determine what a real commercial-freight observation site actually hears,
    and establish the first defensible empirical commercial-road-unit RF
    observability measurement.

Prerequisites:

    real SDR
    real antenna
    real physical site
    defensible receiver coordinates
    receiver profile procedure
    clock-quality procedure
    independent synchronized road_unit_v1 counting method
    evidence-manifest procedure
    P16 receiver node path operational

P19 MUST NOT assume passenger-car TPMS prevalence applies to commercial trucks.

Record independent traffic counts outside the RF pipeline.

Counting unit:

    road_unit_v1 =
    tractor + attached trailer traveling together

Record uncertain/unclassifiable road units separately.

P19 must distinguish AT LEAST FOUR denominators:

    D1:
    independently observed commercial road_unit_v1 traffic

    D2:
    RF activity plausibly relevant to the roadway observation period/site

    D3:
    RF observations canonicalizable under the active canonicalization version

    D4:
    RF evidence clusterable into GroundView pass structures

Do not publish one ambiguous "truck detection rate."

Every rate must identify numerator and denominator.

P19 measurements include where available:

    independent commercial road-unit count
    RF event count
    accepted / duplicate / rejected
    protocol distribution
    model distribution
    unknown protocols
    canonicalizable observations
    unique canonical identities
    derived passes
    sensors/pass
    cadence
    frequency
    RSSI
    SNR
    spool depth
    spool age
    retries
    clock state
    receiver health
    environmental/site notes material to interpretation

P19 PASS means:

    real physical evidence is durably captured,
    independently counted,
    clock/profile documented,
    manifest-verifiable,
    replayable,
    uncontaminated by synthetic evidence.

P19 PASS does NOT require GroundView's RF thesis to succeed.

A valid finding of poor commercial RF observability is a successful experiment.

If hardware is unavailable:

    P19 = FIELD_VALIDATION_REQUIRED

and continue safe build-ahead work.

Never fabricate P19.

===============================================================================
18. SENSOR IDENTITY STABILITY / COLLISION RESEARCH
===============================================================================

Do not assume `protocol:model:sensor_id` is globally unique forever.

Keep `groundview_canonical_v1` frozen.

Add field diagnostics capable of measuring:

    same physical sensor changing representation
    same known road unit losing/gaining sensors
    independently known different road units sharing canonical IDs
    decoder-version interpretation changes
    protocol-family collision behavior
    long-term sensor replacement/churn

This is a scientific diagnostic.

Do not "fix" canonical-v1 based on speculation.

If field evidence justifies a successor, create a new version and preserve v1.

===============================================================================
19. P20 — REAL TWO-SITE A→B EXPERIMENT
===============================================================================

Goal:

    measure real downstream RF continuity under frozen matcher-v1
    while preserving the independent physical truth material P21 will need.

Prerequisites:

    P19 PASS
    two physical receivers
    defensible site coordinates
    receiver profiles
    receiver comparability assessment
    clock eligibility
    defensible direction
    defensible travel-time bounds
    independent synchronized truth-capture method at BOTH sites

Truth material must be captured WHILE REALITY IS HAPPENING.

Acceptable methods may include:

    controlled instrumented vehicles
    synchronized manual observation
    independently reviewed camera/video
    another documented independent physical method

Do not require P20 to judge matcher accuracy.

Do require P20 to preserve the independent evidence from which later labels can
be created.

GroundView output must not influence truth collection.

Where practical, include:

    sparse traffic
    dense traffic
    known-same controlled cases
    known-different / negative controls
    plausible competing vehicles
    sensor loss between sites
    sensor gain between sites
    unknown protocol conditions
    receiver-performance variation

Run frozen matcher-v1 unchanged.

Do not retune after looking at results.

P20 PASS means:

    real A→B candidate behavior is reproducible and inspectable
    AND independent truth source material survived for later annotation.

It does NOT mean matcher precision or recall is established.

===============================================================================
20. P21 — BLINDED INDEPENDENT MATCHER EVALUATION
===============================================================================

The evaluation must be scientifically independent.

Annotators must not see:

    GroundView score
    confidence label
    candidate ranking
    matcher choice
    research matcher result

before labels are frozen.

Preserve:

    original independent evidence
    individual annotations
    disagreements
    adjudication
    label provenance
    label uncertainty

The evaluation unit must NOT consist only of matcher-emitted candidates.

This is critical.

Known-same A→B road-unit transitions for which GroundView emitted:

    NO_CANDIDATE

must be represented so recall can decrease correctly.

If the same-road-unit denominator is incomplete:

    recall = NOT_ESTIMABLE

Do not manufacture recall from the candidate table.

Before scoring, freeze `groundview_evaluation_plan_v1` or equivalent.

It must define:

    evaluation unit
    inclusion/exclusion criteria
    known-same count
    known-different count
    label provenance
    uncertain-label treatment
    data partitions
    traffic-density representation
    protocol representation
    shared-sensor representation
    site/receiver-pair representation
    precision method
    recall method
    false-positive method
    false-negative method
    ambiguity method
    no-candidate method
    uncertainty/confidence intervals where statistically justified
    evidence-sufficiency decision method
    matcher-promotion criteria

Do not invent an arbitrary fixed N now.

Do not redefine success after seeing the scores.

Where evidence volume permits, separate:

    exploratory/tuning evidence
    validation evidence
    final locked evaluation evidence

Do not repeatedly tune against the final locked evaluation dataset.

===============================================================================
21. BASE-RATE / NATURAL-TRAFFIC EVALUATION
===============================================================================

A balanced evaluation set can be useful diagnostically.

It must not masquerade as real-traffic prevalence.

Report separately:

    controlled diagnostic evaluation

and:

    natural-traffic evaluation

Natural-traffic evaluation should preserve actual candidate prevalence and
ambiguity conditions where possible.

Operational precision claims require appropriate natural prevalence or a
scientifically justified weighting method.

Do not let a convenient 50/50 labelled dataset imply real-world positive
predictive performance.

===============================================================================
22. MATCHER PROMOTION GOVERNANCE
===============================================================================

Any matcher successor requires:

    new immutable matcher identifier
    documented research evidence
    recorded candidate configurations tested
    predeclared evaluation protocol
    independent evaluation evidence
    reproducible comparison against v1
    documented improvements
    documented regressions
    migration decision
    continued ability to query/replay v1

Valid P21 outcomes are:

    V1_ACCEPTABLE

    VERSIONED_CHANGE_JUSTIFIED

    EVIDENCE_INSUFFICIENT

If evidence is insufficient:

    collect more evidence.

Do not promote v2 because a research runner exists.

===============================================================================
23. P22 — REAL MULTI-SITE CORRIDOR CONTINUITY
===============================================================================

Goal:

    determine whether validated pairwise evidence can support a truthful
    multi-observation road-unit episode across 3+ physical sites.

Test:

    A → B → C+
    missing B
    receiver outage
    competing nearby road units
    forks
    merge pressure
    weak edge
    delayed arrival
    sensor disappearance
    sensor appearance
    high traffic density
    gap recovery
    episode termination

Track correctness is NOT the same as match-edge correctness.

Evaluate separately:

    edge correctness
    episode/track correctness
    branch correctness
    missed-observation recovery
    false continuation
    false split
    termination correctness

A series of individually plausible edges may still form the wrong journey.

P22 PASS requires defensible episode-level continuity.

If pairwise recognition works but tracks fail:

    preserve pairwise capability,
    do not fake journey capability,
    investigate/version track logic separately.

P22 is the empirical gate that earns authoritative P23 transit visualization.

===============================================================================
24. TEMPORARY IDENTITY REMAINS TEMPORARY
===============================================================================

Network scale must not silently create permanent truck identity.

A road-unit episode:

- has a beginning,
- continues while evidence justifies continuity,
- may branch,
- may weaken,
- may become ambiguous,
- may become lost,
- terminates.

A similar fingerprint reappearing days later is not automatically the same
continuing episode.

Any future cross-episode recurrence model belongs in GV-C12 and is separately
versioned INFERRED output.

===============================================================================
25. P23 — BRANCH-SAFE TRANSIT PROJECTION
===============================================================================

P23 provides truthful movement intelligence after P22 earns it.

The primary domain object is NOT an animated truck.

The primary domain object is evidence-backed temporary continuity.

The animation is a projection.

`groundview_transit_state_v1` or repository equivalent should support fields
equivalent to:

    transit_state_id
    journey/track id
    from observed pass
    candidate next observed pass if known
    from receiver
    candidate next receiver(s)
    state
    movement envelope
    candidate route geometries
    candidate route count
    estimated progress if justified
    estimated position only if sufficiently constrained
    earliest arrival
    latest arrival
    route basis
    temporal basis
    estimator version
    ambiguity state
    expiration condition
    updated_at

States should support semantics equivalent to:

    AT_OBSERVATION_SITE
    IN_TRANSIT_INFERRED
    IN_TRANSIT_AMBIGUOUS
    ARRIVAL_WINDOW
    EXPECTED_NOT_SEEN
    LOST_FROM_COVERAGE
    TRACK_ENDED

Do not add fake precision.

A single estimated moving coordinate is permitted only when route basis is
sufficiently constrained.

When multiple materially plausible routes exist:

    preserve all relevant branches,
    OR show uncertainty geometry,
    OR stop precise motion.

Never choose one road because it looks better on the globe.

Do not display an uncalibrated numeric `route_confidence` as though it were a
probability.

Prefer factual ambiguity/evidence fields until probability calibration exists.

===============================================================================
26. TRACK END ≠ DESTINATION
===============================================================================

Permanent invariant:

    track ended
    ≠
    destination reached

Likewise:

    last observed near facility
    ≠
    facility arrival

and:

    expected receiver not seen
    ≠
    proof the vehicle did not travel there

GroundView must always preserve these distinctions.

===============================================================================
27. P24 — MEASURED-NEED INFRASTRUCTURE
===============================================================================

P24 is conditional.

Do NOT preselect:

    PostgreSQL
    Kafka
    Redis
    Kubernetes
    service mesh
    worker farm
    sharding

because national GroundView may someday be large.

First benchmark the actual system.

Measure:

    events/sec
    peak event rate
    durable commit latency
    batch latency
    state/store size
    snapshot/query latency
    replay duration
    memory
    CPU where useful
    spool backlog
    spool age
    concurrent receivers
    candidate-generation growth
    track volume
    retention growth
    failure recovery time

P24 activates only when measured operation demonstrates an actual bottleneck or
availability requirement.

When migration is justified:

1. freeze candidate storage schema/version,
2. snapshot old authoritative store,
3. replay representative evidence through old implementation,
4. replay through candidate implementation,
5. compare OBSERVED IDs,
6. compare derived IDs,
7. compare inferred IDs,
8. compare version/config references,
9. perform parity/shadow reads where practical,
10. test concurrent idempotency,
11. test auth nonce behavior,
12. test rollback/restart,
13. test backfill,
14. test receiver-spool compatibility,
15. perform one explicit authority cutover,
16. retain old snapshot as audit/rollback evidence.

At every instant:

    exactly one evidence store is authoritative.

Do not change matcher or provenance semantics during persistence migration.

===============================================================================
28. PRE-P25 OPERATIONAL REVIEW
===============================================================================

Before GroundView changes from experiment into persistent regional observation
network, require explicit decisions covering:

    receiver site authorization
    receiver ownership/operator responsibility
    camera use
    access control
    credential lifecycle
    retention
    raw RF retention
    image/video retention
    public/private service exposure
    incident handling
    physical maintenance
    privacy impact
    jurisdictional requirements

Do not burden P19 laboratory/field experiments with national-scale bureaucracy.

Do not silently move from 3 experimental receivers to 100 persistent receivers.

===============================================================================
29. P25 — REGIONAL OPERATIONAL NETWORK
===============================================================================

P25 proves GroundView can operate as a persistent regional physical-observation
network.

Build/validate as measured need requires:

    receiver enrollment
    provisioning
    credential rotation
    revocation
    quarantine
    decommissioning
    recovery
    installation revisions
    software-version reporting
    clock health
    site health
    spool health
    ingest health
    decoder health
    unknown protocol trends
    coverage diagnostics
    regional playback
    incident handling

No receiver-count number itself defines success.

===============================================================================
30. P26 — MULTI-REGION / NATIONAL ARCHITECTURE
===============================================================================

Region is an operational partition.

It is not a new truth model.

Preserve:

    one GroundView evidence model
    versioned schemas
    versioned algorithms
    immutable observations
    receiver provenance
    source_event_id
    historical replay

A road-unit episode may cross operational regions without changing semantic
identity rules.

Cross-region duplicate ingestion remains idempotent.

Do not introduce distributed complexity before measured need.

===============================================================================
31. P27 — LARGE-SCALE LIVE / HISTORICAL EPISODE SERVICE
===============================================================================

P27 supports scalable access to temporary road-unit episodes.

Capabilities include:

    live episode updates
    historical episode lookup
    observed receiver sequence
    match-edge inspection
    competing-candidate inspection
    fork inspection
    weakest-link inspection
    transit state
    gap state
    lost-from-coverage state
    algorithm/config provenance
    regional crossing
    playback

No permanent universal truck identifier is created from RF continuity alone.

===============================================================================
32. P28 — MABELINE PHYSICAL-EVIDENCE BRIDGE
===============================================================================

P28 connects GroundView road-unit episodes to broader Mabeline evidence.

Possible edges:

    road_unit_episode → candidate facility
    road_unit_episode → candidate carrier
    road_unit_episode → candidate USDOT entity
    road_unit_episode → candidate tractor/unit number
    road_unit_episode → candidate trailer
    road_unit_episode → candidate container
    road_unit_episode → candidate visual identity

These are evidence edges.

They do not modify raw RF evidence.

They do not enter matcher-v1.

They remain INFERRED unless an independent contract allows a stronger truth
classification.

They may be recomputed/withdrawn without rewriting RF history.

===============================================================================
33. P29 — MATURE SKYVIEW GROUNDVIEW SURFACE
===============================================================================

The mature SkyView layer should support:

    receiver network
    receiver health
    coverage
    observed passes
    matches
    journeys/tracks
    inferred transit
    uncertainty
    ambiguity
    candidate routes
    facility interactions
    destination hypotheses
    historical playback
    semantic evidence
    evidence inspection
    algorithm/config inspection

A technically sophisticated user must be able to answer:

    What was actually observed?
    What was derived?
    What was inferred?
    Which sensors contributed?
    How healthy were those sensors?
    How good were their clocks?
    Which matcher ran?
    Which road constraints were used?
    Which competitors existed?
    What is the weakest link?
    Why did the journey continue?
    Why did it branch?
    Why was a gap bridged?
    Why was a facility interaction inferred?
    Why was a destination inferred?
    Is this position measured or modeled?
    When did GroundView stop knowing?

If a beautiful animation cannot answer those questions, it is a product
regression.

===============================================================================
34. P30 — PRODUCTION HARDENING / GEOGRAPHIC EXPANSION
===============================================================================

P30 concerns mature operations, not permission to deploy.

Production-grade concerns include:

    receiver fleet lifecycle
    access controls
    audit logging
    backup
    restore
    disaster recovery
    retention enforcement
    capacity planning
    algorithm rollout control
    schema migration discipline
    security review
    monitoring
    incident response
    evidence-integrity verification
    field-node update process
    regional failover where justified

Production deployment remains an explicit owner authorization.

Additional countries/regions require jurisdiction-specific operational/privacy/
retention/security review.

Do not assume one global policy.

===============================================================================
35. END-STATE CAPABILITY PROGRAM
===============================================================================

The P phases prove that GroundView deserves stronger claims.

The GV-C program ensures the product ambition is not lost.

Implement safe software foundations now where instructed.

Do not call capability foundations empirically validated before their gates.

===============================================================================
36. GV-C1 — JOURNEY ENGINE
===============================================================================

Goal:

    transform successive evidence-backed observations into a temporary
    road-unit journey/episode graph.

A journey should represent:

    observed nodes
    inferred links
    branches
    gaps
    candidate continuations
    evidence references
    algorithm versions
    termination state

The journey is temporary.

It is not permanent vehicle identity.

Build now:

- repository-consistent journey/episode data structures,
- deterministic IDs where appropriate,
- observed-node vs inferred-edge distinction,
- serialization,
- replay hooks,
- graph tests,
- branch/termination tests.

Do not claim real journey validity until P22.

===============================================================================
37. GV-C2 — ROAD-NETWORK CONSTRAINT ENGINE
===============================================================================

Goal:

    represent where a commercial road unit could physically travel,
    not fabricate where it did travel.

Create a provider-neutral abstraction capable of representing:

    road segments
    directed edges
    receiver-to-road associations
    junctions
    commercial feasibility
    truck restrictions
    weight/height/length restrictions where known
    travel-time envelopes
    candidate paths
    facility access
    route branches
    restriction source
    restriction effective time
    road-graph snapshot/version

Do not hard-code one mapping provider unless repository architecture already
requires it.

Do not assume:

    shortest route == actual route.

Do not treat any road graph as perfect ground truth.

Commercial routing constraints vary by jurisdiction, local access, dimensions,
temporary restrictions, and data-source completeness.

Every route calculation must preserve:

    graph/source identity
    snapshot/version
    applied restrictions
    route basis

Build interfaces/tests now.

Authoritative movement use remains empirically gated.

===============================================================================
38. GV-C3 — LIVE TRACK STATE
===============================================================================

For every active journey, eventually maintain recomputable state equivalent to:

    last_observed
    last_observed_at
    episode_age
    candidate_next_receivers
    expected_receiver_windows
    movement_envelope
    candidate_routes
    ambiguity
    gap state
    continuity state
    expiration condition

Do not use uncalibrated probabilities merely because numeric scores look useful.

The state must be recomputable from evidence + exact config/version.

Build the model now.

Enable authoritative live use only after P22/P23.

===============================================================================
39. GV-C4 — RECEIVER PREDICTION
===============================================================================

A mature GroundView network should reason about where an active road unit could
plausibly be observed next.

Inputs may include:

    last observations
    receiver topology
    road topology
    travel-time envelopes
    direction
    receiver health
    coverage state
    route ambiguity
    current journey state

Outputs should support:

    candidate_next_receivers
    earliest plausible arrival
    latest plausible arrival
    unreachable receivers
    alternate receivers
    route basis
    uncertainty

A missed expected receiver hit may produce:

    EXPECTED_NOT_SEEN

or repository-equivalent state.

Never interpret this alone as proof of route choice.

Reasons include:

    alternate route
    receiver failure
    coverage failure
    RF modality disappeared
    clock problem
    wrong continuity hypothesis
    journey ended

Build interface/simulation/tests now.

Validate operational meaning later.

===============================================================================
40. GV-C5 — GAP BRIDGING
===============================================================================

National utility requires gaps.

Example:

    A observed
    [50 miles not observed]
    C observed

GroundView may infer continuity if evidence justifies it.

It must never fabricate intermediate hits.

Gap state must retain:

    last actual observation
    next actual observation
    gap duration
    gap distance if defensible
    candidate routes
    competing journeys
    supporting fingerprint evidence
    supporting modalities
    receiver blind spots
    receiver health
    timing basis
    uncertainty
    version

Distinguish explicitly:

    OBSERVED_CONTINUITY

from:

    INFERRED_GAP_CONTINUITY

Build data structures/tests now.

Do not empirically validate before real multi-site evidence.

===============================================================================
41. GV-C6 — FACILITY ARRIVAL / DEPARTURE / DWELL
===============================================================================

GroundView should eventually reason about physical interaction with:

    warehouse
    yard
    terminal
    port
    border facility
    distribution center
    other Mabeline physical location

Model truthful states such as:

    PASS_BY
    POSSIBLE_ARRIVAL
    OBSERVED_NEAR_FACILITY
    INFERRED_ARRIVAL
    OBSERVED_ARRIVAL
    DWELL_CANDIDATE
    DWELL_INFERRED
    DEPARTURE
    LOST_NEAR_FACILITY

Do not create `OBSERVED_ARRIVAL` unless an actual observation contract supports
that statement.

Facility geofence/area is CONFIG or external evidence, not road-unit truth.

Build state skeleton and evidence requirements now.

Do not claim validated arrival/dwell without field evidence.

===============================================================================
42. GV-C7 — DESTINATION INFERENCE
===============================================================================

Destination intelligence is IN SCOPE.

Destination fabrication is forbidden.

Future destination inference may use:

    observed journey progression
    road graph
    receiver sequence
    arrival evidence
    dwell evidence
    facility evidence
    departure evidence
    anonymous recurrence
    independent Mabeline evidence

Output:

    candidate destinations
    evidence basis
    ambiguity
    provenance
    model version
    expiration/update time

Distinguish:

    OBSERVED_DESTINATION
    INFERRED_DESTINATION
    PREDICTED_DESTINATION
    UNKNOWN
    TRACK_LOST

A track ending is never enough to produce `INFERRED_DESTINATION`.

Create a versioned research/domain skeleton now if repository structure supports
it.

Do not ship destination claims before evidence exists.

===============================================================================
43. GV-C8 — MABELINE EVIDENCE BRIDGE
===============================================================================

This capability corresponds strongly with P28.

Build reusable evidence-edge semantics that reference, rather than rewrite,
GroundView evidence.

GroundView physical continuity remains distinct from semantic meaning.

===============================================================================
44. GV-C9 — CORRIDOR NETWORK
===============================================================================

A corridor is more than multiple receivers uploading.

A mature corridor should understand:

    receiver topology
    coverage
    health
    expected next receiver
    blind spots
    continuity rate
    traffic density
    track fragmentation
    receiver usefulness
    corridor flow

P22 provides the scientific proof.

P25 operationalizes persistent corridor/regional behavior.

Build topology/diagnostic foundations now.

===============================================================================
45. GV-C10 — NATIONAL GROUNDVIEW
===============================================================================

Architect for eventual growth such as:

    10 receivers
    100
    1,000+
    interstate corridors
    freight chokepoints
    ports
    yards
    terminals
    warehouses
    border crossings
    national road graph

These are scale possibilities, not near-term receiver targets.

Capabilities eventually include:

    receiver registry
    topology
    coverage map
    blind spots
    health
    config
    regional partitions
    national episode graph
    active episodes
    playback
    receiver placement analysis

Infrastructure remains measured-need only.

===============================================================================
46. GV-C11 — NETWORK INTELLIGENCE / PLACEMENT
===============================================================================

GroundView should eventually reason about its own sensor network.

Questions include:

    Which receiver should see this journey next?
    Which expected receiver did not?
    Is that receiver healthy?
    Is the site underperforming?
    Where is coverage weak?
    Which receiver pair causes fragmentation?
    Where would another receiver reduce ambiguity most?
    Which corridors are undersensed?

Build interfaces for:

    coverage deficit
    ambiguity contribution
    expected-observation miss
    receiver usefulness
    candidate placement

Do not confuse network-quality inference with vehicle truth.

===============================================================================
47. GV-C12 — ANONYMOUS RECURRENCE
===============================================================================

Recurring-route intelligence is allowed only under strict identity boundaries.

Potential future outputs:

    anonymous fingerprint recurrence
    repeated corridor pattern
    repeated facility interaction
    repeated route shape

Do not automatically merge recurrences into permanent identity.

Any recurrence system is:

    separately versioned
    INFERRED
    episode-external
    uncertainty-aware

Build only minimal interfaces now if they naturally fit existing architecture.

Do not prematurely create long-term identity.

===============================================================================
48. GV-C13 — MULTISIGNAL ROAD-UNIT FINGERPRINT / FUSION
===============================================================================

TPMS is GroundView's first empirical modality.

It is not GroundView's ceiling.

Possible future modalities:

    rf_tpms
    other passive RF
    camera
    vehicle marking
    trailer marking
    container marking
    visual dimensions
    roadside sensor
    future lawful passive signal

Do NOT retrofit these inputs into frozen matcher-v1.

Do NOT copy all modalities into one flattened "raw observation" structure if
that destroys their individual provenance.

Prefer a modality-neutral evidence-reference abstraction:

    evidence bundle / observation refs
        ├─ RF observation refs
        ├─ camera observation refs
        ├─ marking observation refs
        └─ other modality refs

Each underlying modality retains its own OBSERVED evidence.

Future fusion belongs in a separately versioned research family such as:

    groundview_fusion_research_v0

and, only if justified:

    groundview_fusion_v1

Fusion outputs must explain:

    which modalities contributed
    which evidence objects were used
    which weights/gates/model version applied
    which modalities disagreed
    resulting uncertainty

Fusion does not rewrite modality-specific history.

Existing camera/OCR/binding work should be reused.

Do not build a duplicate camera pipeline.

===============================================================================
49. GV-C14 — LIVE SKYVIEW GROUND LAYER / ONE EARTH
===============================================================================

The mature ground layer should eventually combine:

    actual observations
    evidence-constrained modeled motion
    journeys
    uncertainty
    receiver network
    facilities
    semantic evidence
    playback
    provenance inspection

within the EXISTING SkyView Earth.

Observed contact and inferred motion must be visually unmistakable.

An anonymous commercial road unit may feel live to the user while the system
still truthfully shows where observation ends and modeling begins.

That is the product destination.

===============================================================================
50. CAPABILITY UNLOCK MAP
===============================================================================

Use this relationship.

GV-C1 Journey Engine
    software foundation now
    empirical authority after P22

GV-C2 Road-Network Constraint Engine
    interfaces/models now
    field-constrained use P22/P23+

GV-C3 Live Track State
    structures now
    authoritative product use P23+

GV-C4 Receiver Prediction
    simulation/interface now
    empirical evaluation P22/P25+

GV-C5 Gap Bridging
    structures/tests now
    empirical validation P22+

GV-C6 Facility Interaction
    state/evidence model now
    empirical validation after corridor/facility evidence

GV-C7 Destination Inference
    skeleton/research contract now
    validation only after facility/journey evidence

GV-C8 Mabeline Bridge
    evidence-edge foundation now if reusable
    mature integration P28

GV-C9 Corridor Network
    topology foundation now
    scientific proof P22
    operations P25

GV-C10 National GroundView
    architecture interfaces only now
    operations P26/P27+

GV-C11 Network Intelligence
    diagnostic interfaces now
    useful optimization after real regional data

GV-C12 Anonymous Recurrence
    minimal versioned research boundary now
    real research only with longitudinal evidence

GV-C13 Multisignal Fusion
    modality/evidence-reference foundation now
    empirical fusion only with independent labelled evidence

GV-C14 Live SkyView Ground Layer
    data/presentation contracts may be prepared now
    authoritative inferred movement after P23
    mature product P29

===============================================================================
51. ROAD GRAPH DATA INTEGRITY
===============================================================================

Road data changes over time.

Any road-constraint result capable of affecting scientific interpretation should
reference:

    road_graph_snapshot_id
    source/provider
    retrieval/effective time where relevant
    restriction data version
    applied commercial-vehicle assumptions
    route-engine version

Truck routing can depend on:

    one-way rules
    HGV restrictions
    weight
    height
    length
    axle constraints
    local access
    terminal access
    temporary restrictions
    construction
    jurisdiction

Do not pretend every source contains all restrictions.

Route feasibility is an INFERRED/CONFIG-derived constraint.

It is not physical proof of the route actually taken.

===============================================================================
52. MOVEMENT-ENVELOPE RULES
===============================================================================

The road-network engine should answer:

    where the journey could physically be
    where it could not be
    which receivers are reachable
    which route families remain feasible
    which candidate continuation is physically impossible

It should NOT answer:

    "the truck definitely drove this exact polyline"

unless independent OBSERVED evidence actually supports that claim.

Movement-envelope narrowing can use accumulating evidence.

When new observation C arrives, recompute the prior hypotheses deterministically
under the relevant estimator/constraint version.

Do not rewrite historical states without version/run provenance.

===============================================================================
53. EXPECTED-NOT-SEEN SEMANTICS
===============================================================================

A predicted receiver miss is useful evidence.

It is not proof.

Whenever GroundView expected an observation and did not receive one, reasoning
must account for at least:

    receiver health
    receiver installation/profile
    clock health
    current ingest health
    spool backlog
    coverage quality
    modality observability
    alternate route
    journey termination
    incorrect prior association

Only then may non-detection influence inference.

===============================================================================
54. MULTIMODAL NEGATIVE EVIDENCE
===============================================================================

Absence in one modality is not automatically evidence of physical absence.

Examples:

    TPMS disappears but camera sees candidate road unit.
    Camera is occluded but RF persists.
    Container marking unavailable but RF continues.

Future fusion must distinguish:

    modality not observed
    modality unavailable
    modality unhealthy
    modality expected but absent
    modality contradictory

Do not flatten these states.

===============================================================================
55. OBSERVABILITY BEFORE SCALE
===============================================================================

Build operational visibility before P25.

Metrics/logs should answer:

    Is receiver alive?
    Is receiver clock healthy?
    Did receiver profile change?
    Is RF behavior anomalous?
    Is spool growing?
    Is spool aging?
    Is central ingest keeping up?
    Are auth failures changing?
    Are duplicate rates abnormal?
    Is protocol mix changing?
    Are unknown protocols increasing?
    Is a site pair degrading?
    Are tracks fragmenting?
    Is ambiguity increasing?
    Did a software release shift behavior?
    Is store/query performance nearing a capacity trigger?

Operational telemetry is NOT road-unit physical evidence.

Do not store high-cardinality sensor IDs as metric labels.

Keep evidence data and ops telemetry semantically distinct.

Do not invent SLO numbers yet.

Define SLOs only when operational requirements and measurements justify them.

===============================================================================
56. CAPACITY / COST MODEL
===============================================================================

Build a parameterized capacity model now.

Inputs should support:

    receiver count
    average events per receiver/time
    peak factor
    average event payload
    batch behavior
    derived expansion
    candidate-match growth
    track/journey volume
    retention
    raw evidence retention
    replay workload
    client/viewer demand

Outputs should estimate:

    ingest throughput
    storage growth/day
    derived storage
    index requirements
    replay workload
    network traffic
    compute bands
    approximate operating cost bands where useful

Label estimates as estimates.

Update them as field measurements arrive.

Do not let capacity-model placeholders become claimed production facts.

===============================================================================
57. RECEIVER SECURITY / THREAT MODEL
===============================================================================

Maintain a GroundView-specific threat model covering:

    forged receiver
    stolen receiver credential
    replayed signed request
    nonce abuse
    duplicated event
    event tampering
    receiver ID spoofing
    compromised receiver
    malicious RF payload
    spoofed TPMS ID
    oversized batch
    malformed JSON
    clock manipulation
    denial of service
    secret exposure
    unauthorized enrollment
    admin-surface exposure
    poisoned semantic evidence

Preserve current HMAC-v1 unless a successor is actually justified.

HMAC proves possession of receiver credentials.

It does not prove:

    receiver physical integrity
    sensor authenticity
    truth of every submitted radio event

Before persistent P25 operation, support:

    provisioning
    rotation
    revocation
    quarantine
    decommissioning
    recovery

Do not put secrets in:

    observations
    logs
    reports
    status
    run manifests

===============================================================================
58. CHAOS / FAILURE PROGRAM
===============================================================================

Extend existing failure drills with repository-appropriate automated tests or
repeatable runbooks for:

    receiver restart
    adapter restart
    uploader restart
    network loss
    central outage
    disk full
    spool tail corruption
    cursor corruption
    process crash during local append
    process crash during central commit
    central committed but client never saw ACK
    duplicate batch
    delayed batch/backfill
    clock jump forward
    clock jump backward
    credential revocation
    receiver replacement
    regional ingest outage
    backfill after outage
    partial storage migration failure

No ACK may imply durability that did not happen.

Recovery must not create duplicate OBSERVED evidence.

If a spool-v1 semantic limitation requires behavioral change, version the spool
rather than silently changing historical semantics.

===============================================================================
59. VERSION COMPATIBILITY REGISTRY
===============================================================================

For every versioned family used after P18, make behavior explicit:

    exact version identity
    supported reader versions
    supported writer versions
    unknown-version behavior
    replay behavior
    migration behavior
    historical-preservation rule

Cover at minimum:

    event
    canonicalization
    clustering
    matcher
    tracks
    journey
    transit estimator
    receiver CONFIG
    receiver profile
    receiver-link CONFIG
    road graph/route config
    facility interaction
    destination inference
    evidence binding/fusion
    storage schema

Avoid implicit "use latest" when replay requires exact history.

Unknown required versions should fail clearly rather than silently falling back.

===============================================================================
60. SCIENTIFIC CLAIM LADDER
===============================================================================

GroundView must be able to stop at the strongest claim the evidence supports.

Useful conceptual claim ladder:

    L0  receiver can capture relevant radio evidence

    L1  evidence can be canonicalized/stabilized sufficiently

    L2  road-unit pass fingerprints can be formed

    L3  same road unit can be recognized pairwise downstream

    L4  multi-site temporary journeys are reliable

    L5  realistic observation gaps can be bridged defensibly

    L6  facility interaction can be inferred defensibly

    L7  destination hypotheses are useful and calibrated enough

    L8  multisignal fusion improves continuity/meaning

    L9  regional/national operation is technically/economically justified

Failure at a higher level does not erase valid lower-level capability.

Do not build product language implying a higher claim than the program earned.

===============================================================================
61. EMPIRICAL STOP / REDIRECTION CONDITIONS
===============================================================================

The program must be capable of disproving its own ambition.

Examples:

    Class 8 TPMS/passive RF observability inadequate
    sensor IDs unstable
    collisions too common
    receiver sensitivity dominates observed differences
    pairwise recognition unreliable
    pairwise works but multi-site continuity fails
    gap bridging too ambiguous
    route graph insufficiently constraining
    required receiver density uneconomic
    facility interaction unreliable
    destination inference too uncertain
    multisignal fusion provides little benefit
    national continuity infeasible while corridors remain useful

Valid responses include:

    improve field engineering
    collect more data
    restrict protocol/modalities
    create a newly versioned algorithm
    reduce product claim
    retain corridor-only capability
    abandon a specific capability
    stop the RF thesis

Forbidden response:

    manipulate semantics or evidence so the demo still appears successful.

===============================================================================
62. BUILD-AHEAD POLICY
===============================================================================

Do not stop all engineering because P19 physical hardware is unavailable.

Build NOW where absent and repository-consistent:

SCIENTIFIC INTEGRITY

    requirement traceability
    manifest-v2
    evidence verification
    clock-quality model
    receiver profiles/install epochs
    comparability tooling
    ground-truth schema
    blinded annotation tooling
    evaluation-plan freeze
    matcher-promotion governance
    no-candidate recall tests
    natural-prevalence reporting
    sensor-ID stability diagnostics
    track-level evaluation

MOVEMENT-INTELLIGENCE FOUNDATIONS

    journey/episode model
    observed-node/inferred-link distinction
    road-network abstraction
    road-constraint snapshots
    movement-envelope structures
    candidate-next-receiver structures
    expected-not-seen state
    gap model
    branch-safe transit state
    arrival/departure/dwell skeleton
    destination-hypothesis skeleton
    facility evidence edges
    uncertainty representation

NETWORK FOUNDATIONS

    receiver topology model
    receiver-link topology
    health/profile/clock state
    coverage/blind-spot structures
    receiver-prediction interfaces
    placement-analysis interfaces
    benchmark harness
    capacity model
    storage parity interface

MULTISIGNAL FOUNDATIONS

    modality-neutral evidence references
    modality provenance
    fusion research interface
    evidence bundles
    Mabeline evidence-edge compatibility

RELIABILITY / SECURITY

    chaos tests
    idempotency/replay tests
    malformed-input tests
    spool corruption drills
    ACK ambiguity drills
    credential lifecycle structures
    quarantine/revocation tests
    version-compatibility registry

DOCUMENTATION

    authoritative spec extensions
    traceability
    field method
    operations
    end-state blueprint

===============================================================================
63. DO NOT BUILD AHEAD THESE EMPIRICAL CLAIMS
===============================================================================

Do not manufacture:

    P19 commercial-RF capture rate
    Class 8 TPMS prevalence
    P20 downstream persistence
    P21 precision/recall
    P21 matcher-v2 justification
    optimal receiver spacing
    optimal clustering parameters
    P22 real corridor continuity
    real gap-bridging reliability
    facility arrival accuracy
    destination accuracy
    real route probabilities
    national continuity
    multimodal gain
    production SLOs

Build the instruments.

Do not invent their eventual measurements.

===============================================================================
64. IMPLEMENTATION WAVES — EXECUTE
===============================================================================

After repository inspection and baseline, execute the following waves.

Do not duplicate existing functionality.

Use repository naming/layout conventions.

WAVE 0 — REPOSITORY RECONNAISSANCE

- read STATUS,
- read SPEC,
- read BLUEPRINT,
- inspect all current GroundView modules,
- inspect current tests,
- inspect scripts,
- inspect manifests,
- inspect clock code,
- inspect existing experiment tooling,
- inspect camera/binding/federation code,
- inspect current UI/layer structures,
- inspect git diff.

Produce an internal mapping:

    requirement → existing implementation → gap.

Do not create new files until you have searched for equivalents.

WAVE 1 — BASELINE

Run:

    node --test src/data/groundview/*.test.mjs
    node scripts/groundview-replay.mjs

Record exact actual output in the working notes/status as appropriate.

WAVE 2 — TRACEABILITY + VERSION REGISTRY

Implement:

    groundview_requirements_v1 responsibility
    dependency/invalidation graph
    post-P18 version compatibility registry

Add validation tests.

WAVE 3 — EVIDENCE INTEGRITY

Implement:

    manifest-v2
    artifact hashing
    manifest verification
    missing/tampered-artifact tests

Preserve old manifest readers.

WAVE 4 — CLOCK + RECEIVER PROFILE

Implement:

    clock-quality structures
    field-run timing eligibility logic
    receiver profile/install epoch
    profile diff/comparability structures

Do not alter matcher-v1.

Add injection tests.

WAVE 5 — BLINDED TRUTH + EVALUATION

Implement:

    ground-truth schema
    blinded annotation export/interface
    frozen label-set identity
    frozen evaluation-plan identity
    matcher-output join only after label freeze
    NO_CANDIDATE false-negative handling
    natural-prevalence reporting
    research/final partition governance
    promotion record

Add focused tests.

WAVE 6 — JOURNEY FOUNDATION

Implement/reuse:

    temporary journey/episode graph
    observed node vs inferred edge
    branch representation
    termination
    deterministic/replayable representation

Do not claim field validity.

WAVE 7 — ROAD / MOVEMENT FOUNDATION

Implement provider-neutral:

    road graph interfaces
    route constraint snapshot
    receiver-road association
    candidate path abstraction
    movement envelope
    route ambiguity
    route-version provenance

Do not hard-code a provider merely to finish the task.

WAVE 8 — LIVE STATE / RECEIVER PREDICTION / GAPS

Implement models/interfaces/tests for:

    candidate next receivers
    expected windows
    EXPECTED_NOT_SEEN
    gap state
    branch-safe transit
    uncertainty
    expiration

Keep authoritative product use gated by P22/P23.

WAVE 9 — FACILITY / DESTINATION FOUNDATION

Implement truthful state models and evidence requirements for:

    pass-by
    possible arrival
    arrival evidence
    dwell
    departure
    lost near facility
    destination hypothesis

No actual destination claims without field evidence.

WAVE 10 — NETWORK FOUNDATION

Implement/reuse:

    topology
    coverage/blind-spot representation
    receiver health linkage
    capacity model
    benchmark harness
    future storage parity harness

Do not migrate storage merely because the harness exists.

WAVE 11 — MULTISIGNAL FOUNDATION

Inspect existing camera/binding code first.

Implement only missing cross-modality abstractions:

    evidence references
    modality provenance
    fusion-research boundary
    evidence bundle
    contradiction/absence states

Never insert semantic/camera inputs into matcher-v1.

WAVE 12 — SECURITY / CHAOS

Add appropriate automated tests and/or runbooks for the failure/threat cases
specified above.

Preserve current auth contracts.

WAVE 13 — PRESENTATION CONTRACTS

Prepare presentation helpers/domain adapters needed eventually for:

    observed contacts
    journeys
    movement envelopes
    ambiguity
    candidate receivers
    gaps
    facility state
    destination hypotheses

Do not enable authoritative moving-truck visualization before P22/P23.

WAVE 14 — REGRESSION

Run focused tests throughout.

At completion run:

    node --test src/data/groundview/*.test.mjs
    node scripts/groundview-replay.mjs

plus all newly added scripts/tests.

Verify:

    36 packets
    9 passes
    20 matches
    5 tracks
    89.29 canonical pre-competition score

Verify:

    matcher-v1 unchanged
    GroundView default OFF
    field mode rejects synthetic_fixture
    no `confirmed` RF label
    no fake OBSERVED truck GPS

WAVE 15 — DOCUMENTATION

Update authoritative docs accurately.

Then stop only at the real empirical boundary.

If no physical P19 prerequisites exist:

    P19 = FIELD_VALIDATION_REQUIRED

That is the correct state.

===============================================================================
65. DOCUMENTATION PROGRAM
===============================================================================

Preserve P0–P18 history.

Maintain:

    SkyView/GROUNDVIEW_STATUS.md
    SkyView/GROUNDVIEW_SPEC.md
    current GroundView BLUEPRINT.md

Prefer a small additional durable documentation set:

    SkyView/GROUNDVIEW_FIELD_METHOD.md
    SkyView/GROUNDVIEW_TRACEABILITY.md
    SkyView/GROUNDVIEW_OPERATIONS.md
    SkyView/GROUNDVIEW_END_STATE.md

Do not create these if exact equivalents already exist.

GROUNDVIEW_FIELD_METHOD.md owns:

    P19–P22 field methodology
    independent traffic counts
    receiver profile procedure
    receiver comparability
    clock eligibility
    truth capture
    blinding
    evaluation
    scientific invalidation criteria

GROUNDVIEW_TRACEABILITY.md owns:

    requirement → implementation → test → artifact → gate

Prefer generating it from machine-readable traceability data if practical.

GROUNDVIEW_OPERATIONS.md owns:

    receiver lifecycle
    threats
    chaos/failure
    capacity triggers
    storage migration
    retention
    operational review
    rollback
    regional operations

GROUNDVIEW_END_STATE.md is REQUIRED unless an equivalent already exists.

Its purpose is specifically to prevent future engineering discipline from
narrowing GroundView back into only a TPMS/matcher experiment.

It should preserve:

    north star
    P19–P30 scientific/operational path
    GV-C capability program
    journey engine
    road constraints
    live track state
    receiver prediction
    gap bridging
    facility interaction
    destination inference
    corridor/network intelligence
    anonymous recurrence boundary
    multimodal fusion
    Mabeline bridge
    live SkyView ground layer
    one-Earth product vision

Clearly label incomplete future capabilities.

===============================================================================
66. STATUS RULES
===============================================================================

STATUS must accurately distinguish:

    SOFTWARE_FOUNDATION_READY

from:

    FIELD_VALIDATION_REQUIRED

from:

    PASS / EMPIRICALLY_VALIDATED.

For every major new workstream record where practical:

    current status
    exact tests
    evidence artifact
    unresolved risk
    empirical blocker
    next safe action

Do not mark P19+ PASS from simulation.

===============================================================================
67. PRIVACY / ACCESS DISCIPLINE
===============================================================================

GroundView's very usefulness can create sensitive longitudinal physical
tracking data.

Do not make national raw sensor histories publicly accessible by accident.

Before persistent P25-scale operation, define:

    who may access raw evidence
    who may access semantic identity
    public vs private product surface
    raw evidence retention
    media retention
    audit requirements
    credential/operator responsibilities

Do not prematurely invent policy numbers.

Do create the architectural controls and review gates needed to implement policy
later.

===============================================================================
68. UI TRUTH RULES
===============================================================================

OBSERVED and INFERRED must be visually unmistakable.

Examples:

OBSERVED:

    receiver site
    observed timestamp
    raw/normalized evidence references

DERIVED:

    pass
    canonical identity
    fingerprint

INFERRED:

    match
    journey edge
    journey
    movement envelope
    estimated transit
    gap bridge
    facility interaction
    destination hypothesis
    semantic association

CONFIG:

    receiver location
    route/link
    facility area
    road graph constraint

Never label inferred transit:

    GPS

unless actual GPS evidence exists.

Never label a TPMS-only match:

    confirmed.

When evidence expires:

    stop pretending to know.

===============================================================================
69. CORE NEW INVARIANTS
===============================================================================

Preserve these across all future work:

Evidence may constrain movement without becoming a fabricated observation.

A physical-path hypothesis is INFERRED, never OBSERVED GPS.

A road graph says where a road unit could travel; it does not prove which path
was taken.

A missed expected receiver hit is evidence, not proof.

A receiver-authenticated upload is not proof that the RF payload itself was an
authentic tire-sensor transmission.

A receiver with a poor clock cannot silently expand the candidate universe.

Receiver hardware differences cannot silently become evidence of sensor churn.

A facility proximity event is not automatically arrival.

An episode ending is not automatically destination.

A recurring fingerprint is not automatically permanent identity.

A gap bridge never invents intermediate observations.

A multimodal fusion result never rewrites modality-specific OBSERVED evidence.

Ground truth never enters frozen RF matching.

Recall must include known-same cases where the matcher emitted no candidate.

Natural traffic prevalence must not be replaced with a convenient balanced
evaluation without disclosure.

Track-level correctness is not implied by edge-level correctness.

Scale does not make temporary identity permanent.

National operation does not relax provenance.

Unknown version does not silently mean "latest."

Operational telemetry is not road-unit evidence.

Historical algorithms remain replayable.

Negative evidence remains visible.

Ambition may expand INFERRED intelligence.

Ambition may never falsify OBSERVED truth.

===============================================================================
70. TEST REQUIREMENTS
===============================================================================

Add repository-appropriate focused tests for at least the following new
invariants where implementation exists.

MANIFEST

    deterministic/canonical manifest
    hash verification
    tamper detection
    missing artifact
    no secret leakage
    historical-manifest compatibility

CLOCK

    healthy clock
    stale synchronization
    known offset
    drift
    forward jump
    backward jump
    travel-window boundary
    scientific-run ineligibility without matcher mutation

RECEIVER PROFILE

    stable profile identity
    gain/config change creates revision
    hardware replacement creates new installation epoch
    profile diff
    comparability report

BLINDING

    annotation export lacks matcher fields
    label-set freeze
    label hash identity
    disagreement preservation
    adjudication provenance
    matcher join only after freeze

EVALUATION

    known-same candidate found
    known-same NO_CANDIDATE becomes false negative
    known-different feasible candidate can become false positive
    incomplete truth denominator returns NOT_ESTIMABLE
    natural prevalence reported
    diagnostic balanced prevalence separately identified
    final evaluation cannot be reused as silent tuning set

IDENTITY DIAGNOSTICS

    known-different collision case
    same-unit sensor churn case
    decoder-version change report

JOURNEY

    A→B→C
    fork
    ambiguous edge
    weak edge
    missed middle
    receiver outage
    delayed observation
    termination
    long unsupported gap does not create permanent continuity

ROAD / TRANSIT

    one valid route
    two equally plausible routes
    route restriction
    disconnected graph
    ambiguous route produces no false precise coordinate
    estimator expiration
    LOST_FROM_COVERAGE
    road graph snapshot/version retained

RECEIVER PREDICTION

    plausible next receiver
    unreachable receiver
    unhealthy expected receiver
    EXPECTED_NOT_SEEN
    alternate route
    no negative-evidence certainty

FACILITY

    pass-by
    possible arrival
    lost near facility
    actual independent arrival evidence
    dwell candidate
    departure
    track end alone never becomes destination

DESTINATION

    no evidence → unknown
    track end near facility → not destination
    multiple candidate destinations → ambiguity
    evidence-supported candidate → INFERRED only
    independent observed contract required for OBSERVED destination

MULTISIGNAL

    RF-only remains valid
    camera-only evidence retains camera provenance
    combined evidence retains both references
    modality contradiction preserved
    missing modality distinguished from negative observation
    fusion output cannot alter RF-v1 history

AUTH / SECURITY

    wrong secret
    nonce replay
    stale timestamp
    receiver/body mismatch
    oversized body
    oversized batch
    malformed JSON
    disabled receiver
    quarantined receiver
    secret scan
    field HTTP lacks admin mutation

CHAOS

    restart
    network outage
    central outage
    disk full
    corrupted spool tail
    ACK ambiguity
    duplicate backfill
    credential revocation with backlog

CAPACITY / STORAGE

    current-store benchmark repeatability
    parity harness
    one-authority migration invariant

PRESENTATION

    inferred coordinate never serializes as OBSERVED
    GroundView OFF unchanged
    ambiguous journey never becomes one arbitrary moving path
    lost track does not become destination

===============================================================================
71. ACCEPTANCE THRESHOLD POLICY
===============================================================================

Use hard binary thresholds for true invariants such as:

    zero synthetic_fixture in field evidence
    zero secret leakage
    zero duplicate OBSERVED truth from retries
    zero durability ACK without commit
    zero in-place mutation of matcher-v1
    zero fake OBSERVED GPS

Do NOT invent empirical numerical thresholds merely to finish the project.

For empirical thresholds:

1. define measurement,
2. define decision procedure,
3. freeze it before evaluation,
4. collect evidence,
5. report uncertainty,
6. apply the decision.

This applies to:

    clock eligibility
    receiver comparability
    matcher acceptance
    track acceptance
    route ambiguity
    gap-bridging acceptance
    facility interaction
    destination inference
    SLOs
    capacity migration

===============================================================================
72. FAILURE INVALIDATION
===============================================================================

If an upstream scientific assumption fails, explicitly identify downstream
claims it invalidates.

Examples:

P19 commercial RF observability fails materially:
    blocks strong TPMS-primary national thesis;
    does not block GroundView as future multimodal observation architecture.

P20 downstream persistence fails:
    blocks matcher-validation progression;
    may motivate receiver engineering or modality changes.

P21 matcher unacceptable:
    blocks P22 continuity claim until resolved.

P22 tracks unreliable:
    blocks authoritative P23 moving-road-unit product.
    pairwise evidence may remain valid.

Road topology too ambiguous:
    P23 may use uncertainty envelopes rather than one moving icon.

Facility inference poor:
    GroundView may still track corridors but not claim facility arrival.

Destination inference poor:
    preserve journey capability; do not claim destinations.

National economics poor:
    preserve regional/corridor capability.

Do not make lower-level valid evidence disappear because the larger vision was
not earned.

===============================================================================
73. FINAL EXECUTION BOUNDARY
===============================================================================

When safe build-ahead work is complete:

If real P19 prerequisites exist:

    prepare and execute P19 using the field method.

If they do not exist:

    leave P19 = FIELD_VALIDATION_REQUIRED.

Do not ask a broad SDR questionnaire merely to complete software work.

Do not fabricate a field run.

Do not begin P20 physical claims without P19.

Do not begin P21 scoring without P20 truth material.

Do not make authoritative moving-truck product claims before P22/P23.

Do not deploy persistent regional observation before operational review.

Do not deploy production GroundView without explicit authorization.

===============================================================================
74. FINAL REQUIRED CURSOR REPORT
===============================================================================

At the end of this execution, return a precise report containing:

1. Repository baseline discovered

2. Branch and working-tree state

3. Exact baseline commands run

4. Exact baseline results

5. Authority conflicts discovered

6. Existing architecture reused

7. Files changed

8. New files created

9. New contract/version identifiers

10. New tests

11. New scripts/tooling

12. Requirement-traceability work

13. Evidence-integrity work

14. Clock/receiver-comparability work

15. Blinded evaluation work

16. New movement-intelligence foundations

17. Journey/road/gap/facility/destination foundations

18. Receiver-prediction/network-intelligence foundations

19. New multisignal foundations

20. Reliability/security/chaos work

21. Capacity/storage-parity work

22. Documentation changes

23. Exact final test commands

24. Exact final test results

25. Frozen replay verification:
        36 / 9 / 20 / 5 / 89.29
    or exact explanation of any repository-authoritative contradiction

26. Deep Research recommendations rejected or modified and why

27. Original Ambition capabilities restored to the durable roadmap

28. Work deliberately deferred pending physical evidence

29. Current state of P19

30. Remaining BLOCKING/HIGH risks

31. Exact next safe action

Also include a compact machine-readable summary where practical.

Never claim to have run a command that was not run.

Never invent a test result.

===============================================================================
75. DEFINITION OF DONE FOR THIS CURSOR SESSION
===============================================================================

This session is successful when:

- repository truth has been inspected,
- current baseline is verified,
- frozen P0–P18 semantics remain intact,
- safe scientific-hardening work has been implemented,
- safe movement-intelligence foundations have been implemented,
- safe network/multimodal foundations have been implemented,
- tests cover the new invariants,
- the existing regression remains stable,
- authoritative documents preserve both rigor and ambition,
- P19 remains honestly FIELD_VALIDATION_REQUIRED unless actual physical evidence
  was collected under the required procedure.

Do not stop merely after writing documentation if repository-consistent software
foundations can safely be implemented.

Do not continue into fabricated field conclusions merely because software work
is complete.

===============================================================================
76. FINAL GROUNDVIEW DEFINITION
===============================================================================

GroundView is intended to become a distributed physical ground-observation
system inside SkyView.

It observes commercial road units through independent roadside evidence.

It creates temporary evidence-backed physical identities when justified.

It connects successive observations into journeys.

It constrains those journeys against real transportation topology.

It maintains live evidence-constrained movement state.

It predicts which parts of the sensor network should plausibly observe a road
unit next.

It can use non-detection carefully without confusing it with proof.

It bridges coverage gaps without pretending those gaps were observed.

It can recognize facility interaction, arrival, departure, and dwell when
evidence supports those conclusions.

It can infer candidate destinations while keeping inference separate from
observation.

It can attach Mabeline semantic evidence without contaminating physical RF
matching.

It can grow from a handful of receivers into corridors, regions, and eventually
national-scale topology when measured need and physical evidence justify that
scale.

It can expand from TPMS into a multimodal ground fingerprint while retaining
every modality's raw evidence and provenance.

It presents that physical system on the same SkyView Earth as other observed
domains.

Aircraft receive useful identity from aviation systems.

Ships receive useful identity from maritime systems.

Satellites have catalog identities.

Commercial road units generally do not provide GroundView one universal
identifier.

GroundView therefore constructs a temporary physical identity from repeated
independent observations and continuously tests whether the evidence still
justifies that identity.

For every important statement GroundView eventually makes, it must be capable
of answering:

    What was actually observed?

    What was derived?

    What was inferred?

    Which sensors contributed?

    How healthy were those sensors?

    How good were their clocks?

    Which algorithms ran?

    Which configuration snapshots applied?

    Which road constraints were used?

    Which competing journeys existed?

    Why did continuity continue?

    Why did it branch?

    Why was a gap bridged?

    Why did GroundView expect another receiver?

    Why was that receiver not seen?

    Why was a facility interaction inferred?

    Why was a destination inferred?

    Which modalities contributed?

    How ambiguous is the current movement state?

    When did GroundView stop knowing?

The highest standard is:

    Build extremely ambitious movement intelligence.

    Preserve evidence rigor underneath every layer.

    And when the physical evidence no longer justifies knowledge,
    say so precisely, visibly, and immediately.

BEGIN EXECUTION NOW.
```
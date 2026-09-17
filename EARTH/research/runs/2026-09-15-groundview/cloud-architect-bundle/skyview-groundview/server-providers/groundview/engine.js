import path from 'node:path';
import {
  CANONICAL_VERSION,
  CLUSTER_VERSION,
  MATCHER_VERSION,
  PROVENANCE,
  TRACK_VERSION,
} from '../../../src/data/groundview/constants.mjs';
import { clusterPasses, fingerprintFromPass } from '../../../src/data/groundview/cluster.mjs';
import {
  applyCompetition,
  applyHardGates,
  elapsedSeconds,
  scoreUngatedCandidate,
} from '../../../src/data/groundview/match.mjs';
import {
  fingerprintId,
  matchId,
  passId,
  snapshotId,
  trackId,
} from './ids.js';
import {
  GroundViewError,
  adaptCustomDecoder,
  adaptReceiverNodeEnvelope,
  adaptRtl433Line,
  adaptRtl433Live,
  adaptSourceEvent,
  adaptSyntheticFixture,
} from './normalize.js';
import { normalizeEvent } from './rf/normalizeEvent.js';
import { createGroundViewStore } from './store.js';

const DEFAULT_CACHE = path.join(process.cwd(), '.gev-cache', 'groundview');

export function createGroundViewEngine({ store } = {}) {
  const persistence = store || createGroundViewStore({ rootDir: DEFAULT_CACHE });
  const diagnostics = [];

  function note(code, detail) {
    diagnostics.push({ at: new Date().toISOString(), code, detail });
  }

  async function ingestSourceEvent(raw, defaults = {}) {
    let envelope;
    try {
      envelope = adaptInbound(raw, defaults);
    } catch (error) {
      await persistence.write((state) => {
        state.quarantine.push({
          at: new Date().toISOString(),
          code: error.code || 'GROUNDVIEW_INGEST_PARSE_ERROR',
          raw,
        });
      });
      note(error.code || 'GROUNDVIEW_INGEST_PARSE_ERROR', error.message);
      throw error;
    }
    const observation = normalizeEvent(envelope);
    if (observation.unknown_protocol) note('GROUNDVIEW_UNKNOWN_PROTOCOL', observation.source_event_id);
    if (observation.clock_metadata?.quality === 'suspect') {
      note('GROUNDVIEW_CLOCK_QUALITY_WARNING', observation.source_event_id);
    }
    await persistence.write((state) => {
      const exists = state.observed.observations.some((row) => row.observation_id === observation.observation_id);
      if (exists) return;
      state.observed.events.push(envelope);
      state.observed.observations.push(observation);
    });
    return observation;
  }

  async function ingestNdjson(text, defaults = {}) {
    const lines = String(text || '').split(/\r?\n/);
    const accepted = [];
    const rejected = [];
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        accepted.push(await ingestSourceEvent(JSON.parse(line), defaults));
      } catch (error) {
        rejected.push({ line, code: error.code, message: error.message });
      }
    }
    return { accepted, rejected };
  }

  async function snapshotConfig(kind, config) {
    const id = snapshotId(kind, config);
    await persistence.write((state) => {
      if (!state.config.snapshots.some((row) => row.id === id)) {
        state.config.snapshots.push({
          id,
          kind,
          config,
          created_at: new Date().toISOString(),
        });
      }
    });
    return id;
  }

  async function setReceivers(receivers) {
    await persistence.write((state) => {
      state.config.receivers = [...receivers].sort((a, b) => a.receiver_id.localeCompare(b.receiver_id));
    });
    return snapshotConfig('receivers', receivers);
  }

  async function setLinks(links) {
    await persistence.write((state) => {
      state.config.links = [...links];
    });
    return snapshotConfig('receiver_links', links);
  }

  async function setCameras(cameras) {
    await persistence.write((state) => {
      state.config.cameras = [...cameras];
    });
    return snapshotConfig('cameras', cameras);
  }

  function rebuildMatches(passes, links, clusterSnapshotId) {
    const byReceiver = new Map();
    for (const pass of passes) {
      if (!byReceiver.has(pass.receiver_id)) byReceiver.set(pass.receiver_id, []);
      byReceiver.get(pass.receiver_id).push(pass);
    }
    const generated = [];
    for (const link of links) {
      const upstream = byReceiver.get(link.from_receiver_id) || [];
      const downstream = byReceiver.get(link.to_receiver_id) || [];
      for (const passA of upstream) {
        for (const passB of downstream) {
          const elapsed = elapsedSeconds(passA, passB);
          const scored = scoreUngatedCandidate(passA.sensor_identities, passB.sensor_identities);
          const gates = applyHardGates({
            stats: scored.stats,
            elapsedSeconds: elapsed,
            passA,
            passB,
            link,
          });
          const capped = gates.zero ? 0 : scored.capped_score;
          generated.push({
            provenance: PROVENANCE.INFERRED,
            match_id: matchId({ passAId: passA.pass_id, passBId: passB.pass_id }),
            pass_a_id: passA.pass_id,
            pass_b_id: passB.pass_id,
            receiver_a_id: passA.receiver_id,
            receiver_b_id: passB.receiver_id,
            ...scored.stats,
            jaccard_similarity: scored.stats.jaccard,
            elapsed_seconds: elapsed,
            minimum_travel_seconds: link.minimum_travel_seconds,
            maximum_travel_seconds: link.maximum_travel_seconds,
            travel_time_feasible: gates.travel_time_feasible,
            direction_feasible: gates.direction_feasible,
            base_score: scored.base_score,
            absolute_overlap_cap: scored.absolute_overlap_cap,
            capped_score: capped,
            clustering_config_snapshot_id: clusterSnapshotId,
            score_components: {
              overlap_coefficient: scored.stats.overlap_coefficient,
              shared_count_strength: scored.stats.shared_count_strength,
              jaccard: scored.stats.jaccard,
              weights: { overlap: 0.5, strength: 0.3, jaccard: 0.2 },
            },
          });
        }
      }
    }
    return applyCompetition(generated);
  }

  function rebuildTracks(matches) {
    const edges = matches
      .filter((row) => Number(row.confidence_score) > 0 && row.travel_time_feasible && row.direction_feasible)
      .sort((a, b) => String(a.pass_a_id).localeCompare(String(b.pass_a_id))
        || String(a.pass_b_id).localeCompare(String(b.pass_b_id)));
    const outbound = new Map();
    const inbound = new Set();
    for (const edge of edges) {
      if (!outbound.has(edge.pass_a_id)) outbound.set(edge.pass_a_id, []);
      outbound.get(edge.pass_a_id).push(edge);
      inbound.add(edge.pass_b_id);
    }
    const roots = [...new Set(edges.map((edge) => edge.pass_a_id))].filter((id) => !inbound.has(id));
    const tracks = [];
    const walk = (node, path, matchPath) => {
      const next = outbound.get(node) || [];
      if (!next.length) {
        const passIds = [...path];
        tracks.push({
          provenance: PROVENANCE.INFERRED,
          track_id: trackId({ passIds }),
          pass_ids: passIds,
          match_ids: matchPath.map((edge) => edge.match_id),
          track_builder_version: TRACK_VERSION,
          fork: matchPath.some((edge) => (outbound.get(edge.pass_a_id) || []).length > 1),
          weak_edge: matchPath.some((edge) => Number(edge.confidence_score) < 50),
        });
        return;
      }
      for (const edge of next.sort((a, b) => a.pass_b_id.localeCompare(b.pass_b_id))) {
        if (path.includes(edge.pass_b_id)) continue;
        walk(edge.pass_b_id, [...path, edge.pass_b_id], [...matchPath, edge]);
      }
    };
    for (const root of roots.sort()) walk(root, [root], []);
    return tracks.sort((a, b) => a.track_id.localeCompare(b.track_id));
  }

  async function replay({
    clustering = {},
    matcherVersion = MATCHER_VERSION,
  } = {}) {
    if (matcherVersion !== MATCHER_VERSION) {
      throw GroundViewError('GROUNDVIEW_REPLAY_VERSION_MISSING', matcherVersion);
    }
    const state = await persistence.read();
    const clusterConfig = {
      window_seconds: clustering.window_seconds,
      minimum_sensor_count: clustering.minimum_sensor_count,
    };
    const clusterSnapshot = await snapshotConfig('clustering', clusterConfig);
    const canonicalSnapshot = await snapshotConfig('canonicalization', { version: CANONICAL_VERSION });
    await snapshotConfig('matcher', { version: MATCHER_VERSION });
    const observations = [...state.observed.observations].sort((a, b) => {
      const time = String(a.receiver_timestamp).localeCompare(String(b.receiver_timestamp));
      if (time !== 0) return time;
      return String(a.observation_id).localeCompare(String(b.observation_id));
    });
    const rawPasses = clusterPasses(observations, {
      ...clusterConfig,
      clustering_config_snapshot_id: clusterSnapshot,
    });
    const passes = rawPasses.map((pass) => {
      const id = passId({
        receiverId: pass.receiver_id,
        observationIds: pass.observation_ids,
        snapshotId: clusterSnapshot,
      });
      return {
        ...pass,
        pass_id: id,
        canonicalization_version: CANONICAL_VERSION,
        canonicalization_config_snapshot_id: canonicalSnapshot,
      };
    });
    const fingerprints = passes.map((pass) => {
      const fp = fingerprintFromPass(pass, clusterSnapshot);
      return {
        ...fp,
        fingerprint_id: fingerprintId({ passId: pass.pass_id, identities: pass.sensor_identities }),
      };
    });
    const matches = rebuildMatches(passes, state.config.links, clusterSnapshot);
    const tracks = rebuildTracks(matches);
    const derivedKey = `${CLUSTER_VERSION}:${clusterSnapshot}`;
    const inferredKey = `${MATCHER_VERSION}:${clusterSnapshot}`;
    await persistence.replaceDerived(derivedKey, { passes, fingerprints });
    await persistence.replaceInferred(inferredKey, { matches, tracks });
    return snapshot();
  }

  async function snapshot() {
    const state = await persistence.read();
    const derived = Object.values(state.derived).at(-1) || { passes: [], fingerprints: [] };
    const inferred = Object.values(state.inferred).at(-1) || { matches: [], tracks: [] };
    return {
      receivers: state.config.receivers,
      links: state.config.links,
      cameras: state.config.cameras,
      observations: state.observed.observations,
      events: state.observed.events,
      passes: derived.passes || [],
      fingerprints: derived.fingerprints || [],
      matches: inferred.matches || [],
      tracks: inferred.tracks || [],
      camera_observations: state.camera_observations,
      visual_identities: state.visual_identities,
      bindings: state.bindings,
      experiments: state.experiments,
      heartbeats: state.heartbeats,
      quarantine: state.quarantine,
      diagnostics,
      health: buildHealth(state, derived, inferred, diagnostics),
    };
  }

  async function ingestCamera(observation) {
    await persistence.write((state) => {
      state.camera_observations.push({
        provenance: PROVENANCE.OBSERVED,
        ...observation,
      });
    });
    return observation;
  }

  async function ingestVisualIdentity(row) {
    const record = {
      provenance: PROVENANCE.INFERRED,
      raw_text: row.raw_text,
      normalized_value: row.normalized_value ?? null,
      recognizer_version: row.recognizer_version,
      confidence: row.confidence ?? null,
      camera_observation_id: row.camera_observation_id,
      visual_identity_id: row.visual_identity_id || snapshotId('visual', row),
    };
    await persistence.write((state) => {
      state.visual_identities.push(record);
    });
    return record;
  }

  async function bindCameraToPass(binding) {
    const state = await snapshot();
    const sitePasses = state.passes.filter((pass) => pass.receiver_id === binding.receiver_id);
    const cameraTime = Date.parse(binding.observed_at);
    const nearby = sitePasses.filter((pass) => {
      const start = Date.parse(pass.start_time);
      const end = Date.parse(pass.end_time);
      return cameraTime >= start - 5000 && cameraTime <= end + 5000;
    });
    if (nearby.length !== 1) {
      const record = {
        provenance: PROVENANCE.INFERRED,
        status: nearby.length ? 'ambiguous' : 'unbound',
        competing_camera_trucks: nearby.length,
        camera_observation_id: binding.camera_observation_id,
        pass_ids: nearby.map((pass) => pass.pass_id),
        binding_version: 'groundview_bind_v1',
      };
      await persistence.write((s) => s.bindings.push(record));
      return record;
    }
    const record = {
      provenance: PROVENANCE.INFERRED,
      status: 'bound',
      camera_observation_id: binding.camera_observation_id,
      pass_id: nearby[0].pass_id,
      receiver_id: binding.receiver_id,
      binding_version: 'groundview_bind_v1',
    };
    await persistence.write((s) => s.bindings.push(record));
    return record;
  }

  async function deleteBindings() {
    await persistence.write((state) => {
      state.bindings = [];
    });
  }

  async function recordHeartbeat(row) {
    await persistence.write((state) => {
      state.heartbeats.push({ ...row, at: row.at || new Date().toISOString() });
    });
  }

  async function runExperiment(name, extra = {}) {
    const view = await replay(extra);
    const metrics = experimentMetrics(view);
    const record = {
      experiment_id: snapshotId('experiment', { name, extra }),
      name,
      created_at: new Date().toISOString(),
      metrics,
      config_snapshot_ids: (await persistence.read()).config.snapshots.map((row) => row.id),
    };
    await persistence.write((state) => {
      state.experiments.push(record);
    });
    return record;
  }

  async function calibrate(labelled = []) {
    const view = await snapshot();
    let tp = 0;
    let fp = 0;
    let fn = 0;
    for (const label of labelled) {
      const hit = view.matches.find((match) => match.pass_a_id === label.pass_a_id && match.pass_b_id === label.pass_b_id);
      const predicted = hit && Number(hit.confidence_score) >= (label.threshold ?? 50);
      if (label.positive && predicted) tp += 1;
      else if (label.positive && !predicted) fn += 1;
      else if (!label.positive && predicted) fp += 1;
    }
    const precision = tp + fp ? tp / (tp + fp) : 0;
    const recall = tp + fn ? tp / (tp + fn) : 0;
    return {
      matcher_version: MATCHER_VERSION,
      precision,
      recall,
      tp,
      fp,
      fn,
      note: 'v1 unchanged; a future matcher version must run beside this result',
    };
  }

  async function rebuildFromHistorical() {
    return replay();
  }

  async function playback(asOf) {
    const view = await snapshot();
    return sliceForPlayback(view, asOf);
  }

  async function seedSynthetic({ force = false } = {}) {
    if (process.env.VERCEL) return { seeded: false, reason: 'vercel-memory' };
    const state = await persistence.read();
    const hasObservations = (state.observed.observations || []).length > 0;
    const hasLinks = (state.config.links || []).length > 0;
    if (!force && hasObservations && hasLinks) return { seeded: false };
    const fixture = await import('../../../fixtures/groundview/synthetic.mjs');
    await setReceivers(fixture.RECEIVERS);
    await setLinks(fixture.LINKS);
    await ingestNdjson(fixture.syntheticNdjson(), {
      adapter: 'rtl433',
      source_type: 'rtl433_recorded',
    });
    return { seeded: true, view: await replay() };
  }

  async function seedSyntheticIfEmpty() {
    return seedSynthetic({ force: false });
  }

  return {
    ingestSourceEvent,
    ingestNdjson,
    setReceivers,
    setLinks,
    setCameras,
    replay,
    snapshot,
    playback,
    ingestCamera,
    ingestVisualIdentity,
    bindCameraToPass,
    deleteBindings,
    recordHeartbeat,
    runExperiment,
    calibrate,
    rebuildFromHistorical,
    seedSynthetic,
    seedSyntheticIfEmpty,
    persistence,
    diagnostics,
  };
}

function adaptInbound(raw = {}, defaults = {}) {
  const sourceType = defaults.adapter || defaults.source_type || raw.source_type;
  if (sourceType === 'receiver_node' || raw.source_type === 'receiver_node') {
    return adaptReceiverNodeEnvelope(raw, defaults);
  }
  if (sourceType === 'custom_decoder' || raw.source_type === 'custom_decoder') {
    return adaptCustomDecoder(raw, defaults);
  }
  if (sourceType === 'synthetic_fixture' || raw.source_type === 'synthetic_fixture') {
    return adaptSyntheticFixture(raw, defaults);
  }
  if (sourceType === 'rtl433_live_adapter') {
    return adaptRtl433Live(raw, defaults);
  }
  if (
    sourceType === 'rtl433'
    || sourceType === 'rtl433_recorded'
    || raw.model
    || raw.protocol
    || (raw.time && raw.id != null)
  ) {
    return adaptRtl433Line(raw, {
      ...defaults,
      source_type: defaults.source_type || 'rtl433_recorded',
    });
  }
  return adaptSourceEvent(raw, defaults);
}

function sliceForPlayback(view, asOf) {
  if (!asOf) return view;
  const cutoff = Date.parse(asOf);
  if (!Number.isFinite(cutoff)) return view;
  const observations = (view.observations || []).filter((row) => Date.parse(row.receiver_timestamp) <= cutoff);
  const passes = (view.passes || []).filter((pass) => Date.parse(pass.start_time) <= cutoff);
  const passIds = new Set(passes.map((pass) => pass.pass_id));
  const matches = (view.matches || []).filter((match) => passIds.has(match.pass_a_id) && passIds.has(match.pass_b_id));
  const matchIds = new Set(matches.map((match) => match.match_id));
  const tracks = (view.tracks || []).filter((track) => (track.match_ids || []).every((id) => matchIds.has(id)));
  return {
    ...view,
    observations,
    passes,
    matches,
    tracks,
    playback_at: new Date(cutoff).toISOString(),
  };
}

function experimentMetrics(view) {
  const matches = view.matches || [];
  const passes = view.passes || [];
  const observations = view.observations || [];
  return {
    packets: observations.length,
    unique_raw_ids: new Set(observations.map((row) => row.sensor_id).filter(Boolean)).size,
    unique_canonical_ids: new Set(observations.map((row) => row.canonical_sensor_identity).filter(Boolean)).size,
    estimated_passes: passes.length,
    match_count: matches.length,
    ambiguity_rate: matches.filter((row) => Number(row.competing_candidate_count) > 0).length / Math.max(matches.length, 1),
    score_margin_distribution: matches.map((row) => row.score_margin).filter((value) => value != null),
    confidence_distribution: matches.map((row) => row.confidence_label),
  };
}

function buildHealth(state, derived, inferred, diagnostics) {
  const lastBeat = [...(state.heartbeats || [])].at(-1);
  const receiverLoss = lastBeat
    ? Date.now() - Date.parse(lastBeat.at) > 120000
    : false;
  const clockError = diagnostics.some((row) => row.code === 'GROUNDVIEW_CLOCK_QUALITY_WARNING');
  const decoderFailure = diagnostics.some((row) => row.code === 'GROUNDVIEW_UNKNOWN_PROTOCOL')
    || (state.observed.observations || []).some((row) => row.unknown_protocol);
  const ingestFailure = (state.quarantine || []).length > 0;
  const clusterFailure = !(derived.passes || []).length && (state.observed.observations || []).length > 0;
  const matcherAmbiguity = (inferred.matches || []).some((row) => Number(row.competing_candidate_count) > 0);
  return {
    receiver_loss: receiverLoss,
    clock_error: clockError,
    decoder_failure: decoderFailure,
    ingest_failure: ingestFailure,
    cluster_failure: clusterFailure,
    matcher_ambiguity: matcherAmbiguity,
  };
}

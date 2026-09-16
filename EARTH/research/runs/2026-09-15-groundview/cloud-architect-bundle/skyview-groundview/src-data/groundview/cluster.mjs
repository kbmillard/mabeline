import {
  CLUSTER_VERSION,
  DEFAULT_CLUSTER_WINDOW_SECONDS,
  PROVENANCE,
} from './constants.mjs';
import { canonicalSensorIdentity } from './canonical.mjs';

function compareObservations(a, b) {
  const ta = Date.parse(a.receiver_timestamp || a.observed_at);
  const tb = Date.parse(b.receiver_timestamp || b.observed_at);
  if (ta !== tb) return ta - tb;
  return String(a.observation_id).localeCompare(String(b.observation_id));
}

/**
 * Receiver-local gap clustering. Duplicate packets remain OBSERVED rows
 * but contribute one canonical identity to the fingerprint set.
 */
export function clusterPasses(observations = [], config = {}) {
  const windowSeconds = Number.isFinite(Number(config.window_seconds))
    ? Number(config.window_seconds)
    : DEFAULT_CLUSTER_WINDOW_SECONDS;
  const minimumSensors = Number.isFinite(Number(config.minimum_sensor_count))
    ? Number(config.minimum_sensor_count)
    : 1;
  const snapshotId = config.clustering_config_snapshot_id || null;
  const byReceiver = new Map();
  for (const observation of observations) {
    const receiverId = observation.receiver_id;
    if (!receiverId) continue;
    if (!byReceiver.has(receiverId)) byReceiver.set(receiverId, []);
    byReceiver.get(receiverId).push(observation);
  }
  const passes = [];
  for (const [receiverId, rows] of [...byReceiver.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
    const ordered = [...rows].sort(compareObservations);
    let current = [];
    const flush = () => {
      if (!current.length) return;
      const identities = uniqueIdentities(current);
      if (identities.length < minimumSensors) {
        current = [];
        return;
      }
      passes.push(buildPass(receiverId, current, identities, windowSeconds, snapshotId));
      current = [];
    };
    for (const observation of ordered) {
      if (!current.length) {
        current.push(observation);
        continue;
      }
      const last = current[current.length - 1];
      const gap = (Date.parse(observation.receiver_timestamp || observation.observed_at)
        - Date.parse(last.receiver_timestamp || last.observed_at)) / 1000;
      if (gap > windowSeconds) flush();
      current.push(observation);
    }
    flush();
  }
  return passes;
}

function uniqueIdentities(observations) {
  const seen = new Set();
  for (const observation of observations) {
    const id = observation.canonical_sensor_identity || canonicalSensorIdentity(observation);
    if (id) seen.add(id);
  }
  return [...seen].sort();
}

function buildPass(receiverId, observations, identities, windowSeconds, snapshotId) {
  const ordered = [...observations].sort(compareObservations);
  const start = ordered[0].receiver_timestamp || ordered[0].observed_at;
  const end = ordered[ordered.length - 1].receiver_timestamp || ordered[ordered.length - 1].observed_at;
  const protocolBreakdown = countBy(ordered, (row) => row.rtl433_protocol || row.protocol || 'unknown');
  const modelBreakdown = countBy(ordered, (row) => row.model || 'unknown');
  return {
    provenance: PROVENANCE.DERIVED,
    clustering_version: CLUSTER_VERSION,
    clustering_config_snapshot_id: snapshotId,
    clustering_window_seconds: windowSeconds,
    receiver_id: receiverId,
    start_time: start,
    end_time: end,
    duration_seconds: (Date.parse(end) - Date.parse(start)) / 1000,
    sensor_identities: identities,
    sensor_count: identities.length,
    observation_ids: ordered.map((row) => row.observation_id),
    observation_count: ordered.length,
    protocol_breakdown: protocolBreakdown,
    model_breakdown: modelBreakdown,
    rssi_summary: numericSummary(ordered.map((row) => row.rssi)),
    snr_summary: numericSummary(ordered.map((row) => row.snr)),
  };
}

function countBy(rows, keyFn) {
  const out = {};
  for (const row of rows) {
    const key = String(keyFn(row));
    out[key] = (out[key] || 0) + 1;
  }
  return out;
}

function numericSummary(values) {
  const nums = values.map(Number).filter(Number.isFinite).sort((a, b) => a - b);
  if (!nums.length) return null;
  const sum = nums.reduce((a, b) => a + b, 0);
  return {
    min: nums[0],
    max: nums[nums.length - 1],
    mean: sum / nums.length,
    count: nums.length,
  };
}

export function fingerprintFromPass(pass, snapshotId) {
  return {
    provenance: PROVENANCE.DERIVED,
    pass_id: pass.pass_id,
    receiver_id: pass.receiver_id,
    sensor_identities: [...pass.sensor_identities],
    sensor_count: pass.sensor_count,
    start_time: pass.start_time,
    end_time: pass.end_time,
    canonicalization_version: pass.canonicalization_version,
    clustering_config_snapshot_id: snapshotId || pass.clustering_config_snapshot_id,
  };
}

import { CANONICAL_VERSION } from './constants.mjs';

/**
 * Canonical sensor identity is a DERIVED projection, never observed truth.
 * Raw numeric IDs in different protocol/model namespaces do not match.
 */
export function canonicalSensorIdentity(observation = {}) {
  const protocol = String(observation.rtl433_protocol ?? observation.protocol ?? '').trim();
  const model = String(observation.model ?? '').trim();
  const sensorId = String(observation.sensor_id ?? observation.id ?? '').trim();
  if (!protocol || !model || !sensorId) return null;
  return `${protocol}:${model}:${sensorId}`;
}

export function projectCanonical(observation, { version = CANONICAL_VERSION, snapshotId = null } = {}) {
  return {
    provenance: 'DERIVED',
    canonicalization_version: version,
    canonicalization_config_snapshot_id: snapshotId,
    canonical_sensor_identity: canonicalSensorIdentity(observation),
    raw_sensor_id: observation.sensor_id ?? observation.id ?? null,
    rtl433_protocol: observation.rtl433_protocol ?? observation.protocol ?? null,
    model: observation.model ?? null,
  };
}

import { CLOCK_VERSION, PROVENANCE } from './constants.mjs';

/**
 * Receiver timestamps stay OBSERVED. Any correction is a separate DERIVED record.
 */
export function deriveClockCorrection(observation = {}, offsetSeconds = 0) {
  const receiverTimestamp = observation.receiver_timestamp || observation.observed_at;
  const offset = Number(offsetSeconds) || 0;
  const parsed = Date.parse(receiverTimestamp);
  return {
    provenance: PROVENANCE.DERIVED,
    clock_version: CLOCK_VERSION,
    observation_id: observation.observation_id || null,
    receiver_timestamp: receiverTimestamp,
    offset_seconds: offset,
    corrected_timestamp: Number.isFinite(parsed)
      ? new Date(parsed + offset * 1000).toISOString()
      : null,
  };
}

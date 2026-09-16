import { EVENT_SCHEMA_VERSION, PROVENANCE } from '../../../../src/data/groundview/constants.mjs';

export {
  GroundViewError,
  adaptSourceEvent,
  adaptRtl433Line,
  adaptRtl433Live,
  adaptCustomDecoder,
  adaptReceiverNodeEnvelope,
  adaptSyntheticFixture,
} from '../normalize.js';

import { GroundViewError } from '../normalize.js';
import { canonicalSensorIdentity } from '../../../../src/data/groundview/canonical.mjs';
import { observationId } from '../ids.js';

/** Single RF normalize_event entry. Every adapter must call this. */
export function normalizeEvent(sourceEvent, { ingestedAt } = {}) {
  if (!sourceEvent || sourceEvent.schema_version !== EVENT_SCHEMA_VERSION) {
    throw GroundViewError('GROUNDVIEW_NORMALIZATION_ERROR', 'groundview_event_v1 envelope required');
  }
  const payload = sourceEvent.payload && typeof sourceEvent.payload === 'object'
    ? sourceEvent.payload
    : {};
  const protocol = payload.protocol ?? payload.rtl433_protocol ?? null;
  const model = payload.model ?? null;
  const sensorId = payload.id != null ? String(payload.id) : (payload.sensor_id != null ? String(payload.sensor_id) : null);
  const observation = {
    provenance: PROVENANCE.OBSERVED,
    observation_id: observationId({
      receiverId: sourceEvent.receiver_id,
      sourceEventId: sourceEvent.source_event_id,
    }),
    source_event_id: sourceEvent.source_event_id,
    source_type: sourceEvent.source_type,
    receiver_id: sourceEvent.receiver_id,
    observed_at: sourceEvent.receiver_timestamp,
    receiver_timestamp: sourceEvent.receiver_timestamp,
    ingested_at: ingestedAt || sourceEvent.ingested_at,
    raw_json: payload,
    frequency_hz: sourceEvent.frequency_hz ?? payload.freq ?? null,
    rtl433_protocol: protocol != null ? String(protocol) : null,
    model: model != null ? String(model) : null,
    sensor_id: sensorId,
    pressure: payload.pressure_kPa ?? payload.pressure_PSI ?? payload.pressure ?? null,
    temperature: payload.temperature_C ?? payload.temperature_F ?? payload.temperature ?? null,
    battery: payload.battery_ok ?? payload.battery_V ?? payload.battery ?? null,
    flags: payload.flags ?? null,
    rssi: sourceEvent.signal_metadata?.rssi ?? payload.rssi ?? null,
    snr: sourceEvent.signal_metadata?.snr ?? payload.snr ?? null,
    noise: sourceEvent.signal_metadata?.noise ?? payload.noise ?? null,
    modulation: payload.mod ?? payload.modulation ?? null,
    decoder_name: sourceEvent.decoder_name,
    decoder_version: sourceEvent.decoder_version,
    capture_ref: sourceEvent.capture_ref,
    clock_metadata: sourceEvent.clock_metadata,
    unknown_protocol: !protocol || !model || !sensorId,
  };
  observation.canonical_sensor_identity = canonicalSensorIdentity(observation);
  if (observation.unknown_protocol) {
    observation.parse_note = 'GROUNDVIEW_UNKNOWN_PROTOCOL';
  }
  return observation;
}

import { EVENT_SCHEMA_VERSION, PROVENANCE } from '../../../src/data/groundview/constants.mjs';

const SOURCE_TYPES = new Set([
  'synthetic_fixture',
  'rtl433_recorded',
  'rtl433_live_adapter',
  'custom_decoder',
  'receiver_node',
]);

export function GroundViewError(code, message) {
  const error = new Error(message);
  error.name = 'GroundViewError';
  error.code = code;
  return error;
}

export function adaptSourceEvent(input = {}, defaults = {}) {
  const sourceType = input.source_type || defaults.source_type;
  if (!SOURCE_TYPES.has(sourceType)) {
    throw GroundViewError('GROUNDVIEW_EVENT_IDENTITY_ERROR', `unknown source_type: ${sourceType}`);
  }
  const receiverId = input.receiver_id || defaults.receiver_id;
  if (!receiverId) {
    throw GroundViewError('GROUNDVIEW_EVENT_IDENTITY_ERROR', 'receiver_id required');
  }
  const sourceEventId = input.source_event_id || defaults.source_event_id;
  if (!sourceEventId) {
    throw GroundViewError('GROUNDVIEW_EVENT_IDENTITY_ERROR', 'source_event_id required');
  }
  const receiverTimestamp = input.receiver_timestamp
    || input.time
    || input.observed_at
    || defaults.receiver_timestamp;
  if (!receiverTimestamp) {
    throw GroundViewError('GROUNDVIEW_EVENT_IDENTITY_ERROR', 'receiver_timestamp required');
  }
  return {
    schema_version: EVENT_SCHEMA_VERSION,
    provenance: PROVENANCE.OBSERVED,
    source_type: sourceType,
    receiver_id: receiverId,
    source_event_id: String(sourceEventId),
    receiver_timestamp: new Date(receiverTimestamp).toISOString(),
    sequence_number: input.sequence_number ?? null,
    frequency_hz: input.frequency_hz ?? input.freq ?? null,
    decoder_name: input.decoder_name ?? defaults.decoder_name ?? null,
    decoder_version: input.decoder_version ?? defaults.decoder_version ?? null,
    payload: input.payload ?? input,
    signal_metadata: input.signal_metadata ?? null,
    capture_ref: input.capture_ref ?? null,
    clock_metadata: input.clock_metadata ?? null,
    ingested_at: defaults.ingested_at || new Date().toISOString(),
  };
}

export function adaptRtl433Line(line, defaults = {}) {
  let payload;
  try {
    payload = typeof line === 'string' ? JSON.parse(line) : line;
  } catch (error) {
    throw GroundViewError('GROUNDVIEW_INGEST_PARSE_ERROR', error.message);
  }
  if (!payload || typeof payload !== 'object') {
    throw GroundViewError('GROUNDVIEW_INGEST_PARSE_ERROR', 'rtl_433 row is not an object');
  }
  const sourceEventId = payload.source_event_id
    || [
      defaults.receiver_id,
      payload.time,
      payload.protocol,
      payload.model,
      payload.id,
      payload.freq,
      payload.sequence_number ?? payload.n ?? '',
    ].map((part) => String(part ?? '')).join('|');
  return adaptSourceEvent({
    source_type: defaults.source_type || 'rtl433_recorded',
    receiver_id: payload.receiver_id || defaults.receiver_id,
    source_event_id: sourceEventId,
    receiver_timestamp: payload.time,
    frequency_hz: payload.freq,
    decoder_name: payload.decoder_name || defaults.decoder_name || 'rtl_433',
    decoder_version: payload.rtl_433_version || payload.decoder_version || defaults.decoder_version || null,
    payload,
    capture_ref: payload.capture_ref || defaults.capture_ref || null,
    clock_metadata: payload.clock_metadata || defaults.clock_metadata || null,
    signal_metadata: {
      rssi: payload.rssi ?? null,
      snr: payload.snr ?? null,
      noise: payload.noise ?? null,
    },
  }, defaults);
}

export function adaptRtl433Live(line, defaults = {}) {
  return adaptRtl433Line(line, { ...defaults, source_type: 'rtl433_live_adapter' });
}

export function adaptCustomDecoder(input = {}, defaults = {}) {
  return adaptSourceEvent({
    ...input,
    source_type: 'custom_decoder',
    decoder_name: input.decoder_name || defaults.decoder_name,
    decoder_version: input.decoder_version || defaults.decoder_version,
    capture_ref: input.capture_ref || defaults.capture_ref,
  }, defaults);
}

export function adaptReceiverNodeEnvelope(body, defaults = {}) {
  return adaptSourceEvent({
    ...body,
    source_type: 'receiver_node',
  }, defaults);
}

export function adaptSyntheticFixture(input = {}, defaults = {}) {
  return adaptSourceEvent({
    ...input,
    source_type: 'synthetic_fixture',
  }, { ...defaults, source_type: 'synthetic_fixture' });
}

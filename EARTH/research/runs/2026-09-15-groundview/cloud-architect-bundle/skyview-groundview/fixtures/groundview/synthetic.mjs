const PROTOCOL = '241';
const MODEL = 'TST-507';
const T0 = Date.parse('2026-09-15T10:02:14.000Z');

export const RECEIVERS = [
  {
    receiver_id: 'GV-RX-01',
    name: 'GV-RX-01',
    latitude: 39.0997,
    longitude: -94.5786,
    enabled_frequencies_hz: [315000000, 433920000, 915000000],
  },
  {
    receiver_id: 'GV-RX-02',
    name: 'GV-RX-02',
    latitude: 39.1142,
    longitude: -94.541,
    enabled_frequencies_hz: [433920000],
  },
  {
    receiver_id: 'GV-RX-03',
    name: 'GV-RX-03',
    latitude: 39.13,
    longitude: -94.5,
    enabled_frequencies_hz: [433920000],
  },
];

export const LINKS = [
  {
    from_receiver_id: 'GV-RX-01',
    to_receiver_id: 'GV-RX-02',
    minimum_travel_seconds: 60,
    maximum_travel_seconds: 600,
    direction: 'eastbound',
    distance_meters: 4200,
  },
  {
    from_receiver_id: 'GV-RX-02',
    to_receiver_id: 'GV-RX-03',
    minimum_travel_seconds: 60,
    maximum_travel_seconds: 600,
    direction: 'eastbound',
    distance_meters: 4000,
  },
];

function row(receiverId, sensorId, offsetSec, extra = {}) {
  const { protocol, model, freq, rssi, source_event_id, seq, ...rest } = extra;
  return {
    time: new Date(T0 + offsetSec * 1000).toISOString(),
    protocol: protocol || PROTOCOL,
    model: model || MODEL,
    id: sensorId,
    freq: freq ?? 433920000,
    rssi: rssi ?? -40,
    receiver_id: receiverId,
    source_event_id: source_event_id || `${receiverId}:${sensorId}:${offsetSec}:${seq || 0}`,
    ...(seq != null ? { sequence_number: seq } : {}),
    ...rest,
  };
}

export function syntheticRtl433Rows() {
  return [
    ...['A', 'B', 'C', 'D', 'E', 'F', 'G'].map((id, index) => row('GV-RX-01', id, index * 0.4)),
    row('GV-RX-01', 'A', 1.1, { seq: 1, source_event_id: 'GV-RX-01:A:dup' }),
    ...['J', 'K', 'L', 'M'].map((id, index) => row('GV-RX-01', id, 40 + index)),
    ...['A', 'B', 'D', 'E', 'F'].map((id, index) => row('GV-RX-02', id, 287 + index * 0.3)),
    ...['J', 'L', 'M'].map((id, index) => row('GV-RX-02', id, 360 + index)),
    row('GV-RX-02', 'A', 12, { source_event_id: 'travel-window-miss-A' }),
    row('GV-RX-02', 'B', 12.2, { source_event_id: 'travel-window-miss-B' }),
    row('GV-RX-02', 'A', 420, { source_event_id: 'single-id-coincidence-A' }),
    row('GV-RX-02', 'X', 420.2, { source_event_id: 'single-id-noise-X' }),
    row('GV-RX-02', 'Y', 420.4, { source_event_id: 'single-id-noise-Y' }),
    row('GV-RX-02', 'Z', 420.6, { source_event_id: 'single-id-noise-Z' }),
    row('GV-RX-02', 'A', 480, { source_event_id: 'two-id-A' }),
    row('GV-RX-02', 'B', 480.4, { source_event_id: 'two-id-B' }),
    row('GV-RX-02', 'Q', 480.8, { source_event_id: 'two-id-Q' }),
    {
      time: new Date(T0 + 90 * 1000).toISOString(),
      protocol: '999',
      model: 'OTHER',
      id: 'A',
      freq: 433920000,
      receiver_id: 'GV-RX-01',
      source_event_id: 'namespace-collision-A',
    },
    {
      time: new Date(T0 + 200 * 1000).toISOString(),
      freq: 915000000,
      receiver_id: 'GV-RX-01',
      source_event_id: 'unknown-protocol-raw',
      raw: '????',
    },
    ...['A', 'B', 'D', 'E', 'F'].map((id, index) => row('GV-RX-03', id, 574 + index * 0.4)),
  ];
}

export function syntheticNdjson(shuffle = false) {
  const rows = syntheticRtl433Rows();
  if (shuffle) {
    for (let i = rows.length - 1; i > 0; i -= 1) {
      const j = (i * 7 + 3) % (i + 1);
      [rows[i], rows[j]] = [rows[j], rows[i]];
    }
  }
  return rows.map((row) => JSON.stringify(row)).join('\n');
}

export function cameraFixture() {
  return [{
    camera_observation_id: 'cam-1',
    camera_id: 'GV-CAM-01',
    receiver_id: 'GV-RX-01',
    observed_at: new Date(T0 + 1 * 1000).toISOString(),
    bbox: [0, 0, 10, 10],
  }];
}

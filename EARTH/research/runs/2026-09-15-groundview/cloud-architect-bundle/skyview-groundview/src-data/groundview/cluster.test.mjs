import test from 'node:test';
import assert from 'node:assert/strict';

import { clusterPasses } from './cluster.mjs';
import { canonicalSensorIdentity } from './canonical.mjs';
import { DEFAULT_CLUSTER_WINDOW_SECONDS } from './constants.mjs';
import { deriveClockCorrection } from './clock.mjs';
import { describeMatch, passAnchor } from './presentation.mjs';

function obs(partial) {
  return {
    observation_id: partial.observation_id,
    receiver_id: partial.receiver_id || 'GV-RX-01',
    receiver_timestamp: partial.receiver_timestamp,
    canonical_sensor_identity: partial.canonical_sensor_identity
      || canonicalSensorIdentity(partial),
    rtl433_protocol: partial.rtl433_protocol || partial.protocol,
    model: partial.model,
    sensor_id: partial.sensor_id || partial.id,
  };
}

test('default cluster window is 30s and splits on gap greater than the window', () => {
  assert.equal(DEFAULT_CLUSTER_WINDOW_SECONDS, 30);
  const passes = clusterPasses([
    obs({ observation_id: '1', receiver_timestamp: '2026-09-15T10:00:00Z', protocol: '241', model: 'TST-507', id: 'A' }),
    obs({ observation_id: '2', receiver_timestamp: '2026-09-15T10:00:20Z', protocol: '241', model: 'TST-507', id: 'B' }),
    obs({ observation_id: '3', receiver_timestamp: '2026-09-15T10:00:51Z', protocol: '241', model: 'TST-507', id: 'C' }),
  ]);
  assert.equal(passes.length, 2);
  assert.deepEqual(passes[0].sensor_identities, ['241:TST-507:A', '241:TST-507:B']);
  assert.deepEqual(passes[1].sensor_identities, ['241:TST-507:C']);
});

test('equal timestamps use observation_id as the secondary key', () => {
  const stamp = '2026-09-15T10:00:00.000Z';
  const passes = clusterPasses([
    obs({ observation_id: 'z', receiver_timestamp: stamp, protocol: '241', model: 'TST-507', id: 'Z' }),
    obs({ observation_id: 'a', receiver_timestamp: stamp, protocol: '241', model: 'TST-507', id: 'A' }),
  ]);
  assert.equal(passes.length, 1);
  assert.deepEqual(passes[0].observation_ids, ['a', 'z']);
});

test('duplicate packets stay observed but fingerprint identities are unique', () => {
  const passes = clusterPasses([
    obs({ observation_id: '1', receiver_timestamp: '2026-09-15T10:00:00Z', protocol: '241', model: 'TST-507', id: 'A' }),
    obs({ observation_id: '2', receiver_timestamp: '2026-09-15T10:00:01Z', protocol: '241', model: 'TST-507', id: 'A' }),
  ]);
  assert.equal(passes[0].observation_count, 2);
  assert.deepEqual(passes[0].sensor_identities, ['241:TST-507:A']);
});

test('raw IDs in another namespace do not canonical-match', () => {
  assert.equal(
    canonicalSensorIdentity({ protocol: '241', model: 'TST-507', id: 'A' }),
    '241:TST-507:A',
  );
  assert.notEqual(
    canonicalSensorIdentity({ protocol: '241', model: 'TST-507', id: 'A' }),
    canonicalSensorIdentity({ protocol: '999', model: 'OTHER', id: 'A' }),
  );
});

test('clock correction is DERIVED and leaves receiver time on the observation', () => {
  const observation = { observation_id: 'o1', receiver_timestamp: '2026-09-15T10:00:00.000Z' };
  const derived = deriveClockCorrection(observation, 1.5);
  assert.equal(derived.provenance, 'DERIVED');
  assert.equal(observation.receiver_timestamp, '2026-09-15T10:00:00.000Z');
  assert.equal(derived.corrected_timestamp, '2026-09-15T10:00:01.500Z');
});

test('pass anchors are receiver coverage, never a vehicle coordinate', () => {
  assert.deepEqual(passAnchor({ latitude: 39.1, longitude: -94.5 }), {
    latitude: 39.1,
    longitude: -94.5,
    kind: 'receiver_coverage',
  });
  const described = describeMatch({
    provenance: 'INFERRED',
    confidence_label: 'very_strong',
    confidence_score: 89.29,
  });
  assert.equal(described.not_confirmed, true);
  assert.equal(described.provenance, 'INFERRED');
});

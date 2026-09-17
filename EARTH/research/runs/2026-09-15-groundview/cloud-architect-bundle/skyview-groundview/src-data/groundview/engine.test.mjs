import test from 'node:test';
import assert from 'node:assert/strict';

import { createGroundViewEngine } from '../../../server/providers/groundview/engine.js';
import { createGroundViewStore } from '../../../server/providers/groundview/store.js';
import { createGroundViewHttp } from '../../../server/providers/groundview/http.js';
import { replayCapture } from '../../../server/providers/groundview/rf/lab.js';
import { ingestFederatedEnvelope } from '../../../server/providers/groundview/federation/peer.js';
import { FORBIDDEN_LABEL, MATCHER_VERSION, PROVENANCE } from './constants.mjs';
import {
  LINKS,
  RECEIVERS,
  cameraFixture,
  syntheticNdjson,
} from '../../../fixtures/groundview/synthetic.mjs';

function engine() {
  return createGroundViewEngine({ store: createGroundViewStore({ persist: false }) });
}

async function loaded(shuffle = false) {
  const gv = engine();
  await gv.setReceivers(RECEIVERS);
  await gv.setLinks(LINKS);
  await gv.ingestNdjson(syntheticNdjson(shuffle), { adapter: 'rtl433' });
  return gv.replay();
}

function fakeReq(method, url, body) {
  const payload = body == null ? '' : JSON.stringify(body);
  return {
    method,
    url,
    async *[Symbol.asyncIterator]() {
      if (payload) yield Buffer.from(payload);
    },
  };
}

function fakeRes() {
  return {
    statusCode: 200,
    headers: {},
    body: '',
    setHeader(key, value) { this.headers[key] = value; },
    end(chunk) { this.body = chunk; },
  };
}

test('fixture replay is idempotent and order-independent', async () => {
  const first = await loaded(true);
  const again = engine();
  await again.setReceivers(RECEIVERS);
  await again.setLinks(LINKS);
  await again.ingestNdjson(syntheticNdjson(true), { adapter: 'rtl433' });
  await again.ingestNdjson(syntheticNdjson(true), { adapter: 'rtl433' });
  const second = await again.replay();
  assert.equal(first.observations.length, second.observations.length);
  assert.deepEqual(first.passes.map((row) => row.pass_id), second.passes.map((row) => row.pass_id));
  assert.deepEqual(first.matches.map((row) => row.match_id), second.matches.map((row) => row.match_id));
});

test('canonical 7-vs-5 match is 89.29 and never confirmed', async () => {
  const view = await loaded();
  const hit = view.matches.find((row) => row.shared_count === 5 && row.a_count === 7 && row.b_count === 5);
  assert.ok(hit, 'expected 7-vs-5 subset match');
  assert.equal(Number(hit.confidence_score.toFixed(2)), 89.29);
  assert.equal(hit.matcher_version, MATCHER_VERSION);
  assert.equal(hit.provenance, PROVENANCE.INFERRED);
  assert.notEqual(hit.confidence_label, FORBIDDEN_LABEL);
  assert.ok(!JSON.stringify(view.matches).includes('confirmed'));
});

test('one-id coincidence, two-id match, travel-window miss, and namespace collision', async () => {
  const view = await loaded();
  const one = view.matches.find((row) => row.shared_count === 1 && row.travel_time_feasible && row.b_count === 4);
  assert.ok(one);
  assert.ok(one.confidence_score <= 19);

  const two = view.matches.find((row) => row.shared_count === 2 && row.travel_time_feasible && row.b_count === 3);
  assert.ok(two);
  assert.ok(two.confidence_score <= 49);

  const miss = view.matches.find((row) => row.travel_time_feasible === false && row.shared_count >= 1);
  assert.ok(miss);
  assert.equal(miss.confidence_score, 0);

  const otherNs = view.observations.filter((row) => row.canonical_sensor_identity === '999:OTHER:A');
  const tpmsA = view.observations.filter((row) => row.canonical_sensor_identity === '241:TST-507:A');
  assert.equal(otherNs.length, 1);
  assert.ok(tpmsA.length >= 1);
  const colliding = view.matches.filter((row) => row.shared_sensor_identities?.includes('999:OTHER:A')
    && row.shared_sensor_identities?.includes('241:TST-507:A'));
  assert.equal(colliding.length, 0);
});

test('unknown protocol remains observed and does not invent identity', async () => {
  const view = await loaded();
  const unknown = view.observations.filter((row) => row.unknown_protocol);
  assert.ok(unknown.length >= 1);
  assert.equal(unknown[0].canonical_sensor_identity, null);
  assert.equal(unknown[0].provenance, PROVENANCE.OBSERVED);
  assert.equal(view.health.decoder_failure, true);
});

test('tracks chain A to B to C, mark forks, and never mint a vehicle id', async () => {
  const view = await loaded();
  const chained = view.tracks.filter((row) => row.pass_ids.length >= 3);
  assert.ok(chained.length >= 1);
  assert.ok(view.tracks.some((row) => row.fork));
  assert.ok(view.tracks.every((row) => row.provenance === PROVENANCE.INFERRED));
  assert.ok(view.tracks.every((row) => !row.vehicle_id && !row.permanent_id));
});

test('camera OCR binding is optional and inferred; RF still matches without it', async () => {
  const gv = engine();
  await gv.setReceivers(RECEIVERS);
  await gv.setLinks(LINKS);
  await gv.ingestNdjson(syntheticNdjson(), { adapter: 'rtl433' });
  const rfOnly = await gv.replay();
  assert.ok(rfOnly.matches.length > 0);
  await gv.setCameras([{ camera_id: 'GV-CAM-01', receiver_id: 'GV-RX-01' }]);
  const cam = cameraFixture()[0];
  await gv.ingestCamera(cam);
  const identity = await gv.ingestVisualIdentity({
    camera_observation_id: cam.camera_observation_id,
    raw_text: 'ABC1234',
    recognizer_version: 'groundview_ocr_fixture_v1',
    confidence: 0.4,
  });
  assert.equal(identity.provenance, PROVENANCE.INFERRED);
  assert.equal(identity.raw_text, 'ABC1234');
  const bound = await gv.bindCameraToPass({
    camera_observation_id: cam.camera_observation_id,
    receiver_id: 'GV-RX-01',
    observed_at: cam.observed_at,
  });
  assert.equal(bound.provenance, PROVENANCE.INFERRED);
  await gv.deleteBindings();
  const after = await gv.snapshot();
  assert.equal(after.bindings.length, 0);
  assert.ok(after.matches.length > 0);
});

test('receiver-node, custom decoder, federation, lab, experiment, playback, calibrate', async () => {
  const gv = engine();
  await gv.setReceivers(RECEIVERS);
  await gv.setLinks(LINKS);
  const node = await gv.ingestSourceEvent({
    source_event_id: 'node-1',
    receiver_id: 'GV-RX-01',
    receiver_timestamp: '2026-09-15T10:02:14.000Z',
    payload: { protocol: '241', model: 'TST-507', id: 'N1' },
  }, { adapter: 'receiver_node' });
  assert.equal(node.source_type, 'receiver_node');
  const custom = await gv.ingestSourceEvent({
    source_event_id: 'dec-1',
    receiver_id: 'GV-RX-01',
    receiver_timestamp: '2026-09-15T10:02:15.000Z',
    decoder_name: 'custom',
    decoder_version: 'lab-1',
    capture_ref: 'cap-1',
    payload: { protocol: '241', model: 'TST-507', id: 'N2' },
  }, { adapter: 'custom_decoder' });
  assert.equal(custom.source_type, 'custom_decoder');
  assert.equal(custom.capture_ref, 'cap-1');
  const federated = ingestFederatedEnvelope({
    source_event_id: 'fed-1',
    receiver_id: 'GV-RX-02',
    receiver_timestamp: '2026-09-15T10:07:01.000Z',
    payload: { protocol: '241', model: 'TST-507', id: 'N1' },
  });
  assert.equal(federated.source_type, 'receiver_node');
  await gv.ingestSourceEvent({
    source_event_id: 'fed-1',
    receiver_id: 'GV-RX-02',
    receiver_timestamp: '2026-09-15T10:07:01.000Z',
    payload: { protocol: '241', model: 'TST-507', id: 'N1' },
  }, { adapter: 'receiver_node' });
  await replayCapture(gv, {
    ndjson: '',
    decoder_name: 'rtl_433',
    decoder_version: 'fixture',
    capture_ref: 'lab-empty',
  });
  const view = await gv.replay();
  const experiment = await gv.runExperiment('lab-run');
  assert.ok(experiment.metrics.packets >= 2);
  const asOf = await gv.playback('2026-09-15T10:02:14.500Z');
  assert.ok(asOf.playback_at);
  assert.ok(asOf.observations.length <= view.observations.length);
  const labels = view.matches.slice(0, 2).map((match, index) => ({
    pass_a_id: match.pass_a_id,
    pass_b_id: match.pass_b_id,
    positive: index === 0,
    threshold: 50,
  }));
  const cal = await gv.calibrate(labels);
  assert.equal(cal.matcher_version, MATCHER_VERSION);
  assert.ok('precision' in cal);
  const rebuilt = await gv.rebuildFromHistorical();
  assert.equal(rebuilt.matches.length, view.matches.length);
});

test('HTTP snapshot, replay, health, and vercel node ingest', async () => {
  const gv = engine();
  const http = createGroundViewHttp(gv);
  const replayRes = fakeRes();
  await http(fakeReq('POST', '/replay', {
    receivers: RECEIVERS,
    links: LINKS,
    ndjson: syntheticNdjson(),
  }), replayRes);
  assert.equal(replayRes.statusCode, 200);
  const replayed = JSON.parse(replayRes.body);
  assert.ok(replayed.matches.length > 0);

  const snap = fakeRes();
  await http(fakeReq('GET', '/snapshot'), snap);
  assert.equal(JSON.parse(snap.body).passes.length, replayed.passes.length);

  const health = fakeRes();
  await http(fakeReq('GET', '/health'), health);
  assert.equal(JSON.parse(health.body).health.decoder_failure, true);

  const previous = process.env.VERCEL;
  process.env.VERCEL = '1';
  const node = fakeRes();
  await http(fakeReq('POST', '/node/events', {
    source_event_id: 'blocked',
    receiver_id: 'GV-RX-01',
    receiver_timestamp: '2026-09-15T10:02:14.000Z',
    payload: { protocol: '241', model: 'TST-507', id: 'Z' },
  }), node);
  if (previous == null) delete process.env.VERCEL;
  else process.env.VERCEL = previous;
  assert.equal(node.statusCode, 503);
});

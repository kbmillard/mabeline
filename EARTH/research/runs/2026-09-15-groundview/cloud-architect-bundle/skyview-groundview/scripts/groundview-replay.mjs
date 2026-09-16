#!/usr/bin/env node
import { createGroundViewEngine } from '../server/providers/groundview/engine.js';
import { createGroundViewStore } from '../server/providers/groundview/store.js';
import { RECEIVERS, LINKS, syntheticNdjson } from '../fixtures/groundview/synthetic.mjs';

const persist = process.argv.includes('--persist');
const engine = createGroundViewEngine({
  store: persist ? undefined : createGroundViewStore({ persist: false }),
});
await engine.setReceivers(RECEIVERS);
await engine.setLinks(LINKS);
const ingest = await engine.ingestNdjson(syntheticNdjson(process.argv.includes('--shuffle')), {
  adapter: 'rtl433',
  source_type: 'rtl433_recorded',
});
const view = await engine.replay();
const canonical = view.matches.find((row) => row.shared_count === 5 && row.a_count === 7 && row.b_count === 5);
console.log(JSON.stringify({
  packets: ingest.accepted.length,
  rejected: ingest.rejected.length,
  passes: view.passes.length,
  matches: view.matches.length,
  tracks: view.tracks.length,
  canonical_89_29: canonical ? Number(canonical.confidence_score.toFixed(2)) : null,
  health: view.health,
}, null, 2));

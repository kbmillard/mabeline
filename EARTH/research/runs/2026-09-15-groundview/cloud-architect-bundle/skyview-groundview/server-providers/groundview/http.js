import { createGroundViewEngine } from './engine.js';
import { GroundViewError } from './normalize.js';

function send(res, status, body) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(body));
}

function requestUrl(req) {
  let path = String(req.url || '/');
  const prefix = '/api/groundview';
  if (path === prefix || path.startsWith(`${prefix}/`) || path.startsWith(`${prefix}?`)) {
    path = path.slice(prefix.length) || '/';
  }
  if (!path.startsWith('/')) path = `/${path}`;
  return new URL(path, 'http://groundview.local');
}

async function readJson(req) {
  if (req.body && typeof req.body === 'object' && !Buffer.isBuffer(req.body)) return req.body;
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8');
  if (!raw) return {};
  return JSON.parse(raw);
}

export function createGroundViewHttp(engine = createGroundViewEngine()) {
  return async function groundviewHttp(req, res) {
    try {
      const url = requestUrl(req);
      const route = url.pathname.replace(/\/+$/, '') || '/';
      const method = req.method || 'GET';
      if (method === 'GET' && route === '/receivers') return send(res, 200, { receivers: (await engine.snapshot()).receivers });
      if (method === 'POST' && route === '/receivers') {
        const body = await readJson(req);
        await engine.setReceivers(body.receivers || body);
        return send(res, 200, { ok: true });
      }
      if (method === 'GET' && route === '/observations') return send(res, 200, { observations: (await engine.snapshot()).observations });
      if (method === 'GET' && route === '/passes') return send(res, 200, { passes: (await engine.snapshot()).passes });
      if (method === 'GET' && route === '/fingerprints') return send(res, 200, { fingerprints: (await engine.snapshot()).fingerprints });
      if (method === 'GET' && route === '/matches') return send(res, 200, { matches: (await engine.snapshot()).matches });
      if (method === 'GET' && route === '/tracks') return send(res, 200, { tracks: (await engine.snapshot()).tracks });
      if (method === 'GET' && route === '/cameras') return send(res, 200, { cameras: (await engine.snapshot()).cameras });
      if (method === 'GET' && route === '/camera-observations') return send(res, 200, { camera_observations: (await engine.snapshot()).camera_observations });
      if (method === 'GET' && route === '/visual-identities') return send(res, 200, { visual_identities: (await engine.snapshot()).visual_identities });
      if (method === 'GET' && route === '/bindings') return send(res, 200, { bindings: (await engine.snapshot()).bindings });
      if (method === 'GET' && route === '/experiments') return send(res, 200, { experiments: (await engine.snapshot()).experiments });
      if (method === 'GET' && route === '/health') return send(res, 200, { health: (await engine.snapshot()).health });
      if (method === 'GET' && route === '/snapshot') {
        const asOf = url.searchParams.get('at');
        const view = asOf ? await engine.playback(asOf) : await engine.snapshot();
        return send(res, 200, view);
      }
      if (method === 'GET' && route === '/playback') {
        return send(res, 200, await engine.playback(url.searchParams.get('at')));
      }
      if (method === 'POST' && route === '/replay') {
        const body = await readJson(req);
        if (body.fixture === 'synthetic' || body.seed) {
          const seeded = await engine.seedSynthetic({ force: true });
          if (!body.ndjson && !body.events) {
            return send(res, 200, seeded.view || await engine.snapshot());
          }
        }
        if (body.receivers) await engine.setReceivers(body.receivers);
        if (body.links) await engine.setLinks(body.links);
        if (body.cameras) await engine.setCameras(body.cameras);
        if (body.ndjson) await engine.ingestNdjson(body.ndjson, body.defaults || { adapter: 'rtl433' });
        if (body.events) {
          for (const event of body.events) await engine.ingestSourceEvent(event, body.defaults || {});
        }
        const view = await engine.replay({ clustering: body.clustering || {} });
        return send(res, 200, view);
      }
      if (method === 'POST' && route === '/node/events') {
        if (process.env.VERCEL) {
          return send(res, 503, { error: 'GroundView node ingest requires a persistent host' });
        }
        const body = await readJson(req);
        const observation = await engine.ingestSourceEvent(body, { adapter: 'receiver_node' });
        return send(res, 200, { observation });
      }
      if (method === 'POST' && route === '/node/heartbeat') {
        const body = await readJson(req);
        await engine.recordHeartbeat(body);
        return send(res, 200, { ok: true });
      }
      if (method === 'POST' && route === '/experiments/replay') {
        const body = await readJson(req);
        const record = await engine.runExperiment(body.name || 'unnamed', body);
        return send(res, 200, record);
      }
      if (method === 'GET' && route.startsWith('/experiments/') && route.endsWith('/report')) {
        const view = await engine.snapshot();
        return send(res, 200, { experiments: view.experiments, csv: toCsv(view) });
      }
      if (method === 'POST' && route === '/camera-observations') {
        const body = await readJson(req);
        return send(res, 200, { observation: await engine.ingestCamera(body) });
      }
      if (method === 'POST' && route === '/visual-identities') {
        const body = await readJson(req);
        return send(res, 200, { identity: await engine.ingestVisualIdentity(body) });
      }
      if (method === 'POST' && route === '/bindings') {
        const body = await readJson(req);
        return send(res, 200, { binding: await engine.bindCameraToPass(body) });
      }
      send(res, 404, { error: 'unknown GroundView route' });
    } catch (error) {
      const status = error instanceof SyntaxError ? 400 : (error?.name === 'GroundViewError' ? 400 : 500);
      send(res, status, {
        error: error.message,
        code: error.code || (error instanceof GroundViewError ? error.code : 'GROUNDVIEW_STORAGE_ERROR'),
      });
    }
  };
}

function toCsv(view) {
  const rows = [['match_id', 'shared_count', 'confidence_score', 'confidence_label']];
  for (const match of view.matches || []) {
    rows.push([match.match_id, match.shared_count, match.confidence_score, match.confidence_label]);
  }
  return rows.map((row) => row.join(',')).join('\n');
}

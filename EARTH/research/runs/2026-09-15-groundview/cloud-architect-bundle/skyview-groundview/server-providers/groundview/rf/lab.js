import { MATCHER_VERSION, CLUSTER_VERSION } from '../../../../src/data/groundview/constants.mjs';

/** Decoder/capture lab uses the same ingest path; capture_ref is provenance only. */
export async function replayCapture(engine, {
  ndjson,
  decoder_name,
  decoder_version,
  capture_ref,
  clustering,
} = {}) {
  const ingest = await engine.ingestNdjson(ndjson, {
    adapter: 'rtl433',
    source_type: 'rtl433_recorded',
    decoder_name,
    decoder_version,
    capture_ref,
  });
  const view = await engine.replay({ clustering: clustering || {} });
  return {
    ingest,
    clustering_version: CLUSTER_VERSION,
    matcher_version: MATCHER_VERSION,
    snapshot: view,
    empirical: 'FIELD_VALIDATION_REQUIRED',
  };
}

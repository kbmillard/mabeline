export function healthFromSnapshot(snapshot = {}) {
  return snapshot.health || {
    receiver_loss: false,
    clock_error: false,
    decoder_failure: false,
    ingest_failure: false,
    cluster_failure: false,
    matcher_ambiguity: false,
  };
}

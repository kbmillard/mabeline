import { createHash } from 'node:crypto';
import {
  CANONICAL_VERSION,
  CLUSTER_VERSION,
  EVENT_SCHEMA_VERSION,
  MATCHER_VERSION,
  TRACK_VERSION,
} from '../../../src/data/groundview/constants.mjs';

export function sha32(value) {
  return createHash('sha256').update(String(value)).digest('hex').slice(0, 32);
}

export function observationId({ receiverId, sourceEventId }) {
  return sha32(JSON.stringify({
    schema: EVENT_SCHEMA_VERSION,
    receiver_id: receiverId,
    source_event_id: sourceEventId,
  }));
}

export function identityProjectionId({ observationId: id, snapshotId }) {
  return sha32(JSON.stringify({
    observation_id: id,
    canonicalization_version: CANONICAL_VERSION,
    snapshot: snapshotId,
  }));
}

export function passId({ receiverId, observationIds, snapshotId }) {
  return sha32(JSON.stringify({
    receiver_id: receiverId,
    observation_ids: [...observationIds].sort(),
    clustering_version: CLUSTER_VERSION,
    snapshot: snapshotId,
  }));
}

export function fingerprintId({ passId: id, identities }) {
  return sha32(JSON.stringify({
    pass_id: id,
    identities: [...identities].sort(),
    canonicalization_version: CANONICAL_VERSION,
  }));
}

export function matchId({ passAId, passBId }) {
  return sha32(JSON.stringify({
    pass_a_id: passAId,
    pass_b_id: passBId,
    matcher_version: MATCHER_VERSION,
  }));
}

export function trackId({ passIds }) {
  return sha32(JSON.stringify({
    pass_ids: passIds,
    track_builder_version: TRACK_VERSION,
  }));
}

export function snapshotId(kind, config) {
  return sha32(JSON.stringify({ kind, config }));
}

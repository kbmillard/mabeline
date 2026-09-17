export const EVENT_SCHEMA_VERSION = 'groundview_event_v1';
export const CANONICAL_VERSION = 'groundview_canonical_v1';
export const CLUSTER_VERSION = 'groundview_cluster_v1';
export const MATCHER_VERSION = 'groundview_match_v1';
export const TRACK_VERSION = 'groundview_track_v1';
export const BINDING_VERSION = 'groundview_bind_v1';
export const CLOCK_VERSION = 'groundview_clock_v1';

export const DEFAULT_CLUSTER_WINDOW_SECONDS = 30;

export const BASE_SCORE_WEIGHTS = Object.freeze({
  overlap_coefficient: 0.5,
  shared_count_strength: 0.3,
  jaccard: 0.2,
});

export const OVERLAP_CAPS = Object.freeze({
  0: 0,
  1: 19,
  2: 49,
  3: 69,
  4: 84,
});

export const COMPETITION_FACTORS = Object.freeze({
  none: 1,
  margin_gte_25: 1,
  margin_15: 0.95,
  margin_8: 0.85,
  margin_3: 0.7,
  margin_lt_3: 0.5,
});

export const CONFIDENCE = Object.freeze({
  weak: [0, 25],
  possible: [25, 50],
  strong: [50, 75],
  very_strong: [75, 100],
});

export const FORBIDDEN_LABEL = 'confirmed';

export const PROVENANCE = Object.freeze({
  OBSERVED: 'OBSERVED',
  DERIVED: 'DERIVED',
  INFERRED: 'INFERRED',
});

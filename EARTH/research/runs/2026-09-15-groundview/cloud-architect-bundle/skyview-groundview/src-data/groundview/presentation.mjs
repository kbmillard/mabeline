export const DEFAULT_PRESENTATION = Object.freeze({
  showReceivers: true,
  showPasses: true,
  showMatches: true,
  showTracks: true,
});

export function normalizePresentation(input = {}) {
  return {
    showReceivers: input.showReceivers !== false,
    showPasses: input.showPasses !== false,
    showMatches: input.showMatches !== false,
    showTracks: input.showTracks !== false,
  };
}

export function describeMatch(match = {}) {
  return {
    provenance: match.provenance || 'INFERRED',
    match_id: match.match_id,
    confidence_score: match.confidence_score,
    confidence_label: match.confidence_label,
    shared_count: match.shared_count,
    overlap_coefficient: match.score_components?.overlap_coefficient ?? match.overlap_coefficient,
    shared_count_strength: match.score_components?.shared_count_strength ?? match.shared_count_strength,
    jaccard: match.jaccard_similarity ?? match.jaccard,
    competition_factor: match.competition_factor,
    score_margin: match.score_margin,
    competing_candidate_count: match.competing_candidate_count,
    travel_time_feasible: match.travel_time_feasible,
    direction_feasible: match.direction_feasible,
    elapsed_seconds: match.elapsed_seconds,
    matcher_version: match.matcher_version,
    not_confirmed: true,
  };
}

/** A pass is drawn at the receiver coverage site, never as a vehicle coordinate. */
export function passAnchor(receiver) {
  if (!receiver) return null;
  const latitude = Number(receiver.latitude);
  const longitude = Number(receiver.longitude);
  if (![latitude, longitude].every(Number.isFinite)) return null;
  return { latitude, longitude, kind: 'receiver_coverage' };
}

import {
  BASE_SCORE_WEIGHTS,
  COMPETITION_FACTORS,
  MATCHER_VERSION,
  OVERLAP_CAPS,
} from './constants.mjs';

export { MATCHER_VERSION };

export function overlapCap(sharedCount) {
  const n = Number(sharedCount);
  if (!Number.isFinite(n) || n <= 0) return 0;
  if (n >= 5) return 100;
  return OVERLAP_CAPS[n] ?? 0;
}

export function setStatistics(setA = [], setB = []) {
  const a = new Set([...setA].map(String).filter(Boolean));
  const b = new Set([...setB].map(String).filter(Boolean));
  const shared = [...a].filter((id) => b.has(id)).sort();
  const union = [...new Set([...a, ...b])].sort();
  const sharedCount = shared.length;
  const aCount = a.size;
  const bCount = b.size;
  const unionCount = union.length;
  const minCount = Math.min(aCount, bCount);
  return {
    shared_sensor_identities: shared,
    shared_count: sharedCount,
    a_count: aCount,
    b_count: bCount,
    union_count: unionCount,
    jaccard: unionCount > 0 ? sharedCount / unionCount : 0,
    overlap_coefficient: minCount > 0 ? sharedCount / minCount : 0,
    containment_a: aCount > 0 ? sharedCount / aCount : 0,
    containment_b: bCount > 0 ? sharedCount / bCount : 0,
    shared_count_strength: Math.min(sharedCount / 6, 1),
  };
}

export function baseScore(stats) {
  const overlap = Number(stats.overlap_coefficient) || 0;
  const strength = Number(stats.shared_count_strength) || 0;
  const jaccard = Number(stats.jaccard) || 0;
  return 100 * (
    BASE_SCORE_WEIGHTS.overlap_coefficient * overlap
    + BASE_SCORE_WEIGHTS.shared_count_strength * strength
    + BASE_SCORE_WEIGHTS.jaccard * jaccard
  );
}

export function travelTimeFeasible(elapsedSeconds, link) {
  if (!link) return false;
  const elapsed = Number(elapsedSeconds);
  const min = Number(link.minimum_travel_seconds);
  const max = Number(link.maximum_travel_seconds);
  if (![elapsed, min, max].every(Number.isFinite)) return false;
  return elapsed >= min && elapsed <= max;
}

export function directionFeasible(passA, passB, link) {
  if (!link || link.direction == null || link.direction === '') return true;
  return passA?.receiver_id === link.from_receiver_id
    && passB?.receiver_id === link.to_receiver_id;
}

export function competitionFactor(scoreMargin, hasCompetitor) {
  if (!hasCompetitor) return COMPETITION_FACTORS.none;
  const margin = Number(scoreMargin);
  if (!Number.isFinite(margin)) return COMPETITION_FACTORS.margin_lt_3;
  if (margin >= 25) return COMPETITION_FACTORS.margin_gte_25;
  if (margin >= 15) return COMPETITION_FACTORS.margin_15;
  if (margin >= 8) return COMPETITION_FACTORS.margin_8;
  if (margin >= 3) return COMPETITION_FACTORS.margin_3;
  return COMPETITION_FACTORS.margin_lt_3;
}

export function confidenceLabel(finalScore) {
  const score = Number(finalScore);
  if (!Number.isFinite(score) || score < 25) return 'weak';
  if (score < 50) return 'possible';
  if (score < 75) return 'strong';
  return 'very_strong';
}

export function clampScore(value) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < 0) return 0;
  if (n > 100) return 100;
  return n;
}

/**
 * Score one candidate after hard gates. Competition is applied later.
 */
export function scoreUngatedCandidate(setA, setB) {
  const stats = setStatistics(setA, setB);
  const rawBase = baseScore(stats);
  const cap = overlapCap(stats.shared_count);
  const capped = Math.min(rawBase, cap);
  return { stats, base_score: rawBase, absolute_overlap_cap: cap, capped_score: capped };
}

export function applyHardGates({ stats, elapsedSeconds, passA, passB, link }) {
  const travel = travelTimeFeasible(elapsedSeconds, link);
  const direction = directionFeasible(passA, passB, link);
  const sharedOk = (stats.shared_count || 0) >= 1;
  return {
    travel_time_feasible: travel,
    direction_feasible: direction,
    shared_ok: sharedOk,
    zero: !travel || !direction || !sharedOk,
  };
}

export function isFeasibleCompetitor(candidate) {
  return candidate
    && candidate.travel_time_feasible === true
    && candidate.direction_feasible === true
    && Number(candidate.shared_count) >= 1
    && Number(candidate.capped_score) > 0;
}

/**
 * Apply competition among candidates that share upstream pass + downstream receiver.
 * Invalid-time/direction candidates cannot penalize.
 */
export function applyCompetition(candidates = []) {
  const keyed = new Map();
  candidates.forEach((candidate, insertionIndex) => {
    const key = `${candidate.pass_a_id}::${candidate.receiver_b_id}`;
    if (!keyed.has(key)) keyed.set(key, []);
    keyed.get(key).push({ candidate, insertionIndex });
  });
  const out = [];
  for (const group of keyed.values()) {
    const feasible = group
      .filter((row) => isFeasibleCompetitor(row.candidate))
      .map((row) => row.candidate);
    for (const { candidate, insertionIndex } of group) {
      const others = feasible.filter((row) => row !== candidate);
      const hasCompetitor = others.length > 0;
      const bestCompeting = hasCompetitor
        ? Math.max(...others.map((row) => Number(row.capped_score) || 0))
        : 0;
      const margin = (Number(candidate.capped_score) || 0) - bestCompeting;
      const factor = competitionFactor(margin, hasCompetitor);
      const finalScore = clampScore((Number(candidate.capped_score) || 0) * factor);
      out.push({
        ...candidate,
        competing_candidate_count: others.length,
        best_competing_score: hasCompetitor ? bestCompeting : null,
        score_margin: hasCompetitor ? margin : null,
        competition_factor: factor,
        confidence_score: finalScore,
        confidence_label: confidenceLabel(finalScore),
        matcher_version: MATCHER_VERSION,
        insertion_index: insertionIndex,
      });
    }
  }
  return out.sort(compareCandidates);
}

export function compareCandidates(a, b) {
  const score = (Number(b.confidence_score) || 0) - (Number(a.confidence_score) || 0);
  if (score !== 0) return score;
  const shared = (Number(b.shared_count) || 0) - (Number(a.shared_count) || 0);
  if (shared !== 0) return shared;
  const inserted = (Number(a.insertion_index) || 0) - (Number(b.insertion_index) || 0);
  if (inserted !== 0) return inserted;
  return String(a.match_id || '').localeCompare(String(b.match_id || ''));
}

export function elapsedSeconds(passA, passB) {
  const delta = Date.parse(passB?.start_time) - Date.parse(passA?.start_time);
  return Number.isFinite(delta) ? delta / 1000 : null;
}

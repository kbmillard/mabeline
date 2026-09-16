import test from 'node:test';
import assert from 'node:assert/strict';

import {
  applyCompetition,
  applyHardGates,
  baseScore,
  confidenceLabel,
  elapsedSeconds,
  overlapCap,
  scoreUngatedCandidate,
  setStatistics,
} from './match.mjs';
import { MATCHER_VERSION } from './constants.mjs';

const SEVEN = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
const FIVE = ['A', 'B', 'D', 'E', 'F'];

function candidate(partial = {}) {
  return {
    match_id: partial.match_id || 'm',
    pass_a_id: partial.pass_a_id || 'pass-a',
    pass_b_id: partial.pass_b_id || 'pass-b',
    receiver_b_id: partial.receiver_b_id || 'GV-RX-02',
    travel_time_feasible: partial.travel_time_feasible ?? true,
    direction_feasible: partial.direction_feasible ?? true,
    shared_count: partial.shared_count ?? 3,
    capped_score: partial.capped_score ?? 60,
    ...partial,
  };
}

test('canonical 7-vs-5 subset scores 89.29 before competition', () => {
  const scored = scoreUngatedCandidate(SEVEN, FIVE);
  assert.equal(scored.stats.shared_count, 5);
  assert.equal(scored.stats.overlap_coefficient, 1);
  assert.equal(scored.stats.shared_count_strength, 5 / 6);
  assert.equal(scored.stats.jaccard, 5 / 7);
  assert.equal(scored.absolute_overlap_cap, 100);
  const expected = 100 * (0.5 * 1 + 0.3 * (5 / 6) + 0.2 * (5 / 7));
  assert.equal(scored.base_score, expected);
  assert.equal(Number(expected.toFixed(2)), 89.29);
  assert.equal(scored.capped_score, expected);
});

test('overlap caps are 19/49/69/84/100', () => {
  assert.equal(overlapCap(1), 19);
  assert.equal(overlapCap(2), 49);
  assert.equal(overlapCap(3), 69);
  assert.equal(overlapCap(4), 84);
  assert.equal(overlapCap(5), 100);
  assert.equal(overlapCap(9), 100);
  assert.equal(overlapCap(0), 0);
});

test('confidence labels never include confirmed', () => {
  assert.equal(confidenceLabel(0), 'weak');
  assert.equal(confidenceLabel(24.9), 'weak');
  assert.equal(confidenceLabel(25), 'possible');
  assert.equal(confidenceLabel(49.9), 'possible');
  assert.equal(confidenceLabel(50), 'strong');
  assert.equal(confidenceLabel(74.9), 'strong');
  assert.equal(confidenceLabel(75), 'very_strong');
  assert.equal(confidenceLabel(100), 'very_strong');
  for (const score of [0, 19, 49, 69, 84, 89.29, 100]) {
    assert.notEqual(confidenceLabel(score), 'confirmed');
  }
});

test('elapsed time is start-to-start', () => {
  const seconds = elapsedSeconds(
    { start_time: '2026-09-15T10:02:14.000Z' },
    { start_time: '2026-09-15T10:07:01.000Z' },
  );
  assert.equal(seconds, 287);
});

test('hard gates zero invalid travel or direction', () => {
  const stats = setStatistics(SEVEN, FIVE);
  const miss = applyHardGates({
    stats,
    elapsedSeconds: 12,
    passA: { receiver_id: 'GV-RX-01' },
    passB: { receiver_id: 'GV-RX-02' },
    link: {
      from_receiver_id: 'GV-RX-01',
      to_receiver_id: 'GV-RX-02',
      minimum_travel_seconds: 60,
      maximum_travel_seconds: 600,
      direction: 'eastbound',
    },
  });
  assert.equal(miss.travel_time_feasible, false);
  assert.equal(miss.zero, true);
});

test('competition universe: near-tie, inferior, sharing only A, sharing only B, unrelated, exact tie, insertion, invalid cannot penalize', () => {
  const near = applyCompetition([
    candidate({ match_id: 'best', pass_b_id: 'b1', capped_score: 70, shared_count: 4 }),
    candidate({ match_id: 'near', pass_b_id: 'b2', capped_score: 68, shared_count: 4 }),
  ]);
  const bestNear = near.find((row) => row.match_id === 'best');
  assert.equal(bestNear.competing_candidate_count, 1);
  assert.ok(bestNear.score_margin < 3);
  assert.equal(bestNear.competition_factor, 0.5);
  assert.equal(bestNear.confidence_score, 35);

  const inferior = applyCompetition([
    candidate({ match_id: 'top', pass_b_id: 'b1', capped_score: 80, shared_count: 5 }),
    candidate({ match_id: 'low', pass_b_id: 'b2', capped_score: 40, shared_count: 2 }),
  ]);
  assert.equal(inferior.find((row) => row.match_id === 'top').competition_factor, 1);
  assert.equal(inferior.find((row) => row.match_id === 'top').confidence_score, 80);

  const sharingOnlyA = applyCompetition([
    candidate({ match_id: 'a1', pass_a_id: 'A', receiver_b_id: 'R2', pass_b_id: 'b1', capped_score: 80 }),
    candidate({ match_id: 'a2', pass_a_id: 'A', receiver_b_id: 'R3', pass_b_id: 'b9', capped_score: 79 }),
  ]);
  assert.equal(sharingOnlyA.find((row) => row.match_id === 'a1').competing_candidate_count, 0);
  assert.equal(sharingOnlyA.find((row) => row.match_id === 'a1').competition_factor, 1);

  const sharingOnlyB = applyCompetition([
    candidate({ match_id: 'p1', pass_a_id: 'A1', receiver_b_id: 'R2', capped_score: 80 }),
    candidate({ match_id: 'p2', pass_a_id: 'A2', receiver_b_id: 'R2', capped_score: 79 }),
  ]);
  assert.equal(sharingOnlyB.find((row) => row.match_id === 'p1').competing_candidate_count, 0);

  const unrelated = applyCompetition([
    candidate({ match_id: 'u1', pass_a_id: 'A1', receiver_b_id: 'R2', capped_score: 80 }),
    candidate({ match_id: 'u2', pass_a_id: 'A9', receiver_b_id: 'R9', capped_score: 80 }),
  ]);
  assert.equal(unrelated.find((row) => row.match_id === 'u1').competing_candidate_count, 0);

  const tied = applyCompetition([
    candidate({ match_id: 'first', pass_b_id: 'b1', capped_score: 60, shared_count: 3 }),
    candidate({ match_id: 'second', pass_b_id: 'b2', capped_score: 60, shared_count: 3 }),
  ]);
  assert.equal(tied[0].match_id, 'first');
  assert.equal(tied[1].match_id, 'second');
  assert.equal(tied[0].insertion_index, 0);

  const invalid = applyCompetition([
    candidate({
      match_id: 'valid',
      pass_b_id: 'b1',
      capped_score: 40,
      travel_time_feasible: true,
    }),
    candidate({
      match_id: 'invalid-time',
      pass_b_id: 'b2',
      capped_score: 90,
      travel_time_feasible: false,
    }),
    candidate({
      match_id: 'invalid-dir',
      pass_b_id: 'b3',
      capped_score: 90,
      direction_feasible: false,
    }),
  ]);
  const valid = invalid.find((row) => row.match_id === 'valid');
  assert.equal(valid.competing_candidate_count, 0);
  assert.equal(valid.competition_factor, 1);
  assert.equal(valid.confidence_score, 40);
});

test('matcher version is groundview_match_v1', () => {
  assert.equal(MATCHER_VERSION, 'groundview_match_v1');
  assert.equal(baseScore(setStatistics(['A'], ['A'])).toFixed(2), (100 * (0.5 * 1 + 0.3 * (1 / 6) + 0.2 * 1)).toFixed(2));
});

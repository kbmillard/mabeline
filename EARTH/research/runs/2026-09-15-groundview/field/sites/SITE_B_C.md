# SITE_B / SITE_C — corridor placeholders (P20 / P22)

**Status:** PLACEHOLDER until P19 PASS  
**Rule:** Do not invent dual-site or corridor continuity claims before Site A empirical session.

## Spacing / travel-window rules (planning)

1. Sites must share a **plausible commercial corridor** (same primary truck route or connected designated network).
2. Travel time between A→B (and B→C) must be estimable from posted speeds + route length; record link travel-window seconds for clock eligibility (`evaluateTimingEligibility`) — **do not widen matcher-v1** if clocks are bad.
3. Prefer similar RF geometry (height, antenna type) for comparability; if profiles differ, run `comparability.mjs` and mark INCOMPARABLE when required.
4. Independent synchronized truth capture required at **both** ends for P20 (manual counts / video timestamps) — never used to silently tune v1 mid-run.

## SITE_B (P20)

| Field | Value |
| --- | --- |
| site_id | SITE_B |
| receiver_id | GV-RX-FIELD-02 |
| corridor_from | SITE_A |
| approximate_spacing | 5–25 km typical planning band (operator measures actual) |
| lat/lon | TBD after P19 PASS + site walk |
| survey_status | FIELD_VALIDATION_REQUIRED |

## SITE_C (P22 third site)

| Field | Value |
| --- | --- |
| site_id | SITE_C |
| receiver_id | GV-RX-FIELD-03 |
| corridor_role | A→B→C continuity |
| lat/lon | TBD |
| survey_status | FIELD_VALIDATION_REQUIRED |

## Unlock path

```text
P19 PASS (Site A)
  → deploy Site B + comparability + dual truth  → P20 PASS
  → blinded labels / promotion governance       → P21 complete
  → Site C + episode continuity                 → P22 PASS
  → enable journey/envelope presentation        → P23
```
